# Stage 4 T17 — Validation Boundary and Proposed Matched Benchmarks

**Current evidence:** Stage4 static runs 1,508/1,508 internally valid; Stage4 EV feedback runs 52/52 internally valid; 780/780 matching Stage3 numerical baseline metrics; 96 Python tests; original 166 frozen file hashes unchanged. These constitute *self-consistency and regression*, NOT independent external tool validation.

**New native MDT studies:** 0. **New HOMER Pro studies:** 0. No authentic project/export in this package supports new parity.

## Matched benchmark sequence (gated)

1. Re-run controlled original historical **DG-only 24h** native MDT benchmark, source case and exported result recorded. A preserved historical comparison exists, but does not establish this new experiment.
2. Match a **single 24h critical-only** hour-index load (same source weather, unit and clock); document UPS, fuel law, DG startup and minimum operating power.
3. Match **PV/Wind-only 24h** output using the shared hourly per-unit profiles and rated power.
4. Match **BESS-only 24h** charge/discharge caps, 0.8944 per-direction efficiency and SOC 0.1/0.9; note EMS reserve is controller-dependent.
5. Match **combined 168h** 100/100/450 baseline at hours 0, 336 and 6720; require any controller departures to be logged as `NOT_COMPARABLE_CONTROLLER`, not silently corrected.
6. If MDT can represent fuel addition and forced unavailability, replicate 500 L @ 72h, three deliveries, and DG off hours 24–48 with exact tank caps. If unavailable, document that native cross-validation is **structurally unsupported**, not failed parity.
7. For HOMER Pro, separately define financial assumptions, lifetime replacements, dispatch basis and load priority implementation before computing NPC. Never replace native NPC with the existing illustrative CAPEX proxy.

## Source-of-truth anchors

- `week7/stage3/external_inputs/LC1_reference_profiles_8760.csv` and `LC1_external_input_provenance.json` for demand/resources and source SHA-256.
- `week7/stage3/external_inputs/LC1_DG_MDTCatalogue_Fuel_Curve.csv` for archived **active** MDT-derived 25–100% DG fuel curve, *not* the unused fixed `0.25 L/kWh` default.
- `week7/stage4/contingency.py` for Stage4 intervention timing, 2,000 L tank cap and per-step accounting.
- `week7/stage4/outputs/stage4_stage3_baseline_parity.csv` for exact regression (780 pairs), not independent solver parity.

## Evidence checklist for any future native run

Record native software version/licence context, raw project file, 2025 LST hour indices, dispatch policy, priority load implementation, minimum generator output, initial storage/fuel, fuel replenishment semantics, results/export files and SHA-256, unmodified numerical results and manually reviewed differences.

**No EENS** or failure probability is calculated in Stage4. 52 starts are deterministic coverage of one weather year and do not represent an empirical distribution.
