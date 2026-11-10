# Maintaining the LC1 repository

[简体中文](workspace-guide-zh.md)

Keep shared equipment models and energy accounting in `models/core/`. Put
outage dispatch and contingency logic in `models/islanded/`, and annual grid
dispatch and lifecycle cost calculations in `models/grid_connected/`.
All models read the shared inputs in `data/`. Place validation evidence and
selected result tables in `validation/`, and figures in `Image/`.

Use descriptive scenario names and retain the original identifier in the
[scenario index](scenario-index.md). Record the model version, input hashes,
outage window and initial conditions with each result. The operating reserve
floor and the state of charge at outage start are separate inputs.

Run `python -m pytest -q` from the repository root. Use the
[archive replay](../validation/archive-replay.md) to compare against the
frozen hourly traces and cashflows. The [source map](source-map.csv) identifies
byte-identical copies and files adapted for the consolidated layout.

Keep full solver archives and machine-specific notes in their original
locations or in the Git-ignored `local-only/` directory. Check the staged file
list before pushing changes that include new data, reports or figures.
