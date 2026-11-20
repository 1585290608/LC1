# EN3400 — Proposed Methodology (Version 0.3, working draft)

**Study:** Hybrid Microgrids for Defence Applications (LC1), representative operational-support demand near Sennybridge, Wales.  
**Evidence classification:** exploratory deterministic simulation. This text is **not** confirmation that the installed loads, electricity connection, EV hardware, or proposed network exist at MOD Sennybridge.  
**Prepared:** 19 November 2026. **Supervisor scope approval:** NOT RECEIVED.

## 1. Research aims and design boundary

The objective is to investigate the effect of replacing the original LC1 demand assumption with a transparent, representative **120-person operational support camp**, including grid-to-vehicle charging demand, on the feasibility and resilience of a PV–wind–diesel–battery microgrid capable of operating as an island. The principal research questions are: (i) How does a traceable load estimate affect the adequacy of the original 50 kW PV, 50 kW wind, 100 kW diesel and 300 kWh stationary BESS? (ii) How do generation and stationary storage configurations affect critical-service availability during 24/72/168 h outages? (iii) How does reduced delivered EV charging affect vehicle mission readiness? (iv) Which comparisons require independent simulation, OEM evidence or supervisor approval?

The physical/functional boundary is a *single assumed AC bus*. Distribution impedance, three-phase asymmetry, reactive power, voltage, frequency, power quality, switching transients, energy-export agreements and protection coordination are not solved. The assumed generator, battery inverter and UPS do not establish proven grid-forming or black-start capability.

## 2. Prior work and historical preservation

The frozen historical source baseline (S0) and Cloud A/Cloud B exploration are not modified. Original LC1 Python models and the 2025 source weather are preserved inside the development package, with 166 original files tracked by SHA-256. The previous DG-only 24 h MDT parity record remains labelled **historical limited DG-only numerical parity**; it does not establish new PV/wind/BESS/EV parity. Cloud B outputs with names containing `SYNTHETIC` are not field data or native validation.

The following scenario classes must be kept distinct:

| Scenario | Load model | Battery / vehicle support | Present status |
|---|---|---|---|
| S0 | Original LC1 1,104 kWh/day assumed aggregate | 50/50 kW renewables, 300 kWh BESS, no bidirectional EV | Frozen historical baseline plus Python reference replay |
| S1 | New 120-person central/low/high model | Original hardware as adequacy test; broader sizing under examination | Provisional, Python screening only |
| S2 | Same as S1 | One emergency EV supports critical loads | Not implemented; external V2B technology evidence gate |
| S3 | Same as S1 | Mission-constrained fleet V2B/V2M | Not implemented; external evidence gate |
| S4 | Same as S1 | Extra stationary BESS, no V2G/V2B | Completed 300/450/600 kWh sensitivity under assumed hardware costs; not a globally optimal design |

Do **not** label a selected S1 candidate as *optimum* before HOMER or otherwise matched lifecycle-cost optimisation and additional resilience constraints.

## 3. Traceable electricity demand: WP1 T03–T07

Load assumptions are in `week7/config/equipment.csv` (14 mutually exclusive categories) and `week7/config/fleet.csv` (seven model vehicle archetypes, not specific OEM vehicles). The equipment calculations are in `week7/outputs/{low,central,high}_equipment_calculations.csv` and the hourly outputs in `{low,central,high}_load_8760.csv`. Actual military load surveys and mission diaries have not been obtained.

For equipment category *i* with aggregate energised power rating `P_i` (kW), calendar duty indicator `a_i(t)∈{0,1}`, and case utilisation `u_s,i`, power is

\[ P_{s,i}(t)=P_i\,a_i(t)\,u_{s,i}. \]

The critical tier uses 100% of each energised aggregate rating. In the Auxiliary tier the deterministic utilisation factors are **0.65 (low), 0.80 (central), 1.00 (high)**. These are not measured random occupancy distributions. Report annual energy as `Σ_{t=0}^{8759} P(t) × 1 h`, average `kWh/day = annual kWh / 365`, and demand peak as `max_t P(t)`. Seasonal schedules explicitly separate heating, cooling and ventilation to limit double counting; these separations still require site review.

