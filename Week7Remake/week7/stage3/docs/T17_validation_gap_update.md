# Stage 3 — Validation and Audit Results

- **Frozen archive:** original 166-file SHA256 baseline remains separately checked with `python week7/audit/check_preservation.py`.
- **Python tests:** all 84 collected test instances pass (78 previously reported + 6 new Stage3 tests). Tests confirm code and numerical accounting only.
- **Extended deterministic studies:** 1,404 valid of 1,404; max AC residual 2.84e-14 kWh; no same-hour BESS dual operation; fuel inventory nonnegative.
- **External tool comparability:** Week7 new MDT runs = 0, HOMER Pro runs = 0. The profiles, actual archived diesel fuel model and 108-case manifest are *generic interchange inputs* only.

## Historical MDT scope

Historical saved comparison `validation/diesel-energy-accounting/native-mdt-diesel-comparison.csv` demonstrates DG-only, 24 h controlled parity for generated kWh, service and fuel under matched archived catalogue assumptions; its source records are inherited, not rerun here. No new native solver results have been provided and full microgrid parity remains unverified.

## Active diesel model mapping (important T17 audit finding)

S3-v2 calls `ResearchDiesel.set_fuel_model('MDT_DERIVED')`. This bypasses the `Settings.fuel_l_per_kwh = 0.25` fixed default. Correct external reference fuel values, at generator ON output:

| ON power (kW) | Actual archived-model fuel rate (L/h) |
|---:|---:|
| 25 | 9.8421 |
| 50 | 15.5202 |
| 75 | 21.8608 |
| 100 | 28.0120 |

This curve is archived catalogue-derived, not new manufacturer validation. Idle and generator output below 25 kW are deliberately not extrapolated.

## Open evidence gaps

1. Site/camp infrastructure and vehicle values are unverified provisional assumptions; approval needed.
2. 100 kW grid-import assumption has not been established from an actual Sennybridge connection study.
3. External MDT/HOMER project/runtime settings and authentic output files are absent: new cross-tool parity cannot be claimed.
4. The 52 equal-spaced weather windows do not estimate EENS, failure probabilities, weather extremes outside 2025, or 168h sustained reliability under fuel-delivery uncertainty.
5. No voltage, frequency, network load-flow, grid-forming, UPS transfer, earthing, protection or OEM vehicle bidirectional evidence.
6. CAPEX is illustrative; comprehensive NPC requires fuel price, tariffs, O&M, replacement, outage valuation and lifecycle definitions.

## Evidence labels for dissertation graphics

`EXPLORATORY_PYTHON_SCREENING` for all new figures and numerical results; `HISTORICAL_DG_ONLY_PARITY` for the preserved 24h native comparison; `NOT_VALIDATED_NATIVE` for the new hybrid models and sizing conclusions; `NOT_IMPLEMENTED` for S2/S3 emergency EV discharge.
