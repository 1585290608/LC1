# T19 — S0/S1/S4 Research Comparison (Version 0.3)

**Evidence:** numerical Python simulation only, provisional 120-person load, 2025 fixed LST; not MOD measured data or HOMER/MDT re-optimisation.

## A. Historical-demand S0 compared with revised-demand S1

The common hardware and Jan 1–7 window are used; **demand changed**, so differences measure the modelled consequence of a new load assumption, not a measured efficiency improvement.

| Indicator (same 168 h start) | S0 original demand | S1 provisional central demand |
|---|---:|---:|
| PV / Wind / BESS | 50 / 50 kW / 300 kWh | 50 / 50 kW / 300 kWh |
| Critical ENS (kWh) | 0.0 | 259.6 |
| Total ENS (kWh) | 0.0 | 3,534.6 |
| Diesel use (L) | 997.0 | 2,000.0 |
| Critical EA | 100.00% | 95.93% |

S0 was independently replayed in the previous phase using the historical S3 dispatch, while S1 here is the isolated S3-v2 repair. Other than the documented fuel-exhaustion charge-direction safeguard, the six previously valid candidate outcomes matched prior screening within 1e-6. Therefore **demand changes dominate the comparison, but it is not a pure controlled treatment on identical controller code**. The result remains a research model comparison.

## B. Extended candidate comparison: 52 weekly outage starts

Every result below is for a **168-hour** independent outage initialisation under identical 2,000 L initial diesel fuel, 70% BESS SOC and static central EV charging demand. `Mean` is per simulated window, not probability-weighted EENS. CAPEX assumes indicative coefficients from `week7/outage_sensitivity.py`, not a vendor quote or net present cost.

| PV / Wind (kW) | BESS (kWh) | Indicative CAPEX (£) | Mean Total ENS (kWh) | p90 Total ENS (kWh) | Worst Critical EA | Critical-shortfall windows (of 52) |
|---:|---:|---:|---:|---:|---:|---:|
| 50 / 50 | 300 | 529,350 | 3,356.5 | 5,158.6 | 63.22% | 52 |
| 50 / 50 | 450 | 589,350 | 3,272.4 | 5,079.1 | 63.22% | 52 |
| 50 / 50 | 600 | 649,350 | 3,191.0 | 5,000.9 | 63.69% | 52 |
| 75 / 75 | 300 | 660,775 | 1,569.0 | 3,904.2 | 69.00% | 28 |
| 75 / 75 | 450 | 720,775 | 1,486.0 | 3,814.8 | 69.54% | 27 |
| 75 / 75 | 600 | 780,775 | 1,422.6 | 3,725.7 | 69.54% | 26 |
| 100 / 100 | 300 | 792,200 | 846.2 | 2,690.7 | 74.79% | 15 |
| 100 / 100 | 450 | 852,200 | 767.0 | 2,533.8 | 75.10% | 15 |
| 100 / 100 | 600 | 912,200 | 719.0 | 2,429.1 | 75.10% | 15 |

The 24h and 72h groups produced zero Critical ENS in each of the 52 aligned starts, but noncritical ENS remains. For 168h, even the 100/100 kW, 600 kWh configuration experiences **15 of 52** intervals with nonzero Critical ENS, at a worst-window Critical EA of approximately **75.10%**. In all those 15 windows the diesel fuel stock was exhausted in the model. These are conditional counterfactual results, not observations of 15 actual outages.

The 100/100/600 option gives lower descriptive **mean total ENS** than 100/100/450 (719.0 vs 767.0 kWh/window), but costs approximately £60,000 more in indicative stationary-storage CAPEX. The 600 kWh alternative does **not** eliminate the same 15 critical-shortfall windows. No unique economic/resilience optimal capacity is selected.

## C. EV and S2/S3 scope separation

- **S1 dynamic fleet charging:** inherited previous-phase result for Jan 168 h: 50/50/300 gives 28 completed of 29 planned mission opportunities; 75/75/450, 100/100/450 and 100/100/600 each show 29/29 in that particular window. These outcomes depend on provisional vehicle sizes/routes and served charging.
- **S2 single emergency vehicle V2B**: no execution or quantified benefit. OEM + charger + island/grid-forming proof missing.
- **S3 mission-constrained fleet V2M**: no execution or quantified benefit; EV propulsion reserve is enforced for charging/mission readiness but no V2B discharge algorithm is switched on.
- **S4 extra stationary BESS, no V2B:** capacity alternatives are in the 52-week table, with an assumed fixed 90 kW PCS and no lifecycle battery wear pricing.

## D. Interpreting the result for the dissertation

The central research finding is sensitivity to **site-demand assumptions, outage start, diesel fuel availability and dispatch**, not evidence of an installed design or an economically optimal microgrid. In particular, the previous four-season 100% critical EA for some candidates is a statement about those four windows only, not a year-round guarantee.

Figures: `week7/stage3/figures/52week_capex_vs_mean_ENS.png` and `52week_critical_shortfall_count.png` (research-only, non-native).

## E. Unresolved comparisons

No genuine new native MDT/HOMER Pro runs; no site energy telemetry; no OEM V2B/V2M evidence; no probabilistic EENS; no NPC or full network voltage/frequency/UPS ride-through assessment. All future doctoral/supervisor-quality conclusions require these caveats.