### 3.1 EV service model

The fleet comprises four 75 kWh Light Utility vehicles, two 160 kWh Medium Logistics vehicles, and one 100 kWh Mobile Emergency Support vehicle, all illustrative. Scheduled route distances, per-kilometre consumption, arrival/departure, charger limits and protected mission reserves are explicit assumptions in the fleet CSV. Charge efficiency is **0.92**, charging target SOC **0.90**, and the total shared AC feeder charging limit **70 kW**.

For vehicle *v*, the discrete SOC identity for an interval is

\[ E_{v,t+1}=E_{v,t}+\eta_{EV,ch}P^{served}_{EV,v,t}\Delta t-E^{traction}_{v,t}. \]

Traction use is deducted upon return in the implementation; a planned departure is allowed only if its pre-departure stored energy meets *route kWh + protected mission reserve*. The return/departure logic and charging schedules are reproduced in `week7/load_model.py` and the outage-supply-dependent feedback in `week7/nextstage/fleet_feedback.py`. Missed trips are logged as misses rather than falsely spending propulsion energy. Unavailable/away vehicles do not charge. **No EV battery energy is transferred to the stationary load** in the present model.

### 3.2 Demand supply coupling

The energy system dispatches the EV requested charging as lowest-priority demand after critical and auxiliary loads. The **actual delivered AC charging**, not requested charging, is returned to the fleet model to determine the next vehicle SOC. Thus `EV charging ENS` is the AC supply deficit of charging requested under the dynamic feedback rule; mission cancellations may alter future charging requests, so a static vs dynamic `EV ENS` comparison has different denominators.

## 4. Microgrid model, energy accounting and dispatch

Available intermittent generation is based on the inherited normalised 2025 Sennybridge-specific source series, scaled by PV and wind nameplate kW. Each simulation uses a one-hour source time step (`Δt=1 h`) in fixed **2025 local standard time**, not time-zone-adjusted British Summer Time. Proportional scaling does not account for wind turbine power-curve or array-layout changes.

Power is allocated preferentially to: **C4ISR and other identified critical loads, then Auxiliary, then vehicle charging**. All categories are definitions for this study, not verified Ministry of Defence service priorities. The stationary battery is constrained to 90 kW PCS, `SOCmin=0.10`, `SOCmax=0.90`, and dispatch reserve `SOCreserve=0.30`; per-direction efficiency is **0.8944**. When modelled as stored energy, its state equation is

\[ E^{B}_{t+1}-E^{B}_t =\eta_c P^B_{ch,t}\Delta t - \frac{P^B_{dis,t}\Delta t}{\eta_d}. \]

The diesel is modelled as 100 kW with a provisional 25% minimum ON-power, **one-hour start-up**, an illustrative 25 kW dump sink, and an initial available fuel stock of 2,000 L per outage experiment. The actual numerical DG fuel function is **MDT_DERIVED**, i.e. an archived piecewise specific-consumption catalogue interpolation (see `models/islanded/config/fuel-models.json`); the default `Settings.fuel_l_per_kwh=0.25` is *not* the fuel function used by S3-v2. It must not be passed to a comparator as the active law. The catalogue is not an OEM guarantee. All balance equations account for generated vs delivered/dumped DG energy, renewable curtailment, inverter losses and fuel inventory separately.

The S3-v2 hourly controller is an isolated copy. If diesel runs out partway through an interval, it prospectively prevents diesel-to-battery charging so that a battery discharge later in that same interval does not occur after a charge; it does not weaken the no-simultaneous charge/discharge constraint. The legacy controller and outputs are preserved and are not silently overwritten.

## 5. Experimental design and common initial state

