# LC1 Week 7 — Stage 6

## Purpose

T09/T16 normal-year grid import headroom, dynamic seven-EV fleet SOC, hourly energy-balance and normal-year cash-flow **proxy** (not complete NPC), in addition to preserved Stage 3–5 independent islanded scenarios. New code only under `week7/stage6/`. No native MDT or HOMER Pro run.

## Reproduce (from `LC1-main` root)

```bash
PYTHONDONTWRITEBYTECODE=1 python -B -m week7.stage6.run_study --jobs 4
PYTHONDONTWRITEBYTECODE=1 python -B -m week7.stage6.grid_limit_sweep
PYTHONDONTWRITEBYTECODE=1 python -B -m week7.stage6.postprocess
PYTHONDONTWRITEBYTECODE=1 python -B -m pytest -q -p no:cacheprovider tests week7/tests week7/nextstage/tests week7/stage3/tests week7/stage4/tests week7/stage5/tests week7/stage6/tests
PYTHONDONTWRITEBYTECODE=1 python -B week7/audit/check_preservation.py
```

`--jobs 1` is the serial equivalent. Uses 81 8,760-hour provisional grid-limit simulations and 14 focused sweeps; outputs are CSV and PNG. For experiment details see `docs/Stage6_T09_Annual_Grid_and_Cost_Results.md`.

## Strict interpretation

- No validation against native MDT/HOMER Pro or field deployment.
- Unserved EV charging hour is deferrable; it can be re-requested on a later hour. It is NOT automatically lost annual traction kWh or reliability EENS. See `EV_charging_slot_deficit_kwh_DEFERABLE` vs `nondeferrable_infrastructure_ENS_kwh`.
- Grid limit values are unapproved sensitivity assumptions. `NO_SHORTFALL_ENERGY_ONLY` says nothing about network stability, fault performance or connection permission.
- Do not add Stage 5 hypothetical fuel/outage present values to normal-year 2025 repeated grid costs without a coherent timeline/event probability and double-count prevention. Economic column is **not full NPC**.
- Baseline files are frozen with `week7/audit/baseline_sha256.csv`. Always use `python -B` / `PYTHONDONTWRITEBYTECODE=1` to avoid rewriting historical `.pyc` files in the original archive.
