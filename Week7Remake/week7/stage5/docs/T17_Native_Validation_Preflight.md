# LC1 Stage 5 — T17 Native MDT/HOMER Validation Preflight

**Status:** `INTERNAL_PREFLIGHT_PASSED_NATIVE_NOT_PERFORMED`.

## What was checked

- SHA-256 of the Stage 3 external 8,760-hour reference profiles, 108-case manifest and four-point active `MDT_DERIVED` diesel fuel curve against their registered provenance.
- All 8,760 consecutive 2025 fixed-LST hourly timestamps and arithmetic consistency of planned Critical, Auxiliary and EV loads for low/central/high profiles.
- All 166 original frozen source-file SHA-256 values.
- All nine existing Stage 4 result artifact hashes; 1,508 static and 52 dynamic EV research runs; 780 Stage 3 vs Stage 4 BASE comparison entries; model-internal validity labels.

**These are internal provenance and self-consistency checks, not cross-solver verification.** New native Microgrid Design Toolkit simulations in Stage 5: **0**. New HOMER Pro simulations in Stage 5: **0**. No authentic new native project/export file is in the package, and a generic input CSV is not a native MDT/HOMER project format.

## Required next externally executed validation steps

1. Record native MDT software version, actual project settings, weather clock convention, fuel law and load-tier implementation. Re-run original DG-only 24-hour test as a separate historical benchmark. Do not extrapolate this to revised hybrid dispatch.
2. Run a matched 24-hour critical-only isolated benchmark. Require engine start delay, fuel curve, initial inventory, UPS assumptions, controller and priority logic to be documented.
3. Compare PV/Wind-only hourly generation output, BESS-only power/energy conversion and controller semantics separately before attempting the 168-hour combined S3-v2 case.
4. Attempt matched 168-hour combined cases with start indices 0, 336 and 6720 only where matching priority-load dispatch, fuel cap, initial SOC and AC-reference model are feasible. If not, record `NOT_COMPARABLE_CONTROLLER` or `UNSUPPORTED_TOOL_FEATURE`; do not invent a numerical pass.
5. For refuel, DG forced shutdown and EV mission readiness tests, document native tool feature support. If native refills, tiered dispatch or vehicle missions cannot be represented equivalently, use Python sensitivity as a separate model result, not native cross-validation.
6. For HOMER Pro, include a complete commercial-cost case with qualified component quotes, normal-year operations, fuel and O&M, replacement and load-service assumptions before its NPC can be compared with this project's **partial PV of selected cash streams**. There is no complete NPC comparison in Stage 5.

`week7/stage3/compare_external.py` is an existing guarded comparison programme for separately supplied native exports with matching metadata and SHA-256. It does not independently authenticate the export and should only run after provenance and configuration equivalence are reviewed.

Source-of-truth for this preflight: `outputs/stage5_T17_preflight.json` and `outputs/stage5_T17_preflight.csv`.
