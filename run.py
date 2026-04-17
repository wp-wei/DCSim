#!/usr/bin/env python3
"""Headless OpenModelica runner for MyDC.Examples.SingleRoomDX."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# ---- Configurable paths and runtime parameters ----
ROOT = Path(__file__).resolve().parent
MYDC_PACKAGE = ROOT / "MyDC" / "package.mo"
OUTPUT_DIR = ROOT / "results"
SIM_MODEL = "MyDC.Examples.SingleRoomDX"
SIM_START = 0
SIM_STOP = 21600
SIM_INTERVAL = 60

# Preferred env var is BUILDINGS_PATH, BUILDINGS_LIB is kept for compatibility.
BUILDINGS_PATH_ENV = "BUILDINGS_PATH"
BUILDINGS_LIB_ENV = "BUILDINGS_LIB"
OMLIBRARY_ENV = "OPENMODELICALIBRARY"


def fail(layer: str, message: str, code: int = 1) -> None:
    print(f"[ERROR] {layer}: {message}", file=sys.stderr)
    sys.exit(code)


def find_buildings_package() -> Path:
    """Find Buildings/package.mo via env variables or common local paths."""
    candidates: list[Path] = []

    if os.environ.get(BUILDINGS_PATH_ENV):
        candidates.append(Path(os.environ[BUILDINGS_PATH_ENV]).expanduser())

    if os.environ.get(BUILDINGS_LIB_ENV):
        candidates.append(Path(os.environ[BUILDINGS_LIB_ENV]).expanduser())

    oml = os.environ.get(OMLIBRARY_ENV, "")
    for entry in [p for p in oml.split(os.pathsep) if p.strip()]:
        pth = Path(entry).expanduser()
        candidates.append(pth / "Buildings")
        candidates.append(pth)

    candidates.extend(
        [
            ROOT / "Buildings",
            ROOT.parent / "Buildings",
            Path.home() / "Buildings",
            Path("/opt/Buildings"),
            Path("/usr/share/modelica/Buildings"),
        ]
    )

    for base in candidates:
        pkg = base / "package.mo" if base.name == "Buildings" else base / "Buildings" / "package.mo"
        if pkg.exists():
            return pkg.resolve()

    fail(
        "buildings-path",
        (
            "Could not find Buildings/package.mo. Set BUILDINGS_PATH (preferred) "
            "or BUILDINGS_LIB to the Buildings root directory."
        ),
    )


def main() -> None:
    try:
        from OMPython import OMCSessionZMQ
    except Exception as exc:  # noqa: BLE001
        fail("python-dependency", f"Failed to import OMPython: {exc}")

    if not MYDC_PACKAGE.exists():
        fail("modelica-package", f"Missing package file: {MYDC_PACKAGE}")

    buildings_package = find_buildings_package()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        omc = OMCSessionZMQ()
    except Exception as exc:  # noqa: BLE001
        fail("environment", f"Failed to start OpenModelica session (omc): {exc}")

    def send(expr: str, layer: str) -> object:
        try:
            result = omc.sendExpression(expr)
        except Exception as exc:  # noqa: BLE001
            fail(layer, f"OMC command failed: {expr} -> {exc}")
        if isinstance(result, str) and result.lower().startswith("error"):
            fail(layer, f"OMC returned error for `{expr}`: {result}")
        return result

    installation_dir = send("getInstallationDirectoryPath()", "environment")
    if not isinstance(installation_dir, str) or not installation_dir:
        fail("environment", f"Unexpected getInstallationDirectoryPath() response: {installation_dir}")

    buildings_root = buildings_package.parent
    omlib_dir = Path(installation_dir) / "lib" / "omlibrary"
    user_lib_dir = Path.home() / ".openmodelica" / "libraries"
    modelica_path = os.pathsep.join(
        [omlib_dir.as_posix(), buildings_root.as_posix(), user_lib_dir.as_posix()]
    )

    if send(f'setModelicaPath("{modelica_path}")', "environment") is not True:
        fail("environment", f"setModelicaPath failed for: {modelica_path}")

    print(f"[INFO] OpenModelica installation: {installation_dir}")
    print(f"[INFO] Modelica path: {send('getModelicaPath()', 'environment')}")

    print("[INFO] Checking standard Modelica library...")
    if send("loadModel(Modelica)", "modelica-stdlib") is not True:
        fail("modelica-stdlib", "loadModel(Modelica) returned False")

    print(f"[INFO] Loading Buildings from: {buildings_package}")
    if send(f'loadFile("{buildings_package.as_posix()}")', "buildings-load") is not True:
        fail("buildings-load", f"loadFile failed for {buildings_package}")

    print(f"[INFO] Loading MyDC from: {MYDC_PACKAGE}")
    if send(f'loadFile("{MYDC_PACKAGE.as_posix()}")', "mydc-load") is not True:
        fail("mydc-load", f"loadFile failed for {MYDC_PACKAGE}")

    if send(f"isModel({SIM_MODEL})", "mydc-load") is not True:
        fail("mydc-load", f"Model class not found: {SIM_MODEL}")

    sim_cmd = (
        f"simulate({SIM_MODEL}, startTime={SIM_START}, stopTime={SIM_STOP}, "
        f"numberOfIntervals={(SIM_STOP - SIM_START) // SIM_INTERVAL}, "
        f'outputFormat="mat", simflags="-emit_protected", '
        f'resultFile="{(OUTPUT_DIR / "SingleRoomDX_res").as_posix()}")'
    )

    print("[INFO] Running simulation...")
    sim_res = send(sim_cmd, "simulation-runtime")

    result_file = ""
    if isinstance(sim_res, dict):
        result_file = str(sim_res.get("resultFile", ""))
    elif isinstance(sim_res, str):
        m = re.search(r'resultFile\s*=\s*"([^"]+)"', sim_res)
        if m:
            result_file = m.group(1)

    if not result_file:
        fail("result-parsing", f"resultFile missing in simulate() response: {sim_res}")

    result_path = Path(result_file)
    if not result_path.exists():
        alt = OUTPUT_DIR / f"{result_file}.mat"
        if alt.exists():
            result_path = alt
        else:
            fail("result-parsing", f"Result file was reported but not found: {result_file}")

    print("[INFO] Simulation completed.")
    print(f"[INFO] Result file: {result_path.resolve()}")


if __name__ == "__main__":
    main()
