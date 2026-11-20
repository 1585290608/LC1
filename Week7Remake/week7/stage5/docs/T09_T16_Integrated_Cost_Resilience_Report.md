# LC1 Stage 5 — T09/T16 Cost–Resilience–Fuel Logistics Integrated Screening

**Prepared:** 19 November 2026  
**System:** EN3400 LC1 — provisional 120-person camp and seven EV archetypes  
**Evidence status:** `ILLUSTRATIVE_CONDITIONAL_NOT_NPC_NOT_EENS_NOT_NATIVE_VALIDATED`  
**Scope:** 52 deterministic 168-hour windows, 2025 fixed local-standard-time input year. Not random-event sampling, not supplier pricing, not DG warranty/availability assurance.

## Executive findings

1. Raising PV/Wind from 100/100 kW and BESS from 450 to 600 kWh raises inherited illustrative installed **CAPEX from £852,200 to £912,200** (+£60,000). Under unchanged no-refuel S3-v2 dispatch, mean total ENS across 52 start windows falls from **767.0 to 719.0 kWh** (~48.0 kWh), but 15/52 windows still exhibit some Critical Load ENS in both cases.
2. For **100/100/450**, scheduling a hypothetical 500 L fuel delivery at hour 72 reduces mean total ENS to **423.8 kWh** and Critical Load shortfall windows to **6/52**. Three 500 L deliveries at 48/96/144 reduce these to **288.0 kWh** and **0/52** respectively. This requires delivery access and DG availability not validated by this study, and under tank limits only **1,196.8 L** on average of the nominal 1,500 L is accepted.
3. Conditional *selected* cash-flow present values (20-year, 3% real discount, one **hypothetical** 168-hour event/year, £500/trip and £0.20/accepted L logistic uplift) are ~**£1,325,125** for 100/100/450 without refuelling, ~**£1,436,203** for 100/100/600 without refuelling, ~**£1,336,152** for 100/100/450 with one delivery, and ~**£1,354,018** for 100/100/450 with three deliveries. **These are NOT Net Present Costs (NPCs)**: peacetime 8,760h electricity service/import/export costs and other missing streams are excluded.
4. No policy was proved to satisfy a defended 168h critical-load criterion. Delivery failures and DG unavailability in Stage 4 undermine the idealised triple-delivery performance. The selected cost ranking is strongly preference-dependent and cannot justify final system capacity selection.

## Explicit cost boundary and source

All cost parameters come from **existing LC1 model assumptions**, not fresh quotes: `models/grid_connected/config/economic-parameters.json`, with a provenance explanation in `validation/grid-connected-economics/assumptions.csv`. Core values: PV £1,257/kW, wind £4,000/kW, DC battery (PCS excluded) £400/kWh, diesel £1.35/L, 2.5% installed-CAPEX fixed O&M/year, 3% discount, 20 years, initial and terminal 2,000 L working inventory, battery/PCS/UPS replacement at year 12, DG at year 15. Each source is explicitly inherited/illustrative, **not a market quote**.

Additional *what-if* logistics rates (no supplier basis): baseline £500 per attempted fuel delivery, plus £0.20 for each actually accepted litre. Requested litres rejected by 2,000 L tank headroom do not incur a per-litre logistics premium, but a delivery attempt still incurs the stated trip fee. Fuel consumed by diesel is charged exactly once; delivered fuel is not also purchased separately. This convention assumes the site replenishes stock between independent 168h events.

Current public context for future cost substantiation, **not numerically substituted into this model**:

