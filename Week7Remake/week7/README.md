# LC1 Week 7: demand, EV charging and controlled islanded screening

**Evidence class:** PROVISIONAL SITE + SOFTWARE-VERIFIED NUMERICAL RESULTS. Original LC1 project files are retained byte-for-byte (see `audit/baseline_sha256.csv`). No original results are overwritten by these new scripts.

## Run from repository root

```bash
python week7/audit/check_preservation.py
python -m pytest -q -p no:cacheprovider tests week7/tests
python -m week7.load_model
python -m week7.outage_sensitivity
```

**Important:** Run `load_model` before `outage_sensitivity`, as the latter loads newly generated hourly CSVs. For a new experimental run, copy the `week7/outputs` directory to a new versioned folder before regenerating outputs. The original `data/`, `models/`, `validation/` and `Image/` source files are never changed.

## Outputs

- `audit/baseline_sha256.csv`: frozen source-file digests, all original 166 files preserved.
- `audit/assumption_matrix.csv`: comparison of historical Design A, synthetic B, integrated GitHub and new Week 7 parameters.
- `audit/validation_gap_report.md`: native MDT versus Python evidence boundary and unresolved checks.
- `config/equipment.csv`: site equipment rating and declared operating hours.
- `config/fleet.csv`: 7 proposed EV archetypes with fleet duties and power limits.
- `outputs/{low,central,high}_load_8760.csv`: load-tier 8,760-hour profiles, plus 14 non-duplicated equipment series.
- `outputs/{low,central,high}_ev_trace_61320.csv`: one-hour per-vehicle SOC, charging, propulsion and availability, 61,320 rows per case.
- `outputs/{low,central,high}_equipment_calculations.csv`: annual equipment hours and kWh.
- `outputs/S0_original_site_rerun_S3_dispatch.csv`: baseline *site* with same S3 policy as new site, **not** legacy controller S0.
- `outputs/revised_load_original_hardware_outage_matrix.csv`: original hardware under 3 demand cases x 3 durations.
- `outputs/capacity_screen_nine_options_168h.csv`: limited 9-design candidate matrix plus indicative CAPEX and partial Pareto flag.
- `outputs/capacity_quarantined_issue_details.json`: three failed dispatch configurations recorded and excluded from ranking.
- `outputs/contingency_screen_168h.csv`: baseline, lower fuel, 24-hour DG outage, lower RE and combined stress.
- `outputs/screening_summary.json`: study counts and strict evidence qualifiers.
- `load_calculation_report.md`: all calculation summaries, methodological limits and results.
- `methodology_notes.md`: writing-ready method *notes* (not final dissertation text).

## Key caveats

- All current 120-person loads and EV battery/vehicle values are **modelling assumptions**, not actual MOD procurement or OEM data.
- Original source file `data/load.csv` remains the historic 1,104-kWh/day profile.
- New EV trajectories are **normal scheduled charging demand**, not dynamically linked to unserved charging under outage dispatch. Therefore mission-readiness percentages under outage are **not** claimed.
- **No new native MDT or HOMER Pro executions**. The prior archived DG-only native MDT check does not validate the revised integrated microgrid.
- Neither a nine-point screen nor one winter outage can identify a universally optimal system. `50/50/450`, `75/75/300`, `75/75/450` cases are quarantined due to an inherited S3 same-hour battery power-direction conflict.
