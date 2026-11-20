# Stage 7 — T09 economic replay and non-overlapping cash-flow guard

**Inputs:** the archived Stage 6 `stage6_81_annual_grid_cases.csv` and the inherited `models/grid_connected/config/economic-parameters.json` used in Stage 5/6. **Outputs:** 567 year-by-year rows and 27 comparison rows in `stage7/outputs/`.

**Selection:** only all 27 hypothetical 250 kW grid-limit runs (three demand cases × nine capacities) have zero hourly requested-service shortfall and therefore qualify for this limited service-matched comparison. Cases which shed scheduled loads are not included; choosing a cheaper underserviced case would be an invalid economic comparison.

| Example, Central Demand | Initial CAPEX | Annual grid bill | Selected 20-year cash PV (NOT full NPC) |
|---|---:|---:|---:|
| PV/Wind 100/100 kW, BESS 300 kWh | £792,200 | £75,996.72 | £2,313,178.04 |
| PV/Wind 100/100 kW, BESS 450 kWh | £852,200 | £74,079.45 | £2,396,428.01 |
| PV/Wind 100/100 kW, BESS 600 kWh | £912,200 | £73,009.51 | £2,492,284.18 |

**Verification:** max absolute difference to the archived Stage 6 total across 27 candidates was `9.313225746e-10 GBP`, i.e. floating-point rounding only. This is a replay of the historical financial model, **not** independent evidence of prices or life cycle.

**Excluded (explicitly zero in this ledger):** outage-related fuel burn and dispatch switching, refuelling trips, probability-weighted EENS, shadow reliability prices, EV bidirectional equipment, electrical connection upgrades, local contracted energy tariffs, ancillary services, degradation beyond inherited replacement assumptions. Outage ENS remains a **separate physical metric**, not added to the normal cashflow result.

**Note:** The 2,000 L fuel inventory is purchased at t=0 and recovered at t=20 using the inherited assumption. It must not be confused with diesel fuel **consumption**; energy consumption and stock movements are different cash-flow concepts. The inventory recovery itself remains an unverified economic simplification.
