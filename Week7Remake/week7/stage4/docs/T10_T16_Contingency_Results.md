# LC1 Microgrid — Stage 4: Fuel, DG Availability & Dispatch Sensitivity

**Date:** 19 November 2026  
**Project:** EN3400 LC1 Hybrid Microgrids for Defence Applications  
**Evidence class:** `EXPLORATORY_PYTHON_SCREENING` — not MDT/HOMER Pro validation, site measurement, OEM qualification, or real deployment evidence.

## 1. Research question and method

Study the sensitivity of conditional 168-hour islanded energy availability to (a) scheduled diesel fuel deliveries, (b) forced diesel-generator (DG) non-availability and (c) stationary-storage dispatch thresholds, without changing the historical LC1 models. Adopt the *provisional* 120-person, seven-EV `central` hourly load (2025 fixed LST), 100 kW diesel, 90 kW battery PCS, 2,000 L tank, initial SOC 70%, and the archived `MDT_DERIVED` piecewise DG fuel curve. Hourly controller is the Stage 3 S3-v2 model and not a validated controls implementation. The electric system assumes an AC reference; power quality/transients are not modelled.

52 deterministic starts at `h = 0, 168, …, 8568` use the 2025 weather profiles, each independently reset to the same tank/SOC. The main candidate is PV 100 kW / Wind 100 kW / BESS 450 kWh. A selected six-policy subset is repeated for PV/Wind 75/75 kW + 450 kWh and 100/100 kW + 600 kWh. Each case independently runs a full 168 hours.

**Critical ENS** = sum of unserved C4ISR-tier power × 1 hour. **Total ENS** = critical + auxiliary + planned EV charging ENS. These are *scenario* outcomes; no event probabilities or annual outage counts are specified. Thus **the study does not calculate EENS, LOLE or probabilistic reliability**. A `critical_shortfall_windows` count is a descriptive count *of simulation starts*, not a likelihood of power interruption.

## 2. Comparison of policies, PV 100 / Wind 100 / BESS 450

| Counterfactual policy | Mean Total ENS (kWh/168h) | Mean Critical ENS (kWh/168h) | Critical-shortfall starts / 52 | Mean accepted delivered fuel (L/168h) |
|---|---:|---:|---:|---:|
| No refuel; DG available | 767.0 | 126.9 | 15 | 0.0 |
| +500 L planned at hour 72 | 423.8 | 38.5 | 6 | 463.7 |
| +1,000 L planned at hour 72 | 333.2 | 13.4 | 2 | 722.3 |
| +500 L at hours 48, 96 and 144 | 288.0 | 0.0 | 0 | 1,196.8 |
| Same three deliveries, miss hour 48 | 336.2 | 10.8 | 2 | See raw CSV |
| Same three deliveries, miss hour 96 | 336.2 | 10.8 | 2 | See raw CSV |
| Same three deliveries, miss hour 144 | 333.2 | 13.4 | 2 | See raw CSV |
| DG forced offline hours 24–48, no refuel | 1,327.8 | 245.6 | 41 | 0.0 |
| DG forced offline hours 0–72, no refuel | 2,729.2 | 548.3 | 50 | 0.0 |
| DG off 24–48 AND all three deliveries | 1,154.9 | 198.7 | 41 | See raw CSV |

Numbers are rounded for display; full-precision results in `outputs/stage4_52start_contingency_summary.csv` and all 1,508 runs in `outputs/stage4_52start_contingency_full.csv`. 52 of 52 windows with all three scheduled refuels avoid critical shortfall under *these model assumptions*, **not** a universal 168h reliability guarantee.

**Fuel delivery accounting:** at each designated hour, accepted litres = `min(requested_litres, 2000 − current_tank_litres)`; the remainder is labelled *unaccepted* rather than silently added to the tank. The three nominal 500 L deliveries therefore inject an average **1,196.8 L**, not necessarily 1,500 L. Transfer is assumed instantaneous; access, convoy time, bad weather, safety shutdown, quality, emissions, refuelling logistics and cost are excluded. Missing-delivery tests are *deterministic failure cases*, not derived frequency estimates.

## 3. Stationary capacity and dispatch sensitivity

