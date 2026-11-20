# LC1 Week 7 — Next Stage (S3-v2, EV feedback, multi-season screening)

**Baseline integrity:** 166 original SHA-256 source hashes still match `week7/audit/baseline_sha256.csv`. Earlier `week7/outputs/` and the source `models/` tree are not edited. **All numeric results here are exploratory Python calculations, not native HOMER Pro, native MDT, real-world deployment or a full cost optimisation.**

## Reproduce from repository root

```bash
python week7/audit/check_preservation.py
python -m week7.nextstage.screen
python -m pytest -q -p no:cacheprovider tests week7/tests week7/nextstage/tests
```

This overwrites only the *new versioned* `week7/nextstage/outputs/` files. The previously delivered Week7 outputs are kept unchanged. Python standard library and pytest are sufficient for this module; matplotlib is not required. Source weather/data are the historical fixed 2025 LST 8,760-hour inputs.

## Core development

- `dispatcher.py`: isolated S3_v2 copy with prospective protection against diesel-to-BESS charging when fuel will be exhausted within the same control hour and later BESS discharge would be needed. It does **not** relax BESS or fuel constraints.
- `fleet_feedback.py`: per-vehicle SOC and mission tracking; actual served EV AC energy is distributed to connected vehicles (earliest next departure first). An attempted mission fails *before departure* if it would violate mission reserve. Unserved charging is not silently assumed delivered. No V2G/V2B power.
- `screen.py`: nine 168-hour capacity options; four seasonal starts x 24/72/168h x 9 options; 48 dynamic fleet windows; six existing-hardware contingency checks with and without EV feedback; 100 kW import diagnostic prior to BESS/DG dispatch.
- `tests/test_nextstage.py`: inherited historical-capacity agreement on six valid cases, all scenario AC/BESS accounting, no same-hour BESS dual-direction, EV charger and mission stock ledger, zero-service stress, test output determinism and explicit native validation boundaries.

## Main outputs

- `outputs/nine_candidate_v2_168h.csv` — nine complete frozen-demand 168h comparisons.
- `outputs/seasonal_nine_candidates_24_72_168h.csv` — 108 outage calculations; all 9 options × 3 durations × 4 seasonal starts.
- `outputs/mission_readiness_feedback_matrix.csv` — 48 feedback-coupled EV scenarios, including mission readiness.
- `outputs/contingency_v2_168h.csv`, `outputs/contingency_dynamic_EV_mission_readiness_168h.csv` — fixed-demand and dynamic-fleet stress checks.
- `outputs/winter_168h_original_equipment_EV_trace.csv` and `...plant_trace.csv` — per-vehicle and microgrid hourly audit trail.
- `outputs/preliminary_grid_import_limit_diagnostic.csv` — feasibility flag only, NOT a grid-connected solution.
- `outputs/summary_v2.json` — case counts / quarantines / strict evidence status.

## Interpretation / study boundaries

- Site demand = 120-person **proposed** operational support camp, without site survey.
- The four 168h outage starts are Jan 1, Apr 1, Jul 1, Oct 1 2025 at 00:00 LST, **not** a probabilistic outage distribution. Sums across them are not EENS.
- Fuel = 2000 L initial unless specified; SOC = 70% unless specified; 100 kW DG, 90 kW PCS, 25 kW assumed dump limit.
- `ev_ENS_kwh` in a dynamic run measures **updated** charging demand that responds to previous unserved energy and cancelled missions; it is not directly comparable to original fixed-demand EV ENS without accounting for changed requested energy.
- Annual fixed load profiles are copied and unchanged; only dynamic EV loads change during coupled simulations.
- `Critical Load EA=100%` is an hourly energy-service figure; it is not evidence for UPS transients, frequency, voltage, protection, grid-forming, black start, or real-world outage survival.
- `capex_gbp_illustrative` is a reused static source assumption, not validated prices / NPC / LCOE / business case.

## Remaining gates

1. T03–T05: Site survey, equipment and OEM support for load/vehicle inputs.
2. T09: Multi-year, fuel re-supply, asset reliability, weather and alternative dispatch control sensitivity; HOMER optimisation.
3. T11–T14: Actual bidirectional vehicle and inverter **evidence gate** (see `wp3_bidirectional_evidence_gate.md`).
4. T17: Fresh independent native MDT parity with matched weather/load/component/controller assumptions; not executed here.
5. T18–T20: Supervisor selects dissertation/extension scope and reviews evidence.
