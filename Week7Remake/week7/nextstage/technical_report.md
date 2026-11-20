# LC1 Week 7 Next Stage — Numerical Development & Decision Report

**Date:** 19 November 2026. **Evidence class:** exploratory versioned Python modelling, **not** native MDT/HOMER Pro/field certification.

## WP0 — Preservation and regression

- Original model directories and prior Week7 outputs have not been edited. SHA-256 source baseline: **166/166 matched**.
- Total Python tests: **78 passing**, including the 53 inherited tests and the Week7/new regression tests. These are numerical/software checks only.
- Historical native MDT parity remains DG-only / limited. **Zero newly executed native MDT or HOMER Pro comparisons**.

## WP2 / T08–T10 — S3-v2 control repair and nine candidates

Original S3 had three out of nine combinations quarantined because the diesel depleted fuel within an hour after briefly charging the BESS and then attempted to discharge BESS within the same hour. `nextstage/dispatcher.py` prospectively inhibits diesel-to-BESS charging in that case, retaining a single BESS direction during each hour. No original S3 file or historical CSV was changed.

| PV / Wind (kW) | BESS (kWh) | Critical EA (%) | Total ENS (kWh) | Fuel used (L) | Illustrative CAPEX (£) |
|---:|---:|---:|---:|---:|---:|
| 50 / 50 | 300 | 95.93 | 3,534.6 | 2,000.0 | 529,350 |
| 50 / 50 | 450 | 95.93 | 3,464.2 | 2,000.0 | 589,350 |
| 50 / 50 | 600 | 95.93 | 3,384.4 | 2,000.0 | 649,350 |
| 75 / 75 | 300 | 99.09 | 1,319.8 | 2,000.0 | 660,775 |
| 75 / 75 | 450 | 99.09 | 1,213.0 | 2,000.0 | 720,775 |
| 75 / 75 | 600 | 99.09 | 1,112.5 | 2,000.0 | 780,775 |
| 100 / 100 | 300 | 100.00 | 362.2 | 1,583.9 | 792,200 |
| 100 / 100 | 450 | 100.00 | 226.6 | 1,581.7 | 852,200 |
| 100 / 100 | 600 | 100.00 | 313.0 | 1,539.5 | 912,200 |

All nine options now complete the 2025-01-01 168h **static-demand** window with zero same-hour BESS charging/discharging, AC residual under 1e-6 kWh and no fuel inventory violation. The six originally valid options reproduce their prior ENS/fuel/SOC figures within 1e-6.

**Four independent 168-hour seasonal starts; summed outcomes are descriptive, NOT probability-weighted EENS:**

| PV / Wind (kW) | BESS (kWh) | Four-window total ENS (kWh) | Worst Critical EA (%) | Sum fuel consumed (L) |
|---:|---:|---:|---:|---:|
| 50 / 50 | 300 | 8,945.2 | 90.33 | 8,000.0 |
| 50 / 50 | 450 | 8,576.4 | 90.33 | 8,000.0 |
| 50 / 50 | 600 | 8,310.4 | 90.33 | 8,000.0 |
| 75 / 75 | 300 | 2,276.2 | 99.09 | 6,870.3 |
| 75 / 75 | 450 | 2,113.4 | 99.09 | 6,744.2 |
| 75 / 75 | 600 | 1,819.2 | 99.09 | 6,652.4 |
| 100 / 100 | 300 | 1,073.1 | 100.00 | 4,932.8 |
| 100 / 100 | 450 | 739.8 | 100.00 | 4,707.8 |
| 100 / 100 | 600 | 698.9 | 100.00 | 4,372.1 |

**Finding:** 100/100/600 reduces the *sum* of four 168h ENS windows relative to 100/100/450 but has worse winter ENS (313.0 vs 226.6 kWh) and higher static CAPEX. This is a dispatch-dependent, non-monotonic result. No optimal design is claimed; an economic NPC and larger weather/control space are missing.

## WP1 / WP4 — EV supply affects mission readiness

