# LC1 Week 7 — Stage 3 (source-preserving continuation)

This folder advances T09, T15–T17, T18–T20 from the user's approved LC1 Microgrid Development Plan. It does not overwrite the original LC1 model or Week7 prior-stage output files. New work is in `week7/stage3`.

## Run (from `LC1-main` root, Python 3.13)

```sh
python -m week7.stage3.external_protocol
python -m week7.stage3.weekly_scan
python -m week7.stage3.make_outputs
python -m pytest -q -p no:cacheprovider tests week7/tests week7/nextstage/tests week7/stage3/tests
python week7/audit/check_preservation.py
```

## What was actually completed

- 1,404 simulations: 52 2025-week start points × 3 durations × 9 static central-load equipment combinations; per-case conservation, fuel inventory and SOC checks.
- 108 generic cross-software case manifest records and 8,760h source profiles with SHA256, archived MDT-derived fuel curve and safety-gated comparator. No native project files, no new native MDT/HOMER runs.
- English dissertation methodology version 0.3, a results comparison, a conservative T17 validation guide and a supervisor decisions handoff.
- Original source SHA-256 checks and regression tests. Testing is NOT field or native software validation.

## Main limitations

All load/EV values are illustrative. Every window starts anew with 2,000 L fuel / 70% BESS SOC, so the 52-window summary is not probability-weighted EENS or a longitudinal operation record. Fixed-2025 weather, 1 h dispatch and idealised single AC reference cannot certify voltage, frequency, fuel logistics, islanded protection, charger hardware or grid-forming capability. The nine candidates are not exhaustive and the cost figures are illustrative CAPEX, not HOMER NPC.