For every scenario, retain the same input weather and demand clock, controller, load-tier sequence, component model, initial BESS SOC **0.70**, initial diesel fuel **2,000 L**, 90 kW PCS, and UPS assumptions. Resetting initial inventory makes each outage a counterfactual *independent initialisation*, not a continuous fleet-operation or failure-process time series. The original four-season reference tests start at **2025-01-01, 2025-04-01, 2025-07-01, 2025-10-01**; each has outage lengths **24, 72 and 168 h** for nine generation/storage configurations. The extended T15 analysis starts once per 7-day block, **52 starts at hour 0, 168, …, 8568**, with the same three outage lengths and nine capacity candidates: **1,404 additional static-load runs**.

Weather-window starts are systematically spaced, not sampled in proportion to true event probability, and do not form a calibrated stochastic weather/outage distribution. The first 52 aligned 168-hour windows cover 8,736 of 8,760 source hours, leaving the final 24 hours outside the weekly set.

Outage contingencies are separately tested for fuel reduction, DG unavailability, lower RE availability and lower initial BESS SOC (see prior-stage outputs). These controls are deterministic; neither generator repair nor fuel logistics probability has been calibrated.

## 6. Performance indicators and economic limitations

For a demand tier `j`, **scenario Energy Not Served** is

\[ ENS_j=\sum_{t\in outage}(P^{req}_{j,t}-P^{served}_{j,t})\Delta t, \]

and **Critical Load Energy Autonomy** is

\[ EA_{critical}=1-\frac{ENS_{critical}}{\sum_{t\in outage}P^{req}_{critical,t}\Delta t}. \]

Each simulated run additionally records total ENS (all tiers), diesel consumed/remaining litres, stationary BESS end SOC, available critical energy, EV departures completed/missed (dynamic subset), physical residuals and illustrative up-front CAPEX. An EA of 100% for an hourly study does not prove uninterrupted voltage/frequency or UPS transfer continuity.

For the 52 weekly windows, report **mean, median, 90th percentile, worst-window ENS**, worst-window critical EA and **count of windows with nonzero critical ENS**. These are *descriptive conditional counterfactual statistics*, not failure probabilities or EENS. A probability-weighted EENS requires justified outage/repair/fuel replenishment probabilities and appropriate scenario weighting. CAPEX values are explicitly assumption-based (see `week7/outage_sensitivity.py`, `COSTS`) and do not constitute HOMER NPC, LCOE, lifecycle OPEX or an economic optimum.

## 7. Validation evidence hierarchy: WP0/WP4 T02/T17

1. **File integrity:** SHA-256 verification of all 166 frozen original source files (user source and Week7 original archive).
2. **Software regression:** original Python tests plus the Week7 and Stage3 physical checks, including individual EV SOC ledger, conservation, fuel inventory and power bounds.
3. **Existing native software evidence:** historical controlled DG-only 24 h matched-parameter comparison documented in `validation/diesel-energy-accounting/native-mdt-diesel-comparison.csv`. Its scope must not be broadened.
4. **New MDT/HOMER cross-validation:** not performed. Generic 8,760-hour profile + 108-case manifest + exact archived DG fuel-curve export and a provenance-gated comparison tool are supplied for subsequent independently saved native projects and outputs. The comparison tool can detect numerical disagreements but cannot authenticate a claimed native export solely from a CSV.
5. **Real asset validation:** out of scope without approved field data and equipment studies.

## 8. Ethical, engineering and scope limitations

No MOD survey, vehicle routes, classified facility data, exact military operating requirements, or vendor-certified bidirectional interface has been represented. The emergency V2B/V2M scenarios S2/S3 remain **conditional / future work** until vehicle hardware, bidirectional chargers, anti-islanding isolation, grid-forming interface, source protection, reserve controls and costs are evidenced. Future work also includes voltage/frequency stability, black-start, network constraints, non-hourly UPS transfer behaviour and statistically defensible outage-risk estimation.

**Drafting note:** Replace assumed equipment and fleet references with supervisor-approved, permissible sources before dissertation submission. Figures must retain the caption **Exploratory Python simulation; not native MDT/HOMER Pro or site-validated**. No final capacity recommendation is supported at this stage.
