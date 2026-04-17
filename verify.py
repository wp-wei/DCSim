#!/usr/bin/env python3
"""Post-run verification for MyDC simulation outputs."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT_STEM = ROOT / "results" / "SingleRoomDX_res"
REQUIRED_VARS = ["TRoom", "QIT", "QCool"]


def fail(msg: str, code: int = 1) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(code)


def locate_result() -> Path:
    candidates = [RESULT_STEM, RESULT_STEM.with_suffix(".mat")]
    for path in candidates:
        if path.exists():
            return path
    fail(f"Result file not found. Expected one of: {[str(p) for p in candidates]}")


def parse_ompython_list(value: object) -> list[object]:
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                return parsed
        except Exception:  # noqa: BLE001
            pass
    fail(f"Unexpected OMPython list response: {value}")


def main() -> None:
    try:
        from OMPython import OMCSessionZMQ
    except Exception as exc:  # noqa: BLE001
        fail(f"Failed to import OMPython: {exc}")

    res_file = locate_result()
    print(f"[INFO] Using result file: {res_file}")

    try:
        omc = OMCSessionZMQ()
    except Exception as exc:  # noqa: BLE001
        fail(f"Failed to start OpenModelica session (omc): {exc}")

    vars_out = parse_ompython_list(
        omc.sendExpression(f'readSimulationResultVars("{res_file.as_posix()}")')
    )

    missing = [name for name in REQUIRED_VARS if name not in vars_out]
    if missing:
        fail(f"Required variables not found in result: {missing}")

    dat = omc.sendExpression(
        f'readSimulationResult("{res_file.as_posix()}", {{"time", "TRoom"}}, 0, -1)'
    )
    dat_list = parse_ompython_list(dat)
    if len(dat_list) != 2:
        fail(f"Unexpected response from readSimulationResult: {dat}")

    time_series = dat_list[0]
    temp_series = dat_list[1]

    if not isinstance(time_series, list) or not isinstance(temp_series, list):
        fail(f"Unexpected series types: time={type(time_series)}, TRoom={type(temp_series)}")

    if len(time_series) < 3 or len(temp_series) < 3:
        fail("Temperature series too short; simulation likely failed")

    tmin = min(temp_series)
    tmax = max(temp_series)
    dtr = tmax - tmin
    print(f"[INFO] TRoom range: min={tmin:.3f} K, max={tmax:.3f} K, delta={dtr:.3f} K")

    if dtr < 0.05:
        fail("TRoom appears almost constant (delta < 0.05 K)")

    print("[INFO] Verification passed.")


if __name__ == "__main__":
    main()