- UK DESNZ, [Onshore wind and solar cost and technical assumptions, 6 October 2025](https://www.gov.uk/government/publications/onshore-wind-and-solar-cost-and-technical-assumptions). Scale and capital boundary must be reconciled before transferring to this ~100 kW site.
- UK DESNZ, [Electricity Generation Costs 2025](https://www.gov.uk/government/publications/electricity-generation-costs-2025). Large-scale generation cost/LCOE benchmarks are not direct 100 kW defence microgrid turnkey offers.
- US NLR, [2025 Annual Technology Baseline — Commercial Battery Storage](https://atb.nlr.gov/electricity/2025/commercial_battery_storage). Distinguishes energy/power CAPEX and storage duration; UK FX, taxes, import, installation and PCS scope would need reconciliation.

## Capacity/policy comparison

| PV / Wind | BESS | Planned fuel deliveries | Mean Total ENS (kWh/168h) | Critical-shortfall starts | Illustrative installed CAPEX | Selected 20-year cost PV* |
|---|---:|---|---:|---:|---:|---:|
| 50 / 50 kW | 300 kWh | None | 3,356.5 | 52/52 | £529,350 | £862,094 |
| 75 / 75 kW | 450 kWh | None | 1,486.0 | 27/52 | £720,775 | £1,151,918 |
| 75 / 75 kW | 450 kWh | 500 L @ 48/96/144h | 383.1 | 0/52 | £720,775 | £1,185,325 |
| 100 / 100 kW | 450 kWh | None | 767.0 | 15/52 | £852,200 | £1,325,125 |
| 100 / 100 kW | 450 kWh | 500 L @ 72h | 423.8 | 6/52 | £852,200 | £1,336,152 |
| 100 / 100 kW | 450 kWh | 500 L @ 48/96/144h | 288.0 | 0/52 | £852,200 | £1,354,018 |
| 100 / 100 kW | 600 kWh | None | 719.0 | 15/52 | £912,200 | £1,436,203 |
| 100 / 100 kW | 600 kWh | 500 L @ 48/96/144h | 252.9 | 0/52 | £912,200 | £1,464,949 |

*PV of **selected** cost streams under an assumed **one** 168-hour event per year: CAPEX, fixed O&M, replacement, diesel fuel consumed, fuel inventory and delivery charges; does NOT include normal-operation grid import/export, planned generator fuel during the other 8,592 hours, taxes, external costs or a market-derived outage probability. **Never refer to this column as NPC.**

For all 15 alternatives and full precision, see `outputs/stage5_conditional_economic_comparison.csv`. The omitted combinations include all 9 original non-refuel capacities plus 6 selected fuel-policy alternatives. The 52 start hours remain paired across the same weather/input sequence.

## Shadow-cost and price sensitivity

A **separate non-cash** weighting experiment converts Critical ENS and noncritical ENS into an illustrative preference score. It is not a defence willingness-to-pay, damage estimate, or payments/cash-flow. The underlying physical simulation outputs do not change.

A complete rectangular sensitivity grid includes 486 distinct hypothetical assumption combinations × 15 comparable alternatives = **7,290 scores**: one/four hypothetical outages per year; £0/500/1,500 refuel-trip charge; £0/0.20/0.75 accepted-litre premium; £1/1.35/2 diesel; 0.7/1.0/1.3 battery price multiplier; and three critical/noncritical shadow settings (£0/£0, £100/£10, £250/£25 per kWh).

Winner counts **within this finite choice set**, with 162 combinations for each shadow setting:

| Non-cash shadow values (Critical / Other) | Selected lowest-score alternative | Wins out of 162 |
|---|---|---:|
| £0 / £0 per kWh | PV/Wind 50/50, BESS 300, no refuel | 162 |
| £100 / £10 per kWh | PV/Wind 75/75, BESS 450, three refuels | 162 |
| £250 / £25 per kWh | PV/Wind 75/75, BESS 450, three refuels | 99 |
| £250 / £25 per kWh | PV/Wind 100/100, BESS 450, three refuels | 63 |

This is **not a probability or sensitivity confidence interval**. It shows that design preference shifts when assumed consequences of energy interruption change. Therefore financial and reliability objectives should remain separate until the supervisor agrees a decision rule and defensible cost basis. The lowest-score no-penalty option is operationally inferior by the critical-load metric (52/52 shortfall starts), despite its low inherited CAPEX.

## Reliability and physical feasibility gates

- **No outage probabilities**, so no reliability EENS/LOLE/SAIDI; 52 annual start windows are not a statistical distribution of incident frequency.
- **DG forced unavailability and fuel deliveries:** Stage 4 modelled 100/100/450 DG outage from hour 24 to 48 and observed 41/52 critical shortfall windows, **even with three deliveries**. Missing any single scheduled delivery also reintroduced 2/52 critical shortages. These are separate fuel-access and generator-availability failure modes.
- **No site deployment validation:** the hourly physics assumes the necessary AC reference even when DG unavailable, ignores frequency/voltage transient security and does not prove grid-forming availability; fuel transfer is instantaneous and unconstrained by vehicles/roads.
- **EVs:** Seven scheduled EV archetypes count as noncritical planned charging in the main energy tier. Stage 4 individual EV readiness uses its own dynamic-feedback results; not aggregated into T09 price scoring. No V2B/V2M export power credited.
- **No native MDT/HOMER model replay:** internal preflight passes, but no new independently supplied native exports exist.

## Reproduction and tests

```bash
cd LC1-main
python -B -m week7.stage5.run_study
python -B -m week7.stage5.plots
python -B -m pytest -q -p no:cacheprovider tests week7/tests week7/nextstage/tests week7/stage3/tests week7/stage4/tests week7/stage5/tests
python -B week7/audit/check_preservation.py
```

The study reads Stage 3/4 CSVs and produces only versioned `week7/stage5/outputs/` files. Original LC1 source, historical tests, input weather/load, and Stage 0–4 outputs are not modified. The source-data checks and test log are included in the final package.

**Status:** T09 advanced from capacity-only screening to conditional economic multiobjective screening; T17 remains **internal verification only**. The results are suitable for requesting supervisor feedback but not claiming an economically optimal deployed microgrid.
