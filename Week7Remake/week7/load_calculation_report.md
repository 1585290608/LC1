# LC1 Week 7 — Load Calculation and Preliminary Screening Report

**Report date:** 19 November 2026. **Model status:** hypothetical 120-person camp and generic vehicle archetypes. Numerical Python checks complete; no field measurement, new native MDT, or HOMER optimisation. All timestamps are source 2025 LST, `dt=1 hour`.

## 1. Evidence and methodology

The original source archive has 166 hashed unchanged files. Current repository regression 53/53 passes; 13 additional test instances for the Week 7 extension give **66/66 combined passes**. These are software and hourly accounting checks. Real hardware and MDT hybrid parity remain unverified.

Load calculation (each hourly interval): `equipment_kWh = rated_kW × scenario_utilisation × schedule_indicator × 1 h`; `site_kWh = C4ISR + auxiliary + EV_charge_AC`. For each vehicle `E_trip = distance_km × traction_kWh_per_km`, `E_accepted_DC = charger_AC_kWh × 0.92`, and `SOC_after = SOC_before + E_accepted_DC / battery_capacity_kWh`. Propulsion draw occurs at the mission return hour; the departure guard checks enough pre-departure SOC for trip draw plus protected reserve.

## 2. Proposed 120-person camp demand (not official MOD meter data)

| Demand case | kWh/year | kWh/day avg | Peak kW | C4ISR MWh/year | Aux MWh/year | EV AC MWh/year |
| --- | --- | --- | --- | --- | --- | --- |
| low | 682,535.2 | 1,870.0 | 172.1 | 332.9 | 314.5 | 35.17 |
| central | 763,901.1 | 2,092.9 | 195.1 | 332.9 | 387.1 | 43.96 |
| high | 871,656.4 | 2,388.1 | 225.0 | 332.9 | 483.8 | 54.95 |


**Historical LC1:** 402,960 kWh/year, 1,104 kWh/day, 65 kW peak. The revised Central case is **not** a correction to these historical figures; it is a distinct unverified design envelope.

### Equipment rating and central-demand calculation

| Non-duplicated category | Tier | Installed assumed kW | Annual energised h | Mean kWh/day |
| --- | --- | --- | --- | --- |
| C4ISR_and_command | c4isr | 25.0 | 8,760 | 600.0 |
| Medical_and_emergency_refrigeration | c4isr | 4.0 | 8,760 | 96.0 |
| C4ISR_cooling | c4isr | 6.0 | 8,760 | 144.0 |
| Perimeter_security_lighting | c4isr | 6.0 | 4,380 | 72.0 |
| Accommodation_ventilation | aux | 12.0 | 8,760 | 230.4 |
| Accommodation_socket_loads | aux | 18.0 | 4,380 | 172.8 |
| Accommodation_lighting | aux | 12.0 | 2,920 | 76.8 |
| Catering_electric_cooking | aux | 26.0 | 2,920 | 166.4 |
| Workshops_and_maintenance | aux | 18.0 | 1,566 | 61.8 |
| Laundry | aux | 12.0 | 1,460 | 38.4 |
| Water_pumping_and_treatment | aux | 8.0 | 2,190 | 38.4 |
| Common_area_lighting | aux | 8.0 | 3,650 | 64.0 |
| Space_heating_electric | aux | 30.0 | 3,032 | 199.4 |
| Summer_cooling_noncritical | aux | 6.0 | 920 | 12.1 |


Auxiliary central utilisation is 80% of listed site-group ratings when scheduled, and the year-average kWh/day includes actual weekday and seasonal operating hours. Source assumptions are in `config/equipment.csv`; separate heating/cooling end uses do not overlap, and C4ISR cooling is excluded from accommodation ventilation.

## 3. Fleet and controlled charging (normal schedule only)

| Vehicle | Role | Battery kWh | Traction kWh/km | AC charger kW | Min SOC | Mission km |
| --- | --- | --- | --- | --- | --- | --- |
| LU01 | Light_Utility_EV | 75 | 0.25 | 11 | 0.20 | 60 |
| LU02 | Light_Utility_EV | 75 | 0.25 | 11 | 0.20 | 65 |
| LU03 | Light_Utility_EV | 75 | 0.25 | 11 | 0.20 | 50 |
| LU04 | Light_Utility_EV | 75 | 0.25 | 11 | 0.20 | 55 |
| ML01 | Medium_Logistics_EV | 160 | 0.65 | 22 | 0.25 | 95 |
| ML02 | Medium_Logistics_EV | 160 | 0.65 | 22 | 0.25 | 90 |
| ME01 | Mobile_Emergency_Support_EV | 100 | 0.35 | 11 | 0.45 | 20 |


| Case | EV AC kWh/year | EV DC kWh/year | EV traction kWh/year | Departures | Min observed precharge SOC |
| --- | --- | --- | --- | --- | --- |
| low | 35,167.0 | 32,353.6 | 32,353.6 | 1513 | 0.591 |
| central | 43,958.7 | 40,442.0 | 40,442.0 | 1513 | 0.514 |
| high | 54,948.4 | 50,552.5 | 50,552.5 | 1513 | 0.418 |


