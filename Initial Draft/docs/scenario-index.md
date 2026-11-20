# Scenario naming index · 研究编号对照

Folders and figure captions use names that explain the research question.
Use the original identifiers to trace each entry to configurations, tests and archived results.

| Original study | Folder |
| --- | --- |
| Draft 2 | [Diesel energy accounting](../validation/diesel-energy-accounting/) |
| Draft 3A | [Diesel fuel and dispatch](../validation/diesel-fuel-and-dispatch/) |
| Draft 3B | [Grid-connected economics](../validation/grid-connected-economics/) |
| Draft 3B carbon supplement | [Grid electricity carbon](../validation/grid-electricity-carbon/) |
| Draft 3C | [Outage resilience](../validation/outage-resilience/) |
| Draft 4 | [Cross-study integration](../validation/cross-study-integration/) |

## Coverage and code families

| Family | Included in this checkout | Preserved at original location |
| --- | --- | --- |
| Draft research stages | Selected model or report evidence for Draft 2, 3A, 3B, 3C and 4 | Draft 1 original snapshot and full sealed study outputs |
| Original MDT D0–D2C | [D0-derived input copies](../data/) and the [engineering index](../validation/historical-engineering-evidence/) | D0 source reconciliation and D1, D2, D2B, D2C reports and native evidence |
| Remake versions | [Historical version index](../validation/historical-engineering-evidence/#remake-versions) | V1/V2 mapping, V3–V11 archived reports and V12–V16 full workspaces |
| Original MDT P0–P9 | [Work-package index](../validation/historical-engineering-evidence/#original-mdt-work-packages) | Original implementation plan and engineering records |
| Dispatch S0–S3 | 24 main results across both fuel formulations and 24, 72 and 168 h | Full run evidence |
| Economic P0/P0R/P1/P3 | 12 annual case IDs and 16 financial case IDs in the saved comparison and sensitivity tables | Raw annual dispatch and cashflow traces |
| Resilience C1–C4 | All 18 unique cases and their original group memberships | Raw traces and reused Draft 3A winter baseline |

Economic P2 (price-aware EMS) was planned and has no executed results. D4A–D4C
are planning labels. D4 reconciles archived results using the nominal 50 kWp PV,
50 kW wind, 100 kW DG, 300 kWh BESS and 90 kW PCS configuration documented in its report.

## Diesel and battery control strategies

The saved table contains all 24 combinations of four strategies, two fuel formulations and three outage durations.

| ID | Descriptive name |
| --- | --- |
| S0 | Reference dispatch with diesel surplus sent to dump load |
| S1 | Recover feasible diesel surplus into the battery |
| S2 | Battery-SOC-based diesel start/stop control |
| S3 | Combined diesel start/stop control and surplus charging |
| FIXED_025 | Fixed 0.25 L per generated kWh fuel formulation |
| MDT_DERIVED | Archived MDT positive-load fuel-curve formulation |

[Saved strategy comparison](../validation/diesel-fuel-and-dispatch/strategy-comparison.csv)

## Normal grid-connected operation

P0 is grid only. P0R includes diesel and UPS backup. P1 is hybrid
self-consumption. P3 varies operating reserve. P2 (price-aware EMS) was planned.
E0 and E20 are assumed export caps. R30, R50 and R70 are battery operating
reserve floors. The modelled cap does not establish permission to export.
The separate [sensitivity table](../validation/grid-connected-economics/economic-sensitivity.csv)
contains additional wind output and electricity price cases.

| Original case | Descriptive name |
| --- | --- |
| P0_GRID_ONLY | Grid only |
| P0R_GRID_DG_UPS | Grid with diesel and UPS backup |
| P1_E0_R30 | Hybrid self-consumption, 0 kW export cap, 30% reserve |
| P3_E0_R50 | Hybrid self-consumption, 0 kW export cap, 50% reserve |
| P3_E0_R70 | Hybrid self-consumption, 0 kW export cap, 70% reserve |
| P1_E20_R30 | Hybrid self-consumption, 20 kW export cap, 30% reserve |
| P3_E20_R50 | Hybrid self-consumption, 20 kW export cap, 50% reserve |
| P3_E20_R70 | Hybrid self-consumption, 20 kW export cap, 70% reserve |

### Annual wind sensitivities

| Original case | Descriptive name |
| --- | --- |
| SENS_WIND60_E0_R30 | Hybrid with wind output at 60% of reference, 0 kW export cap, 30% reserve |
| SENS_WIND60_E20_R30 | Hybrid with wind output at 60% of reference, 20 kW export cap, 30% reserve |
| SENS_WIND80_E0_R30 | Hybrid with wind output at 80% of reference, 0 kW export cap, 30% reserve |
| SENS_WIND80_E20_R30 | Hybrid with wind output at 80% of reference, 20 kW export cap, 30% reserve |

### Additional financial sensitivities

These cases use the corresponding P1 hourly results with a different flat import
price. Each retains the 30% reserve assumption of its physical case.

| Original case | Export cap | Import price |
| --- | ---: | ---: |
| P1_E0_R30_PRICE168 | 0 kW | £0.168/kWh |
| P1_E0_R30_PRICE312 | 0 kW | £0.312/kWh |
| P1_E20_R30_PRICE168 | 20 kW | £0.168/kWh |
| P1_E20_R30_PRICE312 | 20 kW | £0.312/kWh |

## Outage resilience

C1 covers season. C2 varies starting fuel. C3 varies starting battery charge.
C4 compares a long outage control against combined reduced renewable availability
and DG outage. The starting charge below describes the start of each islanded event.
C2 uses C1_Winter_P0R and C1_Winter_HYBRID as its 2,000 L references.
C3 uses C1_Winter_HYBRID as its 70% starting-charge reference.
These shared rows are counted once in the 18 unique cases.

| Original case | Descriptive name | Event length | Starting fuel | Starting battery charge |
| --- | --- | ---: | ---: | ---: |
| C1_Winter_P0R | Winter seasonal outage, diesel and UPS | 168 h | 2000 L | — |
| C1_Winter_HYBRID | Winter seasonal outage, hybrid | 168 h | 2000 L | 70% |
| C1_Spring_P0R | Spring seasonal outage, diesel and UPS | 168 h | 2000 L | — |
| C1_Spring_HYBRID | Spring seasonal outage, hybrid | 168 h | 2000 L | 70% |
| C1_Summer_P0R | Summer seasonal outage, diesel and UPS | 168 h | 2000 L | — |
| C1_Summer_HYBRID | Summer seasonal outage, hybrid | 168 h | 2000 L | 70% |
| C1_Autumn_P0R | Autumn seasonal outage, diesel and UPS | 168 h | 2000 L | — |
| C1_Autumn_HYBRID | Autumn seasonal outage, hybrid | 168 h | 2000 L | 70% |
| C2_F500_P0R | Fuel-constrained outage, diesel and UPS | 168 h | 500 L | — |
| C2_F500_HYBRID | Fuel-constrained outage, hybrid | 168 h | 500 L | 70% |
| C2_F1000_P0R | Fuel-constrained outage, diesel and UPS | 168 h | 1000 L | — |
| C2_F1000_HYBRID | Fuel-constrained outage, hybrid | 168 h | 1000 L | 70% |
| C3_SOC30_HYBRID | Starting battery charge, hybrid | 168 h | 2000 L | 30% |
| C3_SOC50_HYBRID | Starting battery charge, hybrid | 168 h | 2000 L | 50% |
| C4_CONTROL_P0R | Long outage control, diesel and UPS | 336 h | 2000 L | — |
| C4_STRESS_P0R | Combined contingency, diesel and UPS | 336 h | 2000 L | — |
| C4_CONTROL_HYBRID | Long outage control, hybrid | 336 h | 2000 L | 70% |
| C4_STRESS_HYBRID | Combined contingency, hybrid | 336 h | 2000 L | 70% |

[Saved scenario matrix with outage timestamps](../validation/outage-resilience/outage-scenarios.csv)