- **75/75 kW + 450 kWh:** no refuel gives 1,486.0 kWh mean Total ENS, critical shortfall in 27/52 windows. With three deliveries, mean Total ENS = 383.1 kWh and zero critical-shortfall windows under this test.
- **100/100 kW + 450 kWh:** 767.0 kWh mean Total ENS and 15/52 critical shortfalls; with three deliveries 288.0 kWh and zero critical-shortfall windows.
- **100/100 kW + 600 kWh:** 719.0 kWh mean Total ENS and 15/52 critical shortfalls; with three deliveries 252.9 kWh and zero critical-shortfall windows.

These numbers demonstrate sensitivity of a *conditional 168h energy-autonomy endpoint*, not the cheapest, best or assured system. The 450 vs 600 kWh comparison still needs full lifecycle cost and non-2025 weather tests.

For the 100/100/450 candidate, tested changes in dispatch reserve SOC, DG stop SOC and allowing DG→BESS charging have small or mixed effects compared with supply logistics; e.g. dispatch reserve 40% produces mean Total ENS 739.5 kWh but mean Critical ENS 130.9 kWh, compared with the 30% baseline 767.0 / 126.9. **The SOC dispatch reserve is a controller threshold and not a universally protected battery floor**: under committed diesel/backup logic, the hardware minimum SOC (10%) is enforced, but the 30% EMS threshold is not guaranteed in every emergency interval. See actual controller and test traces before interpreting “reserve” as assured backup energy.

## 4. Mission readiness sub-study (dynamic EV SOC)

Thirteen evenly spaced starts across the 2025 year were rerun with per-vehicle charging feedback (13 starts × four policies = **52 additional cases**, distinct from the 1,508 static-load outcomes). Each 168h run preconditions its *assumed* vehicle fleet on uninterrupted charging before the outage. Over the thirteen repeated scenarios (each independently initialised), there are 377 **simulated** opportunities per policy:

| Policy | Mission opportunities | Missed departures |
|---|---:|---:|
| Baseline | 377 | 3 |
| +500 L at 72h | 377 | 1 |
| Three 500 L deliveries | 377 | 0 |
| DG forced offline 24–48h | 377 | 1 |

The apparently lower missed departures in the forced-DG-outage policy than in baseline **does not indicate greater fleet resilience**: mission feasibility depends on specific event timing, prioritised charging and feedback-adjusted load. Total ENS becomes substantially worse. These are seven provisional EV archetypes, not certified vehicles. Emergency EV discharge / V2B is disabled throughout.

## 5. Integrity and comparison boundaries

- **1,508 of 1,508** deterministic static-load runs finished; **52 of 52** dynamic EV runs finished.
- Exactly **780** per-metric tests compare Stage 4 `BASE` with archived Stage 3 numerical outputs for all 52 weekly starts and three capacities; largest absolute deviation `< 5×10⁻¹³` in corresponding native units.
- Largest AC balance residual `2.84×10⁻¹⁴ kWh`, battery residual `4.27×10⁻¹⁴ kWh`, cumulative fuel inventory residual `2.90×10⁻¹² L`.
- **96/96** Python tests pass (84 existing + 12 Stage 4 tests) at time of packaging; original 166-file frozen baseline hashes verified unchanged.
- **New native MDT / HOMER Pro executions: zero.** Historical DG-only 24h MDT parity cannot validate this revised multicomponent, load-and-logistics model.

## 6. Unresolved engineering and dissertation tasks

1. **T10/T16:** obtain feasible fuel-delivery schedules and availability evidence; test missed/late refuels against actual operating restrictions and start-up/fuel transfer constraints; consider DG failure/repair probabilities only if justified evidence is available.
2. **T09/T16:** do not assert optimal PV/Wind/BESS from conditional ENS; add realistic component CAPEX/O&M, generator maintenance, fuel delivery charges, NPC discounting and defined reliability valuation, then do full HOMER Pro optimisation if available.
3. **T17:** validate appropriate partial benchmarks in native MDT; verify EMS comparability and energy source mapping before any full-system numerical claim. Current MD/metadata are only *preflight*.
4. **T18/T20:** obtain supervisor scope decisions D1–D9 plus new D10 fuel-logistics scenario, D11 DG downtime assumptions and D12 planned-vs-served EV loading.
5. **WP3:** no bidirectional charging/V2B contribution without exact charger/vehicle/islanding evidence and mission-reserve model. This remains conditional future work.

**Research interpretation:** Under these assumptions, *fuel logistics and DG availability are material resilience constraints* for a 168h contingency. No policy has been proven practical or reliable under field conditions; full-basis design and supervisor signoff are pending.