All seven proposed vehicles retain at least their independent mission reserve in *unconstrained normal charging* with a shared hypothetical 70 kW charger cap. The model has no OEM support evidence and **does not** couple under-supplied EV charging in islanding back to subsequent individual SOC. Thus it cannot certify mission readiness during outages.

## 4. Reproducible original-site versus revised-site comparison

| Outage h | Site model | C4ISR ENS kWh | Total ENS kWh | C4ISR EA % | DG fuel L | End BESS SOC |
| --- | --- | --- | --- | --- | --- | --- |
| 24 | S0 original site | 0.0 | 0.0 | 100.00 | 41.0 | 0.282 |
| 72 | S0 original site | 0.0 | 0.0 | 100.00 | 577.9 | 0.182 |
| 168 | S0 original site | 0.0 | 0.0 | 100.00 | 997.0 | 0.212 |
| 24 | S1 proposed 120 people | 0.0 | 3.1 | 100.00 | 363.2 | 0.100 |
| 72 | S1 proposed 120 people | 0.0 | 468.2 | 100.00 | 1,362.7 | 0.100 |
| 168 | S1 proposed 120 people | 259.6 | 3,534.6 | 95.93 | 2,000.0 | 0.100 |


These S0/S1 labels mean *site-load scenarios*; both use the inherited **S3 dispatch policy**, the original 50/50/300/90/100 kW equipment and the same time windows. This is not the legacy dispatch-strategy label S0. 24/72/168 are nested windows with independent initial inventories, not three independent random weather samples.

## 5. Limited nine-point capacity screen (Central, first 168 winter hours)

| PV/Wind kW | BESS kWh | Indicative CAPEX £ | Critical EA % | Total ENS kWh | Fuel used L | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| 50/50 | 300 | 529,350 | 95.93 | 3,534.6 | 2,000.0 | NONDOMINATED_IN_NINE_OPTIONS_ONLY |
| 50/50 | 450 | 589,350 | — | — | — | INELIGIBLE_NOT_VALID |
| 50/50 | 600 | 649,350 | 95.93 | 3,384.4 | 2,000.0 | NONDOMINATED_IN_NINE_OPTIONS_ONLY |
| 75/75 | 300 | 660,775 | — | — | — | INELIGIBLE_NOT_VALID |
| 75/75 | 450 | 720,775 | — | — | — | INELIGIBLE_NOT_VALID |
| 75/75 | 600 | 780,775 | 99.09 | 1,112.5 | 2,000.0 | NONDOMINATED_IN_NINE_OPTIONS_ONLY |
| 100/100 | 300 | 792,200 | 100.00 | 362.2 | 1,583.9 | NONDOMINATED_IN_NINE_OPTIONS_ONLY |
| 100/100 | 450 | 852,200 | 100.00 | 226.6 | 1,581.7 | NONDOMINATED_IN_NINE_OPTIONS_ONLY |
| 100/100 | 600 | 912,200 | 100.00 | 313.0 | 1,539.5 | DOMINATED |


**6/9 completed.** Three candidates reached a same-hour BESS charging/discharging exception in the inherited S3 routine and were quarantined. Full errors and exact first failure hours are preserved. The Pareto flag considers illustrative **upfront CAPEX versus total 168-hour ENS only**, restricted to these completed options; there is no global optimum, year-life NPC, or independently verified OEM price.

## 6. Central-scenario deterministic contingency screen (168 h)

| Case | C4ISR ENS kWh | Total ENS kWh | DG fuel L | End SOC |
| --- | --- | --- | --- | --- |
| BASE | 259.6 | 3,534.6 | 2,000.0 | 0.100 |
| FUEL_500L | 1,700.5 | 8,486.5 | 500.0 | 0.100 |
| DG_OFF_H24_TO_H48 | 759.8 | 3,674.5 | 2,000.0 | 0.100 |
| LOW_RE_60PCT | 989.7 | 5,272.7 | 2,000.0 | 0.100 |
| FUEL_500_AND_DG_OFF | 1,725.2 | 8,488.5 | 500.0 | 0.100 |


Emergency DG unavailability occurs for elapsed hours 24–48 in the declared stress input. `LOW_RE_60PCT` is a constructed resource multiplier, not observed bad weather or fault frequency. No refuelling takes place. The inherited energy model assumes an energised AC reference during DG outages; its calculated renewable service does **not** establish grid-forming or black-start feasibility.

## 7. Validation limits and priority next steps

**Confirmed:** source-file identity and 66 software tests; hourly power/energy conservation of completed Python runs; vehicle *planned* SOC reserves, individual AC charger ratings and shared AC power; auditable tier-specific energy accounting.

**Outstanding (mandatory for credible final sizing):** real site load references; source-aligned OEM generator/charger data; normal-grid connection adequacy; vehicle readiness feedback from microgrid `ev_unserved_kw`; controller correction of 3 quarantined cases; multi-season and probabilistic uncertainty if claims require reliability; native MDT/HOMER Pro re-runs under equivalent models; independent review of assumed AC reference and 25 kW dump sink.

**Scope gate:** EV bidirectional supply remains **future/conditional**. Do not add hypothetical 10, 20 or 30 kW V2G contributions until real bidirectional capability and mission reserve evidence are available.
