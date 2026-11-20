# LC1 Stage 6 — T09 Annual Grid-Connected Feasibility and Normal-Year Cost Proxy

**Research date:** 19 November 2026  
**Scope:** EN3400 LC1, *provisional* 120-person representative site, seven hypothetical EV archetypes, fixed-LST 2025 weather.  
**Evidence:** Python energy-balance simulation, **not** distribution power flow, network-connection approval, native MDT/HOMER or real-site validation.

## Work executed

- Completed **81** separate 8,760-hour runs: three demand levels × three PV/Wind pair ratings (50/50, 75/75, 100/100 kW) × three stationary BESS capacities (300/450/600 kWh) × three *hypothetical* grid import limits (100/150/250 kW).
- Completed **14** additional 8,760-hour import-headroom scans: central/high demand, 100/100 kW PV/Wind, 450 kWh BESS, limits 100–250 kW in 25 kW increments.
- Reused original provisional hourly weather/resources and infrastructure load categories; EV load is recalculated dynamically from each vehicle's connected state, charger power, traction energy and protected mission reserve. Failed hourly EV charging can be attempted later.
- Modelled original 90 kW PCS, 0.8944 charge/discharge AC–DC efficiency, 30% ordinary battery reserve, 70% initial/terminal target and a 48-hour terminal SOC management window. **No routine DG usage**; no load-serving UPS credit and no assumed grid export in the main runs.
- Applied load-service priority **C4ISR → Auxiliary → EV Charging** and retained any service deficit explicitly, rather than violating the import limit. Passed hourly AC/DC conservation and SOC/PCS/grid power checks.

## Key numerical findings

Selected PV 100 kW / Wind 100 kW / BESS 450 kWh results:

| Demand | Assumed grid limit | Cumulative hourly requested-service shortfall* | Hours with shortfall | Missed EV departures |
|---|---:|---:|---:|---:|
| Central | 100 kW | 41,946.93 kWh | 1,045 | 0 / 1,513 |
| Central | 150 kW | 3,119.27 kWh | 179 | 0 / 1,513 |
| Central | 175 kW | 445.08 kWh | 46 | 0 / 1,513 |
| Central | 200 kW | 0 | 0 | 0 / 1,513 |
| Central | 250 kW | 0 | 0 | 0 / 1,513 |
| High | 100 kW | 80,140.12 kWh | 1,801 | 5 / 1,513 |
| High | 150 kW | 12,430.00 kWh | 453 | 0 / 1,513 |
| High | 200 kW | 632.20 kWh | 48 | 0 / 1,513 |
| High | 225 kW | 0 | 0 | 0 / 1,513 |

* **Not EENS or unique permanent loss of EV energy.** Unserved hourly requests include EV charging deferrals: an unmet charging request may be presented again the following hour, so summing EV shortfalls can repeatedly measure delayed battery deficit. Evaluate the infrastructure-critical/Auxiliary ENS separately and use **actual missed departures** for EV mission readiness. In the 81-run main matrix, zero critical C4ISR ENS was recorded because load priority protects this tier; noncritical service can still fail badly.

All **27** assumed-250 kW grid cases met every *hourly requested energy service* in the three demands and nine equipment options. No candidate at 100 or 150 kW was free from hourly shortfalls. The **200 kW Central** and **225 kW High** thresholds apply **only to the tested 100/100/450 combination under this controller**; they are not mathematical minimum grid connection sizes and are **not approved site import limits**. Electrical fault duty, converter grid-forming, protection, power factor, startup and voltage compliance are not checked.

## Economic comparison (selected normal-year cash streams only)

For *Central*, with assumed 250 kW import limit and all scheduled energy served:

| PV/Wind (kW) | BESS (kWh) | Annual grid import (kWh) | Selected 20-year normal-year cash PV proxy | Independent 168h islanded mean ENS |
|---|---:|---:|---:|---:|
| 50/50 | 300 | ~520,966 | ~£2.693m | 3,356.5 kWh |
| 75/75 | 450 | ~403,829 | ~£2.567m | 1,486.0 kWh |
| 100/100 | 300 | ~313,611 | ~£2.313m | 846.2 kWh |
| 100/100 | 450 | ~305,623 | ~£2.396m | 767.0 kWh |
| 100/100 | 600 | ~301,165 | ~£2.492m | 719.0 kWh |

The proxy includes **inherited illustrative** initial CAPEX, fixed O&M, scheduled component replacements, tank inventory purchase/recovery, hypothetical grid electricity purchases (24p/kWh), £2/day standing charges and zero export sales. The same 2025 operation is repeated for a 20-year 3% real discount calculation. It deliberately **does not add Stage 5 hypothetical outage costs** to the normal year, because overlap/double counting and event probabilities are not resolved. It excludes charging hardware variation, grid-connection upgrades, local tariff quotes, site construction variation, generator cycling, degradation, grid disruptions, tax and reliability-related costs. **It is NOT a validated NPC or a price quote.**

Import tariff what-if cases at 16.8p/24p/31.2p per kWh yield 243 pricing scores but do not change physical dispatch. Do not compare economic values of shed-load alternatives as though full service were delivered.

## Interpretation and required decisions

1. **T09:** Increasing BESS from 300 to 600 kWh at fixed PV/Wind 100/100 costs more in the selected normal-year cash proxy, yet improves *separate* islanded average ENS. No global optimum is claimed.
2. **T16:** EV charging-deferral kWh is not the same quantity as scenario ENS for non-deferrable loads or mission-failure probabilities. Maintain separate response measures.
3. **T17:** There are zero new native MDT/HOMER runs. Stage 6 energy-balance and file-hash tests are internal consistency checks only.
4. **T20:** Confirm whether the site is assumed to be continuously grid connected, intermittently connected or normally islanded; determine the actual connection limit and charging/service priority with the supervisor. This assumption is decisive for peacetime economics.

### Reproduction

```bash
cd LC1-main
PYTHONDONTWRITEBYTECODE=1 python -B -m week7.stage6.run_study --jobs 4
PYTHONDONTWRITEBYTECODE=1 python -B -m week7.stage6.grid_limit_sweep
PYTHONDONTWRITEBYTECODE=1 python -B -m week7.stage6.postprocess
PYTHONDONTWRITEBYTECODE=1 python -B -m pytest -q -p no:cacheprovider tests week7/tests week7/nextstage/tests week7/stage3/tests week7/stage4/tests week7/stage5/tests week7/stage6/tests
PYTHONDONTWRITEBYTECODE=1 python -B week7/audit/check_preservation.py
```

**Validation boundary:** This is an operational energy adequacy *screening* only. Hourly AC/DC energy balance is insufficient to prove real-world microgrid electrical stability, network capacity, fault protection, or native software parity.
