# AGENTS.md

## Repository purpose

This repository contains a minimal, reproducible OpenModelica + Buildings prototype for an air-cooled data center simulation.
The current goal is not full physical fidelity. The first priority is a model that reliably loads, simulates, and produces interpretable temperature response from Python in a headless environment.

## Working style

- Prefer the smallest working change over a large speculative implementation.
- Verify every important assumption by inspecting the actual repository files and installed tools before relying on it.
- Do not assume a Modelica class exists. Check first.
- Do not introduce GUI-based steps unless explicitly requested.
- Keep outputs concise and reproducible.
- When there is a choice between a more realistic model and a more robust model, prefer the more robust model for the first iteration.

## Project structure

Expected structure:

- `README.md`: setup and reproduction instructions
- `requirements.txt`: Python dependencies
- `run.py`: main headless simulation entrypoint
- `verify.py`: post-run verification
- `MyDC/package.mo`: top-level Modelica package
- `MyDC/package.order`
- `MyDC/Examples/package.mo`
- `MyDC/Examples/package.order`
- `MyDC/Examples/SingleRoomDX.mo`: minimal simulation model

## Technical goals

The baseline model should represent a minimal air-cooled DC thermal loop with:

- one room or one lumped thermal zone
- one aggregated IT heat source
- one simple cooling representation
- at least one temperature output that changes over time
- Python-driven execution using OMPython

Do not start with complex chilled-water systems, detailed rack-by-rack airflow, CFD, or power network coupling unless explicitly requested.

## Execution priorities

Always work in this order:

1. Confirm environment and tool availability.
2. Confirm Modelica and Buildings can be loaded.
3. Confirm the custom package can be loaded.
4. Run the minimal simulation.
5. Verify results exist and are sensible.
6. Only then refine structure or documentation.

## Required checks before calling work complete

Before finishing, ensure all of the following are true:

- `omc` is callable
- Python can import `OMPython`
- Modelica standard library loads
- Buildings loads from a real path
- `MyDC.Examples.SingleRoomDX` loads
- simulation runs from Python
- result location is reported
- README contains exact reproduction steps
- verification script passes or clearly explains failure

## Error-handling rules

If a step fails:

- identify the specific failing layer:
  - environment
  - Python dependency
  - Buildings path
  - Modelica package structure
  - model compilation
  - simulation runtime
  - result parsing
- fix the smallest likely cause first
- rerun the failed step before changing additional files
- do not claim success without rerunning verification

If Buildings data-center-specific components are difficult to validate, fall back to simpler Buildings thermal components or a simpler Modelica + Buildings-compatible formulation that still satisfies the baseline goals.

## Coding rules

- Keep Python code straightforward and explicit.
- Put configurable paths and major runtime parameters near the top of `run.py`.
- Add basic exception handling with actionable error messages.
- Keep comments short and useful.
- Avoid unnecessary dependencies.
- Prefer deterministic filenames and output directories.

## Modelica package rules

- Keep the package structure valid for OpenModelica.
- Maintain `package.mo` and `package.order` correctly.
- Use clear class names.
- Avoid speculative inheritance hierarchies in the first version.
- Keep the first model easy to inspect and extend.

## README requirements

README must include:

- prerequisites
- assumed versions if known
- how to obtain or point to Buildings
- exact commands to run
- expected directory structure
- expected outputs
- common failure modes
- what is intentionally simplified
- next sensible extensions

## Done definition

The task is done only when a new user can:

1. install the documented prerequisites,
2. point the code at a valid Buildings installation,
3. run `python run.py`,
4. see that the simulation completed,
5. run `python verify.py`,
6. understand the main outputs from the README.

## Reporting expectations

At the end of a task, provide:

- files created or changed
- commands run
- checks passed
- remaining limitations
- next recommended extension