The new feedback model reroutes *served*, rather than requested, charging into seven connected EV batteries. Mission departure occurs only if traction energy plus protected reserve is available; otherwise the mission is counted as missed, not falsely executed. The vehicle model matches the original all-served 8,760-hour charge profile and 1,513 annual scheduled departures.

| Winter 168h case | Planned mission opportunities | Missed missions | Mission readiness | Dynamic charging ENS (kWh) |
|---|---:|---:|---:|---:|
| 50/50 kW + 300 kWh BESS | 29 | 1 | 96.55% | 3,472.2 |
| 75/75 kW + 450 kWh BESS | 29 | 0 | 100.00% | 1,618.3 |
| 100/100 kW + 450 kWh BESS | 29 | 0 | 100.00% | 614.0 |
| 100/100 kW + 600 kWh BESS | 29 | 0 | 100.00% | 852.4 |

In the 50/50/300 winter case, **1/29 mission opportunities fails** (ML01 on 2025-01-07 at 06:00 LST) because insufficient delivered charging left inadequate departure SOC for its 95 km assumed duty plus 25% protected reserve. This is a **model assumption**, not a documented real-world operational failure.

In the all-served reference, charging remains exactly consistent with the 2025 8,760h generated demand. Under an outage, unmet charging may accumulate and missed trips alter future load requirements; consequently static and feedback-model `ev_ENS_kwh` have different denominators and must not be treated as directly comparable totals.

### WP2 / T10 — Dynamic 168-hour contingency responses

| Stress condition | Critical EA (%) | Total ENS (kWh) | Missions missed / attempted |
|---|---:|---:|---:|
| BASE | 95.93 | 6,555.4 | 1 / 29 |
| FUEL_500L | 73.35 | 16,250.8 | 8 / 29 |
| DG_OFF_H24_TO_H48 | 88.10 | 6,315.1 | 0 / 29 |
| LOW_RE_60PCT | 83.38 | 8,625.0 | 1 / 29 |
| INITIAL_BESS_SOC_30PCT | 95.70 | 6,697.0 | 1 / 29 |
| FUEL_500L_AND_DG_OFF | 72.44 | 15,479.2 | 3 / 29 |

These sensitivities are deterministic and assume no fuel delivery during the 168h window.

## WP1 grid limit diagnostic (NOT a connected-network dispatch)

Before stationary BESS or diesel dispatch, an illustrative 100 kW maximum import limit with the original PV 50 kW / Wind 50 kW would be exceeded by the following hours:

| Demand case | Peak residual import (kW) | Hours over 100 kW | Import deficit sum (kWh/year) |
|---|---:|---:|---:|
| low | 172.1 | 666 | 17,066.3 |
| central | 195.1 | 1,005 | 35,064.3 |
| high | 225.0 | 1,805 | 67,548.0 |

This is a warning about the 100 kW assumption, **not** a claim that the real connection, inverters, or grid power flow have been simulated.

## WP3 / T11 evidence gate and WP5 decision

All fleet entries are generic Light Utility, Medium Logistics, and Emergency Support archetypes, not designated real OEM models. No actual islanded V2B/V2M support was demonstrated. Optional WP3 T12–T14 remains withheld until chargers, PCS, safety/islanding protection, mission reserve and marginal costs are justified.

## Validation boundary / next steps

1. **T17:** Perform fresh native MDT runs, with matched input traces, solver assumptions and controller; preserve native output files and report numeric differences. Current status **NOT DONE**.
2. **T09/T16:** Expand beyond four chosen dates and three durations; add justified outage/repair probabilities only if EENS is desired; analyse diesel refuelling and technology reliability.
3. **T03–T07:** Replace assumed Sennybridge site ratings and EV archetypes with cited/approved equipment evidence; confirm site 100 kW grid connection and occupancy scenarios.
4. **T18–T20:** Supervisor review to approve the scope and whether unvalidated V2B/V2M should remain Future Work.

**Caution:** This model does not establish transient UPS continuity, 3-phase load flow, inverter grid forming, voltage/frequency performance, protective isolation, automatic transfer, site electrification readiness, or economic optimum. No real-world defence deployment has been validated.
