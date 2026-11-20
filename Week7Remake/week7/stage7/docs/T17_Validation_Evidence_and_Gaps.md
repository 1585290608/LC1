# LC1 Stage 7 — T17 Independent-Check Evidence and Native Solver Gap

**Date:** 19 November 2026 · **Classification:** exploratory research, **not** native MDT/HOMER Pro validation.

## Work now executed

- **6 analytical micro-benchmarks / 22 metric comparisons passed.** The independent fixed closed-form results assess: a 24h DG start-delay case, a 24h DG with a 125 L fuel limit, a 24h renewable-only critical/aux priority case, a one-hour battery discharge case, a one-hour battery charge case and a one-hour grid-limit service-priority case.
- **5 archived hourly traces independently audited (18,024 rows):** Stage 6 normal grid case 50/50 kW + 300 kWh at 100 kW import; Stage 6 normal grid case 100/100 kW + 450 kWh at 250 kW import; Stage 4 W03 baseline, DG unavailable 24–48h, and three refuelling arrivals. Audit independently recomputes AC supply=use, BESS DC state energy, load-tier priority, SOC continuity and, for outage, fuel mass conservation. The audit does not trust stored residual fields.
- **27 service-matched economic cases / 567 year-by-year rows** independently reassembled from archived Stage 6 results. The selected 20-year discounted cash-flow PV reconciles to the original to less than £1e-6. Not full NPC; no outage probability, event expense or unmet-energy shadow price counted.
- Four non-header **8,760-value, one-kW-value-per-line files** are available to manually import as HOMER Pro primary electric loads. These are static *planned* EV loads, not vehicle state-feedback dispatch.

## Exact analytical fixture assumptions

| Fixture | Closed-form calculation | Expected |
|---|---|---|
| DG startup | 40 kW requested × (24–1) h; 0.25 L/kWh | 920 kWh; 230 L; 40 kWh ENS |
| DG limited fuel | 125 L ÷ 0.25 L/kWh, 50 kW × 24 h requested | 500 kWh generated, 700 kWh ENS |
| PV/Wind priority | wind 15 kW × 24 h, extra PV 30 kW for hours 10–15; 20 kW critical + 15 kW auxiliary | Critical ENS 90 kWh, Aux ENS 270 kWh, curtailed 60 kWh |
| BESS discharge | min(50,40,(0.7–0.3)×100×0.9) | 36 kWh AC, end SOC 0.30, critical ENS 14 kWh |
| BESS charge | min(80–20,40,(0.9–0.3)×100/0.9) | 40 kWh AC, end SOC 0.66, curtailment 20 kWh |
| Grid priority | load 40+30+10 kW, PV 20 kW, feeder 30 kW, battery at reserve | 0/20/10 kWh critical/aux/EV hourly deficit |

**Very important:** The DG test fixture deliberately uses a **constant 0.25 L/kWh** fuel law to permit hand verification. Stage 4's actual production/outage simulations use the inherited **MDT_DERIVED** fuel curve. Passing the constant-law fixture **does not validate** that curve. Component test conditions are likewise not equivalent to full hybrid dispatch.

## Audit interpretation details

- `dg_delivered_kw` in Stage 4 refers to generator energy delivered to **load only**. AC supply accounting must include `dg_generated_kw – dg_dumped_kw`, not `dg_delivered_kw` alone; the latter omits DG-to-BESS transfers.
- `fuel_initial_l` is sampled **after any hour-start delivery**. Within-hour fuel mass conservation is `fuel_initial_l – dg_fuel_consumed_l – fuel_final_l = 0`. Cross-hour inventory continuity is `previous_fuel_final_l + hour_start_delivery_accepted_l – current_fuel_initial_l = 0`. Do not count deliveries twice.
- Stage 6 EV charging slot deficit may be re-requested in a subsequent hour and **is not permanent mission-energy loss**. No EENS or loss-of-load probability is inferred from the 52 deterministic outage start windows.

## Cross-validation status

| Evidence class | Status | What it supports | What it does NOT support |
|---|---|---|---|
| Original Python tests, original hash preservation | Passed | Regression & historical reproducibility | External truth |
| Stage 7 closed-form fixtures | 6/6 passed | Selected component mathematics | Full DER dispatcher parity |
| Stage 7 raw trace double-entry audit | 5/5 passed | Saved Stage 4/6 hourly energy/fuel accounting | Native software or physical validation |
| Historical 24h native MDT DG-only reference | Historical, preserved | The earlier isolated DG cross-check | New 120-person, EV, BESS and multi-day design |
| New native MDT / HOMER Pro | **0 / 0 runs** | Nothing yet | Any claim of new native parity |
| Sennybridge site survey / OEM-supported V2B | Not available | None | Actual installed-site or mobile emergency support |

## Next genuine native work and acceptance

1. In the installed/licensed native environment, record tool version, full project file checksum, native input and output checksums. Do not invent a native project file or screenshots.
2. Begin with DG-only / renewable-only / BESS one-hour component benchmarks. Match fuel, power limits, startup delay, efficiency, SOC bounds and timestep *before* comparing numbers. Mark any unmodelled startup or native dispatch assumption as `NOT_COMPARABLE_CONTROLLER`.
3. Import Stage 7 8,760-row primary electric load, select model year **2025**, and verify total/peak load. **Do not** mistake archived per-unit renewable-output series for HOMER's meteorological GHI (kWh/m²) or wind speed (m/s).
4. Only then construct truly equivalent 24/72/168-hour hybrid scenarios. Native Load Following / Cycle Charging controllers have different semantics from custom LC1. Use custom controller if supported or describe non-equivalence; never label a default HOMER controller result as equivalent by assumption.
5. Enter actual results into `external_handoff/USER_FILL_native_component_results_template.csv`, attach native source and version metadata, set equivalence fields only after manual inspection, then run the Stage 7 comparator. Its input hashes and value comparison do not authenticate the source.
6. T17 remains open until at least one *genuine* native project is built, run and reviewed, with numerical agreement or transparently documented disagreement.

## Official public tool documentation consulted

- HOMER Pro, [Importing a Load from a Time-series File](https://homerenergy.com/products/pro/docs/latest/importing_a_load_from_time_series_file.html): supports 8,760 single-column kW rows (one value per time step).
- HOMER, [Dispatch Strategy and Controllers](https://homerenergy.com/docs/knowledgebase/article/dispatch-strategy-and-controllers/): Load Following, Cycle Charging, Combined Dispatch, Generator Order and MATLAB Link differ.
- HOMER Pro, [Fuel Curve](https://homerenergy.com/products/pro/docs/latest/fuel_curve.html): linear fuel curve parameters use intercept **coefficient** and slope; do **not** assume the LC1 piecewise fuel curve imports unchanged.
