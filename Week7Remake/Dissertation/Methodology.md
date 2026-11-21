# Methodology

This chapter records the implemented LC1 methods and checks against preserved inputs and outputs. Equation numbers refer to this draft. Bracketed identifiers resolve to the [Evidence Register](Evidence_Register.csv), which records the source commit, file digest and applicability. Numerical illustrations use frozen case definitions. The outputs answer questions about hourly electrical service under modelled conditions.

## 2.1 Research design and electrical boundaries

LC1 represents a hypothetical **120-person operational support camp** in the Sennybridge area of Powys. The facility schedule groups accommodation and ventilation, command and communications, medical refrigeration, catering, water services, workshops, laundry, lighting and vehicle charging. The facility quantities, duty schedules, use factors and electrical ratings are research assumptions. A surveyed installation, measured camp demand and an authorised military load-priority specification were unavailable. The supervisor is asked to agree the representative population, the composition of the Critical tier and the interpretation of critical service [SYS01–SYS02].

The plant boundary is an idealised AC energy bus linking photovoltaic (PV) and wind resource inputs, a diesel generator (DG), an AC-connected stationary battery energy storage system (BESS) through a power conversion system (PCS), and an ideal energy-limited uninterruptible power supply (UPS). Vehicle batteries are tracked on each vehicle's DC side and interact with the bus through unidirectional AC charging. The AC grid is available in the normal-year model only, subject to the modelled feeder import limit. An outage study makes grid import and export zero. Simulated service is allocated in the order Critical (`c4isr` in the code), Auxiliary and EV charging. Critical covers command, dedicated cooling, medical and perimeter security.

Inputs span the **8,760 consecutive one-hour intervals of 2025**, from 1 January at 00:00 to the end of the interval labelled 31 December at 23:00. Labels mark interval starts on fixed NASA POWER Local Solar Time (LST). The location is approximately 51.95° N, 3.57° W and falls in the zero-offset POWER longitude band. Civil-time BST changes are outside the schedule. The meteorological year is a dated resource input, not a typical-year dataset or a time history of camp operations. Grid-connected economics and islanded service have separate run configurations and accounting boundaries [SYS03, REN01]. [Site design basis](../week7/site_design_basis.md) · [Weather provenance](../docs/WEATHER_DATA_AUDIT.md) · [Functional architecture](../research_evidence/islanded_architecture_gate/figures/architecture_overview.svg)

### 2.1.1 Long-term climate reference and representativeness

LC1 uses the archived NASA POWER 2025 hourly fields for its hypothetical Sennybridge-area study point. The Met Office **Sennybridge No 2** 1991–2020 station normals provide long-term climate context. The station catalogue gives 52.0629° N, 3.61341° W, and the Met Office UK Synop list records a station elevation of 307 m for WMO station 03507. The NASA file describes 245.39 m as the MERRA-2 grid-cell mean elevation, rather than a surveyed elevation at the LC1 study point [CLM01, CLM05–CLM06]. [Met Office station table](https://www.metoffice.gov.uk/research/climate/maps-and-data/location-specific-long-term-averages/gcm2jvb2g) · [Station catalogue](https://www.metoffice.gov.uk/research/climate/maps-and-data/uk-synoptic-and-climate-stations) · [UK Synop station list](https://www.metoffice.gov.uk/api/assets/file/uk_synop_station_list_jul24pdf?prefix=assets)

| Attribute | Met Office Sennybridge No 2 | NASA POWER at the LC1 study point |
| --- | --- | --- |
| Coverage and location | 1991–2020 station normals, 52.0629° N, 3.61341° W | 2025 fixed LST, 8,760 hourly gridded records, 51.95° N, 3.57° W |
| Elevation basis | 307 m above sea level, UK Synop station list | 245.39 m, MERRA-2 grid-cell mean |
| Annual temperature | 8.49 °C, calculated as (12.19 + 4.79)/2 from the published annual mean daily maximum and minimum | 9.707916 °C, arithmetic mean of hourly 2 m air temperature (T2M) |
| Annual mean wind at 10 m | 6.83 knots, equivalent to 3.513656 m/s | 4.977205 m/s, arithmetic mean of hourly WS10M |

The station annual normals also report 63.64 air-frost days and 1,565.62 mm rainfall [CLM03]. The wind conversion uses 0.5144444444 m/s per knot [CLM04]. The midpoint of the station's mean daily maximum and minimum is a temperature proxy. It is also used for each monthly comparison. Differences in reference period, location, spatial resolution, terrain and wind exposure make the two datasets suitable for contextual comparison only. The temperature difference is not evidence of a 2025 anomaly at the station, and the wind difference does not test turbine performance. The pack has no 2025 hourly station series and reports no station sunshine normal. The existing hourly weather inputs are retained because monthly normals cannot reproduce their hourly timing or extremes [CLM02–CLM06]. Contains public sector information licensed under the Open Government Licence v3.0. [Station monthly normals](../research_evidence/climate_reference_validation/SENNYBRIDGE_MET_OFFICE_1991_2020_MONTHLY.csv) · [Monthly comparison](../research_evidence/climate_reference_validation/SENNYBRIDGE_MET_OFFICE_VS_NASA_2025_MONTHLY.csv) · [Source record](../research_evidence/climate_reference_validation/CLIMATE_SOURCE_RECORD.md) · [Import checks](../research_evidence/README.md#sennybridge-climate-reference)

## 2.2 Electricity-demand model

At each hourly label $t$, `scheduled_hours` provides the Boolean schedule $S_i(t)$ for equipment group $i$. The active electrical load and annual energy are

$$
P_i(t)=P_{i,\mathrm{rated}} U_{i,s} S_i(t),\qquad
E_{i,s}=\sum_{t=0}^{8759} P_i(t)\Delta t
=P_{i,\mathrm{rated}} U_{i,s} H_i. \tag{1}
$$

Here $P_{i,\mathrm{rated}}$ is the aggregate installed or assumed operating rating in kW, $U_{i,s}$ is the dimensionless utilisation factor for demand case $s$, $H_i=\sum_t S_i(t)\Delta t$ is the annual energised time in hours and $\Delta t=1$ h. Critical uses $U=1$ in all three cases. Auxiliary uses 0.65 (Low), 0.80 (Central) and 1.00 (High). All hour ranges below include the first label and exclude the last. The calendar assigns each hour to its own month even across a midnight span.

| Equipment group | Tier | Rating (kW) | Schedule in 2025 LST | Central $U$ | $H_i$ (h) | Central $P_\mathrm{rated} U H_i$ (kWh) | Evidence |
| --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| Command and communications | Critical | 25 | Continuous | 1.00 | 8,760 | 219,000 | L01 |
| Medical and emergency refrigeration | Critical | 4 | Continuous | 1.00 | 8,760 | 35,040 | L02 |
| Dedicated C4ISR cooling | Critical | 6 | Continuous | 1.00 | 8,760 | 52,560 | L03 |
| Perimeter security lighting | Critical | 6 | 18:00–06:00 | 1.00 | 4,380 | 26,280 | L04 |
| Accommodation ventilation | Auxiliary | 12 | Continuous | 0.80 | 8,760 | 84,096 | L05 |
| Accommodation sockets | Auxiliary | 18 | 06:00–09:00, 17:00–02:00 | 0.80 | 4,380 | 63,072 | L06 |
| Accommodation lighting | Auxiliary | 12 | 06:00–09:00, 18:00–23:00 | 0.80 | 2,920 | 28,032 | L07 |
| Electric catering | Auxiliary | 26 | 06:00–09:00, 11:00–14:00, 17:00–19:00 | 0.80 | 2,920 | 60,736 | L08 |
| Workshops and maintenance | Auxiliary | 18 | 09:00–15:00 weekdays | 0.80 | 1,566 | 22,550.4 | L09 |
| Laundry | Auxiliary | 12 | 13:00–17:00 | 0.80 | 1,460 | 14,016 | L10 |
| Water pumping and treatment | Auxiliary | 8 | 07:00–10:00, 18:00–21:00 | 0.80 | 2,190 | 14,016 | L11 |
| Common-area lighting | Auxiliary | 8 | 07:00–12:00, 16:00–21:00 | 0.80 | 3,650 | 23,360 | L12 |
| Electric space heating | Auxiliary | 30 | Oct–Apr 17:00–05:00, May/Sep 18:00–02:00 | 0.80 | 3,032 | 72,768 | L13 |
| Non-critical summer cooling | Auxiliary | 6 | Jun–Aug 10:00–20:00 | 0.80 | 920 | 4,416 | L14 |

Command contributes $25(24)=600$ kWh/day, refrigeration $4(24)=96$ kWh/day, dedicated cooling $6(24)=144$ kWh/day, and night security lighting $6(12)=72$ kWh/day. Consequently, the tier uses $600+96+144+72=912$ kWh/day and $912(365)=332{,}880$ kWh/year. Demand is 35 kW outside the lighting schedule and 41 kW during it. The designation Critical includes services beyond communications.

As a scheduling cross-check, weekdays contribute $261(6)=1{,}566$ workshop hours, giving $18(0.80)(1{,}566)=22{,}550.4$ kWh. Space heating has $212(12)+61(8)=3{,}032$ eligible hours. The assumed 30 kW rating becomes 24 kW when energised in Central, hence $30(0.80)(3{,}032)=72{,}768$ kWh electrical. Summer cooling spans $92(10)=920$ h and contributes $6(0.80)(920)=4{,}416$ kWh. General accommodation ventilation represents fans only. The preserved electricity budget includes heating once and leaves domestic hot water without a separate equipment row. The table is checked by summing each saved end-use column and comparing with the separate equipment calculation. The assigned ratings, schedules and service groupings remain provisional [SYS02, L01–L15]. [Equipment assumptions](../week7/config/equipment.csv) · [Schedule implementation](../week7/load_model.py) · [Central equipment ledger](../week7/outputs/central_equipment_calculations.csv)

## 2.3 Total, monthly and annual electricity

For the baseline accounting input, $P_{\mathrm{tot}}(t)=P_{\mathrm{crit}}(t)+P_{\mathrm{aux}}(t)+P_{\mathrm{EV,AC}}(t)$, where each is the mean kW of the same hour. Monthly energy in kWh is $E_m=\sum_{t\in m}P_{\mathrm{tot}}(t)\Delta t$. Daily mean in kWh/day is $E_m/d_m$, where $d_m$ is the number of calendar days. Annual energy is $\sum_m E_m$, annual daily mean is $E_{\mathrm{yr}}/365$, mean power is $E_{\mathrm{yr}}/8{,}760$ and peak is $\max_t P_{\mathrm{tot}}(t)$ in kW. The peak is a one-hour mean and does not resolve momentary load.

| Case | Critical (kWh/yr) | Auxiliary (kWh/yr) | EV AC from serialised hourly file (kWh/yr) | Total (kWh/yr) | Mean (kWh/day) | Mean (kW) | Peak (kW) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Low | 332,880 | 314,488.2 | 35,166.956465 | 682,535.156465 | 1,869.959333 | 77.914972 | 172.143478 |
| Central | 332,880 | 387,062.4 | 43,958.695464 | 763,901.095464 | 2,092.879714 | 87.203321 | 195.091304 |
| High | 332,880 | 483,828.0 | 54,948.369552 | 871,656.369552 | 2,388.099643 | 99.504152 | 225.000000 |

For Central January, $67{,}474.639114/31=2{,}176.601262$ kWh/day. Summing twelve stored monthly values reproduces $763{,}901.095464$ kWh. The annual component check gives $332{,}880+387{,}062.4+43{,}958.695464=763{,}901.095464$ kWh. Dividing by 365 and 8,760 gives 2,092.8797136 kWh/day and 87.2033214 kW respectively. The first stored maximum is 195.091304 kW on 2 January at 18:00. All 26,280 hourly records were checked against their timestamps and tier and end-use sums. Separate monthly sums agree with annual energy in each case. Unrounded scheduler AC charging is reported separately in Section 2.5 [DEM01–DEM04]. [Monthly energy and daily means](../research_evidence/temperature_driven_load_calibration/monthly_baseline.csv) · [Frozen Central hourly demand](../week7/outputs/central_load_8760.csv)

## 2.4 External military electricity comparator

Gildea et al. (2017), U.S. Army technical report NATICK/TR-17/011, reports a simulated 300-person temperate Ready State camp. Its DCAM result is 4,091 kWh/day (printed p. 14, Table 4 and pp. 17–18, Tables 7–8). Thus $4{,}091/300=13.636667$ kWh/person/day. The temperate reference uses some direct-fuel heating. EV charging is absent from the identified electrical end uses. Table 7 subdivides the same demand by function as Table 8 by equipment. In Table 7, 510 kWh/day is the functional Command and Control (C2) group. This is a different boundary from the equipment-level communications item (344 kWh/day in Table 8) or LC1's entire Critical tier [LIT01, LIT02].

For total source electricity $E_{300}$, functional C2 energy $E_\mathrm{C2}$, and scale ratio $s=120/300$, the fixed-C2 proxy is

$$
E_\mathrm{proxy}=E_\mathrm{C2}+s(E_{300}-E_\mathrm{C2})+
\frac{E_{\mathrm{EV,AC,Central}}}{365}. \tag{2}
$$

The residual $4{,}091-510=3{,}581$ kWh/day scales to $1{,}432.4$ kWh/day. Restoring C2 once gives $1{,}942.4$ kWh/day. Adding $43{,}958.695464/365=120.434782$ kWh/day of LC1 scheduled EV charging gives $2{,}062.834782$ kWh/day. Relative to this proxy, Central is $100(2{,}092.879714-2{,}062.834782)/2{,}062.834782=1.45649\%$ higher. A purely per-capita scaling gives $4{,}091(0.4)=1{,}636.4$ kWh/day before EV addition and illustrates sensitivity to the scaling rule. Using the LC1 Critical tier as a second C2 term would double count part of the comparator. No hourly profile was derived from the proxy. Differences in functional boundary, weather, heating fuel and end uses preclude an accuracy estimate from percentage closeness. The sprint records restricted access to the report PDF, verification against the original report tables via a public mirror, and preservation of the corroborating Army presentation. [Source and page locators](../research_evidence/load_evidence_sprint/LOAD_EVIDENCE_AUDIT.md) · [Recorded arithmetic](../research_evidence/load_evidence_sprint/SCENARIO_COMPARISON.csv) · [Original Army report text, public mirror](https://www.academia.edu/108894857/Sustainability_Logistics_Basing_Science_and_Technology_Objective_Demonstration_50_300_1000_Person_Base_Camp_Analysis_of_FY12_Operationally_Relevant_Technical_Baseline)

## 2.5 Vehicle demand, charge limits and mission feedback

Seven generic archetypes were instantiated as four light utility vehicles, two medium logistics vehicles and one mobile emergency support vehicle. Ratings, schedules and traction intensities are provisional simulation assumptions. The fleet has a 70 kW shared AC charging limit, 92% AC-to-DC efficiency, and 90% initial and target SOC for each vehicle. Low, Central and High multiply route distance by 0.80, 1.00 and 1.25 respectively [EV01–EV04].

| Vehicle | Capacity (kWh DC) | Traction (kWh DC/km) | Charger (kW AC) | Reserve | Central trip (km) | Departure–return LST | Mission days |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| LU01 | 75 | 0.25 | 11 | 20% | 60 | 07:00–17:00 | Mon–Fri |
| LU02 | 75 | 0.25 | 11 | 20% | 65 | 08:00–18:00 | Mon–Fri |
| LU03 | 75 | 0.25 | 11 | 20% | 50 | 09:00–17:00 | Mon–Fri |
| LU04 | 75 | 0.25 | 11 | 20% | 55 | 07:00–19:00 | Mon–Fri |
| ML01 | 160 | 0.65 | 22 | 25% | 95 | 06:00–17:00 | Mon, Tue, Thu, Fri |
| ML02 | 160 | 0.65 | 22 | 25% | 90 | 07:00–18:00 | Mon, Wed, Thu, Fri |
| ME01 | 100 | 0.35 | 11 | 45% | 20 | 10:00–12:00 | Sun |

For vehicle $j$ with capacity $C_j$ in kWh DC, dimensionless SOC $s_j$, reserve $s_{j,\mathrm{res}}$, distance $D_j$ in km, distance multiplier $m$ and traction rate $e_j$ in kWh DC/km, a scheduled departure is feasible if
$$
E_{\mathrm{trip},j}=mD_je_j,\qquad
C_js_j \ge E_{\mathrm{trip},j}+C_j s_{j,\mathrm{res}}. \tag{3}
$$
The implementation records progression as return, departure, then charging. It debits the stored trip energy on return and permits charging only while connected. For each connected vehicle in next-departure order, ties broken by vehicle ID, hourly AC request is limited by the smallest of $P_{j,\mathrm{rated}}\Delta t$, the remaining fleet allowance and $C_j\max(0,s_\mathrm{target}-s_j)/\eta_\mathrm{EV}$. $E_{j,\mathrm{DC}}=\eta_\mathrm{EV}E_{j,\mathrm{AC,served}}$ and $s_{j,\mathrm{next}}=s_j+E_{j,\mathrm{DC}}/C_j$ across charging. Across return, subtract $E_\mathrm{trip}/C_j$. The limit uses the one-hour implementation.

LU01 illustrates the fleet ledger. A 60 km Central trip consumes $60(0.25)=15$ kWh DC. The departure needs at least $15+0.20(75)=30$ kWh DC. From 90% SOC, stored energy is 67.5 kWh and post-return SOC is $52.5/75=0.70$. Full replenishment requires $15/0.92=16.304348$ kWh AC. With full feeder headroom, one hour at 11 kW delivers 10.12 kWh DC, raises SOC to $62.62/75=0.834933$, and leaves 5.304348 kWh AC for a subsequent hour.

Counting the configured weekdays during 2025 gives 261 trips per light vehicle, 208 for ML01, 209 for ML02 and 52 for ME01. Thus $4(261)+208+209+52=1{,}513$. Using the distances and traction rates above, $261(15+16.25+12.5+13.75)+208(61.75)+209(58.5)+52(7)=40{,}442$ kWh DC. With the same fleet start/end SOC, $40{,}442/0.92=43{,}958.695652$ kWh AC before hourly CSV rounding. The serialised one-hour powers sum to 43,958.695464 kWh, a **0.000188 kWh** reporting difference traceable to rounding. The demand-total calculation uses that serialised sum. The normal schedule performs all departures under full charging service.

The early site design record describes an EV feedback gap. Subsequent `EVFleetFeedback` resolves it at the hourly model boundary. Before a sampled outage the vehicles are preconditioned with fully served charging to the selected start, then only delivered AC changes SOC. The controller records unmet charging requests as charging ENS; part of a deferred request can recur in later hours. Missed missions require an actual failed departure reserve check and are counted separately from AC energy shortfalls. The Stage 3 capacity sweep preserves static planned EV demand and offers no new feedback readiness claim; Stage 4 paired cases and the HDH outage comparison explicitly use the dynamic variant where indicated. Vehicle discharge is for propulsion only [EV03–EV05]. [Vehicle assumptions](../week7/config/fleet.csv) · [Annual Central scheduler summary](../week7/outputs/central_summary.json) · [Dynamic implementation](../week7/nextstage/fleet_feedback.py) · [Stage 4 fleet outcomes](../week7/stage4/outputs/stage4_13start_EV_mission_feedback.csv)

## 2.6 Renewable resource input and dispatched energy

NASA POWER provides hourly GHI based on the CERES product, and 10 m and 50 m wind speeds and 2 m temperature based on MERRA-2. These inputs represent gridded meteorological estimates for the study point. The dispatcher reads the preprocessed, indexed v6 output series $\phi_\mathrm{PV}(t)$ and $\phi_\mathrm{W}(t)$. These are dimensionless available AC powers normalised by DC PV nameplate and rated wind capacity respectively. The implementation multiplies each hourly ratio by its own capacity $K$ in kW:
$$
P_{\mathrm{PV,av}}(t)=K_{\mathrm{PV,DC}}\phi_\mathrm{PV}(t),\qquad
P_{\mathrm{W,av}}(t)=K_\mathrm{W}\phi_\mathrm{W}(t),\qquad
E_\mathrm{av}=\sum_t P_\mathrm{av}(t)\Delta t. \tag{4}
$$

The archived preprocessing script calls the Erbs decomposition for diffuse and direct estimates, isotropic plane-of-array transposition with a fixed south-facing 35° tilt and 0.20 albedo, SAPM cell-temperature calculation, PVWatts DC and PVWatts inverter conversion. It evaluates solar geometry at the interval midpoint, excludes plane-of-array irradiance with the sun below the horizon, applies 10% aggregate DC losses and models a 1.1 DC/AC capacity ratio with 96% nominal inverter efficiency. The resulting AC clipping limit is $1/1.1=0.909091$ kW AC per kW DC. Those are the archived preprocessing functions and settings. The dispatcher itself neither fits a PV model nor ingests GHI, DNI or DHI. DNI and DHI are intermediate model estimates [REN01, REN04].

The wind preprocessor calculates the log-speed interpolation weight $q=\ln(40/10)/\ln(50/10)$. For positive inputs $v_{10}$ and $v_{50}$ in m/s, $v_{40}=v_{10}(v_{50}/v_{10})^q$. Otherwise it uses $v_{50}(40/50)^{0.143}$. It linearly interpolates the NREL DW100 tabulated curve $P_\mathrm{DW100}(v_{40})$, normalises by 100 kW, takes zero outside the tabulated curve and for speeds below 3 or at/above 25 m/s, and multiplies by $1-0.07$ for losses. The reference curve is used for capacity scaling. Site shear, terrain, icing and machine power are unvalidated [REN03–REN04]. [Weather and preprocessing provenance](../docs/WEATHER_DATA_AUDIT.md) · [NASA POWER hourly documentation](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/) · [NREL source curve](https://natlabrockies.github.io/turbine-models/2019COE_DW100_100kW_27.6.html)

As a dispatch input check, at index 1 (1 January 00:00 LST), PV ratio is zero and wind ratio is 0.8749163921250537. The original 50 kW wind assumption gives $50(0.8749163921250537)=43.7458196063$ kW, which matches the saved islanded trace for that hour. Both resource arrays have one record per interval. Integrating provides 1,104.660346 kWh per kW DC of PV and 3,759.634456 kWh per rated kW of wind. At 50/50 kW this represents 55,233.017320 and 187,981.722780 kWh of potential annual electricity before curtailment. The ratios have annual means of approximately 0.12610 and 0.42918. The latter is a power ratio; it does not carry wind-speed units.

If the assumed AC reference permits renewable admission, usable power is allocated to requested load and eligible charging, with remaining islanded surplus curtailed. For reported curtailment $P_{\mathrm{curt}}$ and positive available renewable power $P_{\mathrm{RE,av}}$, the S3-v2 ledger apportions curtailment to PV in the ratio $P_{\mathrm{PV,av}}/P_{\mathrm{RE,av}}$ and assigns the balance to wind. If the AC reference assumption is off, the renewable input is unavailable to islanded dispatch and is accounted as curtailed. Used energy therefore differs from the pre-dispatch resource total. The PV inverter boundary is independent of the stationary BESS's 90 kW PCS [REN02–REN05]. [PV series](../data/v6_solar_pu_index_value.csv) · [Wind series](../data/v6_wind_pu_index_value.csv) · [Dispatch ledger](../week7/nextstage/dispatcher.py)

## 2.7 BESS energy accounting and PCS

The reference outage arrangement uses $C=300$ kWh DC, a bidirectional 90 kW AC PCS, initial SOC 0.70, physical floor 0.10, ordinary reserve 0.30 and maximum 0.90. Capacity screening also uses 450 and 600 kWh, with the same PCS rating. Both efficiencies are 0.8944, giving a modelled round-trip conversion fraction $0.8944^2=0.79995136$ before operational constraints. All SOC values are fractions of the nominal DC capacity. A floor of 0.30 protects ordinary operating reserve; the model may explicitly permit discharge down to 0.10 for contingency support [BAT01].

For SOC $s$, ceiling $s_\mathrm{max}$, selected floor $s_f$, charge and discharge offers $P^\mathrm{offer}$ in kW AC, and interval or subinterval length $\delta$ in h, the power bounds before any control-direction exclusions are
$$
\begin{aligned}
P_{\mathrm{ch,AC}}&=\max\!\left(0,\min\!\left[P^\mathrm{offer}_\mathrm{ch},P_\mathrm{PCS},
\frac{(s_\mathrm{max}-s)C}{\eta_\mathrm{ch}\delta}\right]\right),\\
P_{\mathrm{dis,AC}}&=\max\!\left(0,\min\!\left[P^\mathrm{offer}_\mathrm{dis},P_\mathrm{PCS},
\frac{\max(0,s-s_f)C\eta_\mathrm{dis}}{\delta}\right]\right),\\
C(s_{t+1}-s_t)&=\eta_\mathrm{ch}E_{\mathrm{ch,AC}}-
\frac{E_{\mathrm{dis,AC}}}{\eta_\mathrm{dis}} .
\end{aligned}\tag{5}
$$
Here $E=P\delta$ in kWh, and $\eta_\mathrm{ch}$ and $\eta_\mathrm{dis}$ are dimensionless. Losses are $E_{\mathrm{ch,AC}}(1-\eta_\mathrm{ch})+E_{\mathrm{dis,AC}}(1/\eta_\mathrm{dis}-1)$. The control selection and fixed PCS power constrain usable delivery separately from stored energy.

The Stage 7 `BESS_1H_DISCHARGE` fixture deliberately uses different values: 100 kWh DC, 40 kW AC, $\eta_\mathrm{dis}=0.90$, initial SOC 0.70, an ordinary discharge stop at 0.30 (physical floor 0.10), a 50 kW request and a one-hour interval. The DC inventory above floor is $(0.70-0.30)(100)=40$ kWh. Its AC delivery is $40(0.90)=36$ kWh, less than either power-derived bound of 40 or 50 kWh. The residual Critical demand is $50-36=14$ kWh, the discharge loss is $36/0.90-36=4$ kWh, and the resulting SOC is $0.70-40/100=0.30$. All four metrics pass the closed-form comparison. This verifies the fixture's accounting and limiter behaviour with known inputs. The fixture is separate from the 300 kWh reference plant. In its companion charge case, 60 kWh renewable surplus and a 40 kW PCS yield 40 kWh AC charge, 36 kWh DC addition, final SOC 0.66 and 20 kWh curtailment [BAT02–BAT03]. [Battery implementation](../models/core/components.py) · [Fixture inputs](../week7/stage7/outputs/stage7_component_fixture_inputs.csv) · [Closed-form comparison](../week7/stage7/outputs/stage7_closed_form_benchmark.csv)

The original S3 screen quarantined operating cases involving opposing BESS directions within one hourly control interval during DG fuel exhaustion. S3-v2 retains the original files and anticipates the fuel-limited off-tail within the hour, preventing DG-to-BESS charging before the BESS may need to discharge in that interval. It routes supported DG surplus to the bounded dump sink when charging is disallowed. It retains the SOC, PCS, fuel balance and no-simultaneous-direction checks. The correction is evaluated prospectively in separate outputs [DSP01–DSP03]. [Quarantined issue records](../week7/outputs/capacity_quarantined_issue_details.json) · [Corrected controller](../week7/nextstage/dispatcher.py)

## 2.8 DG output, fuel and inventory

The principal revised islanded cases assume one 100 kW DG and a modelled 25% minimum utilisation. When enabled, fuelled and commanded with positive request $P_\mathrm{req}$, its on-segment power is
$$
P_\mathrm{on}=\min(P_\mathrm{rated},\max[P_\mathrm{req},0.25P_\mathrm{rated}]). \tag{6}
$$
The unit starts from off in the reference case. The startup delay is 1 h from the start command, can advance across intervals, and yields no energy during the delay. The numerical delay is a control assumption. Once started, operation during an hour can be truncated by the fuel inventory. The implementation models zero fuel during off/startup, without a separately identified physical start or running-idle fuel use [DG01].

For the islanded research model, `ResearchDiesel` selects `MDT_DERIVED`. Let $f=P_\mathrm{on}/P_\mathrm{rated}$. For bounding points $f_i,f_{i+1}$ from $0.25,0.50,0.75,1.00$ with specific consumption values $s_i=0.104,0.082,0.077,0.074$ US gal/kWh respectively, the fuel law is
$$
s(f)=s_i+(s_{i+1}-s_i)\frac{f-f_i}{f_{i+1}-f_i},\qquad
\dot F=3.785411784\,P_\mathrm{on}s(f)\quad[\mathrm{L/h}]. \tag{7}
$$
The catalogue's zero point, 0.1095 US gal/h, has different dimensions and is excluded from interpolation. Positive output below the 25% domain is rejected. At 60 kW the interpolation weight is $(0.60-0.50)/(0.75-0.50)=0.40$, so $s=0.082+(0.077-0.082)(0.40)=0.080$ US gal/kWh. At sustained output the rate is $60(0.080)(3.785411784)=18.1699765632$ L/h. At 50 kW, the tabulated value yields 15.5201883144 L/h. The archived curve has evidence against a separate restricted DG-only comparison in the 38–65 kW range. The entire catalogue and vehicle-independent site applicability are not established [DG02].

At the start of an interval, an optional delivery $L_\mathrm{requested}$ is admitted as $A=\min(L_\mathrm{requested},\max(0,F_\mathrm{tank}-F_t))$ in litres. Main reference windows assume no delivery and start with a 2,000 L stock in a 2,000 L tank. For eligible operating time $d_\mathrm{eligible}$ after any startup delay, $d_\mathrm{on}=\min(d_\mathrm{eligible},(F_t+A)/\dot F)$, then $F_{t+1}=F_t+A-\dot F d_\mathrm{on}$ apart from numerical round-off. Generator electricity is $P_\mathrm{on}d_\mathrm{on}$; mean kW for the hour is this energy divided by $\Delta t$. This event handling prevents negative inventory and limits generated energy before allocation. DG surplus can supply BESS charge where authorised by the model. Remaining surplus is bounded by the assumed 25 kW dump capability, with an inadmissible operating point raised when the controller has no supported sink. Fuel is evaluated from **gross on-segment power**, including electricity later charged or dumped [DG01–DG03].

By comparison, the independent Stage 7 `DG_24H_FUEL_LIMIT` fixture uses a deliberately constant $0.25$ L/kWh, zero startup delay, 50 kW demand and 125 L initial fuel. Its rate is 12.5 L/h, giving $125/12.5=10$ h of operation, $50(10)=500$ kWh generated and $(24-10)50=700$ kWh Critical ENS. The Stage 7 startup fixture uses 40 kW with a 1 h initial delay and sufficient fuel, giving $23(40)=920$ kWh generated, $0.25(920)=230$ L and $40(1)=40$ kWh Critical ENS. The stored tests match these values. Both use a simplified fuel law and are not checks of equation (7) [DG04]. [Fuel interpolation](../models/islanded/fuel_models.py) · [Catalogue definition](../models/islanded/config/fuel-models.json) · [Contingency tank rule](../week7/stage4/contingency.py) · [Analytical metrics](../week7/stage7/outputs/stage7_closed_form_benchmark.csv)

## 2.9 Hourly dispatch and conservation checks

The reference revised islanded model uses `instrumented_s3` in the Next Stage dispatcher. Each source's available service is assigned through the same sequential tier allocator. Renewables first serve Critical, Auxiliary and requested EV charging. The controller tests whether the residual can be covered within the PCS and energy above the operating reserve. If uncommitted and that test is met, BESS covers the residual without consuming reserve. If SOC is at/below the reserve or available non-reserve power is insufficient, the DG is committed. A running commitment is cleared when the deficit disappears, or when the stop threshold (0.60 in reference S3-v2) and BESS coverage criterion are both met. The code computes a DG command only for the remaining gap. The on/off time segments preserve generator output and partial-hour fuel exhaustion. During commitment, BESS may support remaining load into its physical floor, and the ideal UPS supplies only unmet Critical load within its power and residual inventory. Excess DG may charge BESS under the permitted direction rule, then goes to a supported dump sink. Excess renewables may charge BESS when there has been no discharge, after which surplus is curtailed in islanding. The anticipatory check in Section 2.7 distinguishes S3-v2 from the historical S3 implementation [DSP01–DSP03].

In AC kWh over a given interval, conserving the common active-energy boundary requires
$$
E_{\mathrm{PV,used}}+E_{\mathrm{W,used}}+E_{\mathrm{DG,gross}}+
E_{\mathrm{grid,in}}+E_{\mathrm{BESS,dis}}+E_{\mathrm{UPS,dis}}
=\sum_{j\in\{\mathrm{crit,aux,EV}\}}E_{j,\mathrm{served}}
+E_{\mathrm{BESS,ch}}+E_{\mathrm{UPS,ch}}+E_{\mathrm{grid,out}}+E_{\mathrm{DG,dump}}. \tag{8}
$$
Renewable availability satisfies $E_\mathrm{RE,av}=E_\mathrm{RE,used}+E_\mathrm{RE,curt}$. Each variable $E$ is its labelled energy transfer over the interval. Curtailment is excluded from the used term, and unserved energy is kept on the demand ledger. Diesel destinations in the audited S3-v2 path satisfy $E_{\mathrm{DG,gross}}=E_{\mathrm{DG,to\,load}}+E_{\mathrm{DG,to\,BESS}}+E_{\mathrm{DG,dump}}$; `dg_to_ups_kw` is zero for this path. DG-to-BESS energy is already part of gross generation and AC charge and is not added as a second source.

In the saved Original winter trace at hour 0, wind 43.7458196063 and BESS 45.2541803937 kW supply 89.0000000000 kWh over one hour. Critical service is 41 kWh and Auxiliary service 48 kWh. DG, UPS, PV, EV, grid and charging terms are zero. The independent stored-trace audit reports a maximum AC residual below $2.843\times10^{-14}$ kWh and battery residual below $2.132\times10^{-14}$ kWh in this 168 h case. It separately reconciles DG destinations, fuel and UPS inventory. These checks demonstrate numerical accounting; the hour resolves neither source transfer nor voltage/frequency behaviour [DSP04, VAL03]. [Winter plant trace](../week7/nextstage/outputs/winter_168h_original_equipment_plant_trace.csv) · [Independent winter audit](../research_evidence/islanded_architecture_gate/PRESERVATION_AND_TEST_REPORT.md)

The separate Stage 6 normal-year implementation routes renewables then BESS then bounded grid import to load and curtails unallocated renewable surplus after charging. It assigns service in the same tier order, runs with dynamic EV requests, and uses neither routine DG supply nor UPS backup. Main cases assume zero export. During the final 48 h it raises the reserve to the initial 70% target and allows supplemental grid charging within unused feeder and PCS headroom when loads are fully covered. The numerical terminal rule and PV/BESS budget are separate from the off-grid controller [EC01, EC06]. [Annual normal-year dispatcher](../week7/stage6/annual_grid.py)

## 2.10 Resilience metrics and experiment design

For tier $j$, $P_{j,\mathrm{req}}$ is scheduled or dynamically requested mean power and $P_{j,\mathrm{served}}$ its supplied mean power. Accumulate kWh across the selected $T$ hours:
$$
\mathrm{ENS}_j=\sum_{t\in T}\max(0,P_{j,\mathrm{req}}(t)-P_{j,\mathrm{served}}(t))\Delta t,\qquad
\mathrm{ENS}_\mathrm{total}=\mathrm{ENS}_\mathrm{crit}+\mathrm{ENS}_\mathrm{aux}+\mathrm{ENS}_\mathrm{EV}. \tag{9}
$$
With positive Critical requested energy $E_{\mathrm{crit,req}}$, the saved Critical Energy Autonomy percentage is
$$
\mathrm{EA}_\mathrm{crit}=100\left(1-\frac{\mathrm{ENS}_\mathrm{crit}}{E_{\mathrm{crit,req}}}\right). \tag{10}
$$
Critical requested energy includes all four Critical services and the denominator is the same for the paired Original/HDH window, as reshaping leaves Critical demand unchanged. $E_{\mathrm{crit,req}}=912,\ 2{,}736,\ 6{,}384$ kWh for the January 24/72/168 h windows. For Original 168 h, $100(1-259.5777377315485/6{,}384)=95.933933\%$. Any corresponding total service fraction would use all contemporaneous requested energy, including that run's EV requests. The selected main results report tier and Total ENS and Critical EA. Total Energy Autonomy is not inferred as a separate headline measure. Annual requested-service deficits in Stage 6 can include recurring EV charging requests and have a different reporting boundary.

Fuel consumed is $\sum \dot F\,d_\mathrm{on}$ in L; it is also initial inventory plus accepted deliveries minus final inventory. Final BESS SOC is the last saved end-of-hour stock fraction. Where reported in Stage 4 and the paired HDH tests, minimum SOC uses the minimum of recorded hourly terminal states over the window. A mission-readiness fraction is $N_\mathrm{completed}/N_\mathrm{opportunities}$ when the denominator is positive, with missed count $N_\mathrm{opportunities}-N_\mathrm{completed}$. A 168 h Original January run completes $28/29=96.5517\%$ of scheduled opportunities. This status cannot be read from total EV charging shortfall alone.

The four-season experiments start on 1 January, 1 April, 1 July and 1 October 2025 in fixed LST. The 24, 72 and 168 h cases share a start and the shorter durations are nested within the longest. Each independent run is initialised to its specified settings. Stage 3 extends this to 52 starts $h_i=168i,\ i=0,\dots,51$ on the same weather year, with separate initialisation for each duration and candidate. It uses static Central EV requests under S3-v2, 70% initial stationary SOC and 2,000 L fuel with no routine resupply. Stages 4–5 use paired deterministic fuel, dispatch and DG availability scenarios, including a separately labelled dynamic fleet subset. The HDH comparison uses the January nested windows with dynamic EV logic for both profiles. Window means, empirical sample quantiles and shortfall counts are descriptive over these sampled inputs. No event probability, EENS, loss-of-load probability or field mission failure probability is estimated [OUT01–OUT04]. [Seasonal cases](../week7/nextstage/outputs/seasonal_nine_candidates_24_72_168h.csv) · [Weekly sampling code](../week7/stage3/weekly_scan.py) · [Deterministic weekly metrics](../week7/stage3/outputs/weekly_52_starts_summary.csv)

## 2.11 Synthetic heating-degree-hour sensitivity

The [long-term station normals](#211-long-term-climate-reference-and-representativeness) provide background climate context. This sensitivity retains the original 8,760 hourly NASA POWER T2M values. The 14.5, 15.5 and 16.5 °C assumptions, the redistribution in equation (11) and the energy target remain as defined below [CLM05–CLM06].

The frozen Original profile has 24 kW Central electric space heating when the calendar schedule enables it. Prior temperature calibration aligned the existing NASA POWER outdoor T2M and looked for whole-year empirical data with separated electrical heating and a matching archetype. Available external heat-pump examples did not identify a defensible transfer coefficient for this camp. The HDH experiment therefore varies **when the existing electricity is used**, with no additional heating energy and no inferred building thermal coefficient [HDH01–HDH04].

For assumed balance temperature $T_b$ in °C, outdoor $T_o(t)$ in °C and eligible heating schedule flag $I_t$, define
$$
\mathrm{HDH}_t=(T_b-T_o(t))_+ \Delta t,\qquad
w_t=I_t\frac{\mathrm{HDH}_t}{\Delta t},\qquad
P_{\mathrm{heat,B}}(t)=\min(P_\mathrm{cap},\alpha w_t). \tag{11}
$$
$\mathrm{HDH}$ has units °C·h, $w_t$ has units °C, $P_\mathrm{cap}=30$ kW is the assumed installed electrical rating, and $\alpha$ is a weight normalisation in kW/°C. The flag restricts use to Original permitted hours with no summer cooling. It preserves other inputs. The three uncalibrated balance temperatures are 14.5, 15.5 and 16.5°C. The 15.5°C setting uses the documented UK degree-day reporting convention as a sensitivity centre, with no claim to a building-specific balance point.

The algorithm first requires $P_\mathrm{cap}\Delta t\#\{w_t>0\}\ge E_\mathrm{heat,A}$, where $E_\mathrm{heat,A}=72{,}768$ kWh. It orders positive weights descending. With remaining target $R$ and sum of remaining weights $W$, $\alpha=R/(\Delta t W)$. If the largest remaining hour would exceed $P_\mathrm{cap}$, fix it at the cap, replace $R$ by $R-P_\mathrm{cap}\Delta t$, exclude its weight and repeat. Here the code implicitly uses $\Delta t=1$ h and stores power to 12 decimal places. When the largest remaining weight fits, the common scale satisfies the capped annual constraint. The 15.5°C case has 3,004 positive-weight hours and $30(3{,}004)=90{,}120$ kWh feasible capacity, giving $90{,}120-72{,}768=17{,}352$ kWh of headroom. The 1,397 hours at the 30 kW cap allocate $1{,}397(30)=41{,}910$ kWh. The remaining $30{,}858$ kWh is allocated across positive uncapped weights by the saved $\alpha=3.233279581553395$ kW/°C.

The reassigned total is $P_\mathrm{B}=P_\mathrm{A}-P_{\mathrm{heat,A}}+P_{\mathrm{heat,B}}$; it leaves the other 13 infrastructure categories and the normal-year planned EV profile unchanged. For 1 January at 00:00, the aligned archived T2M and saved profile give 9.43°C. $w=15.5-9.43=6.07$°C, giving $P_{\mathrm{heat,B}}=19.626007060029$ kW and $P_\mathrm{B}=89-24+19.626007060029=84.626007060029$ kW. The archived NASA source, `data/temp.csv` and the HDH table can be aligned on year, month, day and hour. The normalisation does not model internal gains, a building envelope, a COP, thermal output or measured heating response [HDH01–HDH04].

For each month and end use, the method remains $E_{m}=\sum_{t\in m}P(t)\Delta t$, divided by $d_m$ for daily mean. The monthly Original and HDH 15.5°C space-heating values are shown to two decimal places. The retained monthly total electricity series is linked below.

| Month | Original heating (kWh electric) | HDH 15.5°C heating (kWh electric) |
| --- | ---: | ---: |
| Jan | 8,928.00 | 10,944.87 |
| Feb | 8,064.00 | 9,676.84 |
| Mar | 8,928.00 | 10,254.24 |
| Apr | 8,640.00 | 8,524.44 |
| May | 5,952.00 | 3,882.14 |
| Jun | 0.00 | 0.00 |
| Jul | 0.00 | 0.00 |
| Aug | 0.00 | 0.00 |
| Sep | 5,760.00 | 3,676.91 |
| Oct | 8,928.00 | 7,622.65 |
| Nov | 8,640.00 | 8,192.72 |
| Dec | 8,928.00 | 9,993.19 |

For example, January contains $31(12)$ Original heating hours. $31(12)(24)=8{,}928$ kWh. Summing the 744 adjusted hourly powers gives 10,944.874790 kWh; the 2,016.874790 kWh difference transfers directly to January total electricity, from 67,474.639114 to 69,491.513904 kWh. Across all months, 72,768 kWh electric heating and 763,901.095464 kWh total electricity are conserved within $10^{-7}$ kWh; 4,416 kWh of summer cooling is unchanged. Using exact stored peaks, $100(201.091304-195.091304)/195.091304=3.075483\%$ (approximately 3.08%). The first peak remains 2 January 2025 at 18:00 LST in Original and all three HDH cases. Annual energy equality was checked after serialisation [HDH02–HDH04, HDH06]. [HDH implementation](../research_evidence/hdh_heating_sensitivity/study.py) · [Hourly audit data](../research_evidence/hdh_heating_sensitivity/HDH_HOURLY_8760.csv) · [Monthly comparisons](../research_evidence/hdh_heating_sensitivity/MONTHLY_ENERGY_COMPARISON.csv) · [Annual summary](../research_evidence/hdh_heating_sensitivity/HDH_SCENARIO_SUMMARY.csv)

## 2.12 Paired HDH resilience comparison

The existing experiment reuses the same 2025 winter resource slices and a single 1 January 00:00 LST outage start with 24, 72 and 168 h horizons. Both treatments use 50 kW PV, 50 kW wind, 100 kW DG, 300 kWh BESS, 90 kW PCS, initial BESS SOC 70%, initial fleet SOC 90% and 2,000 L diesel with no delivery. Both use `MDT_DERIVED` and the identical S3-v2 controller and dynamic EV-feedback logic. Only the infrastructure heating shape changes. Post-dispatch EV requests may consequently diverge through SOC feedback. The replay of Original against the preserved dynamic winter trace was verified within the study's $10^{-7}$ tolerance for reported energy balances and matched outcomes [OUT03, HDH05].

| Duration (h) | Critical ENS A → B (kWh) | Auxiliary ENS A → B (kWh) | EV request ENS A → B (kWh AC) | Total ENS A → B (kWh) | Diesel A → B (L) | Critical EA A → B (%) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 24 | 0 → 0 | 0 → 0 | 3.104 → 7.013 | 3.104 → 7.013 | 363.943 → 367.843 | 100 → 100 |
| 72 | 0 → 0 | 78.686 → 132.760 | 995.016 → 1,092.364 | 1,073.702 → 1,225.124 | 1,414.783 → 1,437.394 | 100 → 100 |
| 168 | 259.578 → 277.516 | 2,823.643 → 3,121.634 | 3,472.181 → 3,699.788 | 6,555.401 → 7,098.937 | 2,000 → 2,000 | 95.934 → 95.653 |

For positive baseline quantity $X_A$, the relative change is $100(X_B-X_A)/X_A$; for baseline zero, report the absolute difference only. For 168 h Total ENS, the exact stored difference is 543.535918525461 kWh. Dividing by 6,555.4014352668 kWh and multiplying by 100 gives **8.291421%**. Critical ENS increases by approximately 17.938 kWh, decreasing Critical EA by 0.280989 percentage points. Both cases end at 0.10 stationary SOC and have 28 completed departures out of 29. At 24 and 72 h the zero Critical ENS and 100% Critical EA are hourly energy-accounting outcomes. This paired case establishes sensitivity to load timing with finite fuel under the modelled conditions. It does not infer winter population reliability or weather-year response [HDH05]. [Paired source results and residuals](../research_evidence/hdh_heating_sensitivity/RESILIENCE_COMPARISON.csv) · [HDH validation report](../research_evidence/hdh_heating_sensitivity/VALIDATION_REPORT.md)

## 2.13 Finite capacity and cost–resilience comparisons

The capacity screen crosses three **equal PV/wind nameplate pairs** (50/50, 75/75 and 100/100 kW) with three stationary BESS capacities (300, 450 and 600 kWh). It holds the 90 kW PCS and 100 kW DG fixed. The indicative capital cost $K$ in GBP for capacities $p$ kW PV, $w$ kW wind and $b$ kWh DC BESS is
$$
K=1257p+4000w+400b+250(90)+30{,}000+20{,}000+60{,}000+8{,}000+3(2000). \tag{12}
$$
The fixed amounts cover DG, UPS, common site provision and fixed tank cost; the final term is variable tank capacity at £3/L. The PCS boundary is separate from the DC battery cost. Initial working diesel inventory is outside CAPEX. For 100/100/300, the variable resources and storage contribute £125,700, £400,000 and £120,000, and the remaining equipment/civils/tank contribute £146,500. CAPEX is £792,200. A valid candidate is non-dominated in the finite screen if no other eligible candidate is no worse in CAPEX and Total ENS and strictly better in at least one, allowing $10^{-8}$ comparison tolerance in the implementation. In the repaired static-EV winter screen, 100/100/450 gives 226.562 kWh Total ENS, compared with 312.995 kWh at 100/100/600. Both have zero Critical ENS there, so the latter is dominated in that window on the two objectives. On the 52-start mean, 100/100/600 instead yields 719.0 kWh against 767.0 kWh at 450 kWh. Both have Critical shortfall in 15 of 52 windows. The control and finite sample can change rankings, so a single-window frontier is not a global optimisation result [CAP01–CAP04]. [Illustrative CAPEX and Pareto implementation](../week7/outage_sensitivity.py) · [Corrected 168 h screen](../week7/nextstage/outputs/nine_candidate_v2_168h.csv) · [Weekly results](../week7/stage3/outputs/weekly_52_starts_summary.csv)

The Stage 6 normal-year matrix crosses those nine candidates with three demand cases and three hypothetical import limits (100, 150 and 250 kW). Stage 7 replays the cash flows of the 27 runs with the 250 kW limit and equivalent fulfilled hourly requested service. The 52-start outage metric remains separate. Stage 5 earlier models a separate conditional cash scenario involving one hypothetical 168 h event per year, illustrative fuel delivery costs and omitted annual grid operation. Combining the two cash models risks overlap and is outside the retained accounting [EC01–EC05].

For grid import $Q_\mathrm{in}$ and export $Q_\mathrm{out}$ in kWh/year, assumed unit prices $p_\mathrm{in}$ and $p_\mathrm{out}$ in GBP/kWh, annual grid bill is $G=0.24Q_\mathrm{in}-0.05Q_\mathrm{out}+365(2)$ at default prices and £2/day standing charge. Export is zero in the main runs. If $K$ is CAPEX, $O=0.025K$ fixed annual O&M, $F=2{,}000(1.35)$ the notional fuel inventory value, $R_y$ the scheduled replacement cash in GBP in year $y$, and $r=0.03$ real discount, the selected present value is
$$
\mathrm{PV}_\mathrm{selected}=K+F+\sum_{y=1}^{20}\frac{O+G+R_y}{(1+r)^y}
-\frac{F}{(1+r)^{20}}. \tag{13}
$$
The recurring normal-year grid ledger repeats 2025. Year 12 replaces 70% of the modelled BESS DC and PCS costs and 65% of UPS cost. Year 15 replaces 80% of the DG cost. The final fuel value is recovered as a modelled credit, with no equipment salvage. Cash inputs are illustrative real 2026 GBP.

For Central 100/100/300 at 250 kW, the saved 313,611.33827387897 kWh import and zero exports give $G=0.24(313{,}611.33827387897)+730=75{,}996.72118573094$ GBP. Fixed O&M is $O=0.025(792{,}200)=19{,}805$ GBP and year 0 is $792{,}200+2{,}700=794{,}900$ GBP. Year 1 cash of £95,801.72118573094 discounted by $1/1.03$ is £93,011.37979197179. Year 12 replacements are $0.70(120{,}000+22{,}500)+0.65(20{,}000)=112{,}750$ GBP. Year 15 replacements are $0.80(30{,}000)=24{,}000$ GBP. In year 20, deducting £2,700 gives £93,101.72118573094 before discount. The 21 recorded discounted rows sum to **£2,313,178.0422220556** (within floating-point rounding). Across 27 cases Stage 7 reports a maximum Stage 6 versus Stage 7 present-value difference of $9.3133\times10^{-10}$ GBP. The replay verifies arithmetic, not tariff validity, prices or asset lifetimes. The selected streams omit outage costs, grid upgrades, degradation outside replacements and probability-linked loss. The output is a cash proxy with limited scope rather than a validated full NPC [EC02–EC04]. [Economic assumptions](../models/grid_connected/config/economic-parameters.json) · [Annual grid studies](../week7/stage6/outputs/stage6_81_annual_grid_cases.csv) · [Year-by-year ledger](../week7/stage7/outputs/stage7_selected_costs_year_by_year_567.csv) · [Reconciliation](../week7/stage7/outputs/stage7_27_service_matched_cash_replay.csv)

## 2.14 Validation design and interpretation

| Level | Existing method and result | Permitted inference |
| --- | --- | --- |
| 1. Preservation and regression | Stage 7 regression 143/143; original full baseline 166/166 (public subset 142); Stage 7 output manifest 16 records; Initial Draft independent tests 53/53 | Software behaviour remains consistent on the tested cases and checked files retain their hashes |
| 2. Independent analytical fixtures | Six component fixtures, 22/22 metrics pass against closed-form references; 75 fixture-hour inputs. The tolerance is metric-dependent, $\max(10^{-8},10^{-9}\lvert x_\mathrm{ref}\rvert)$ in each metric's unit | Reproducible component arithmetic within the specified initial states and test inputs |
| 3. Independent ledger reconciliation | Stage 7 checks two 8,760 h normal-year traces and three 168 h outage traces. Separate winter audit covers the 168 h HDH Original trace. AC/DC balances, stored inventories, continuity by row, tier service, fuel and DG destinations are checked where recorded | Numerical conservation and state consistency for the saved simulations |
| 4. Native software comparison | Genuine saved MDT 1.4.2513.0 component tests cover DG, BESS and available-power PV/wind fixtures. Status is assessed separately for aggregate values, event/physical state and visible fixed 1 h steps. Stage 7 HOMER files are handoff inputs; equivalent run and full-cost reconciliation remain outstanding | Scoped comparison only on matching component case definitions and exported evidence |
| 5. Physical equipment and site | No Sennybridge meter or commissioned system test available. Electrical topology, grid forming, transfer and protection are unverified | No claim of physical continuity, equipment qualification or field validation |

The DG-only native fixture matches 1 h aggregate energy/fuel and 24 h aggregate results (500 kWh generated, 125 L consumed, 700 kWh Critical ENS). The 24 h visible clock reports 10 h and 14 h intervals. The observed event boundary coincides with the analytically inferred depletion at 10 h. Direct tank telemetry and the internal solver grid were not established. Fixed visible 1 h output remains STRICT FAIL. Any exact-overlap hourly projection from those states is derived. BESS B1/B2/B3 all pass their aggregate tests; B1/B2 event/state is inconclusive and final SOC is derived, with visible 1 h clock PASS. B3 reserve cutoff at 3.5776 h is accepted for that fixture; fixed 1 h FAIL. PV/wind P1 and W1 pass the declared available-power comparisons, and P2/W2 aggregate and visible clock pass while event/state remains inconclusive. The separate 2 h PV observability test has a passing aggregate and visible clock, with direct hourly state inconclusive. These fixtures do not test irradiance-to-power or wind-speed-to-power physics [VAL02–VAL07, VAL11–VAL12].

D1 integrated execution remains **NO-GO / NOT RUN**. Installed MDT minimum DG output is 40% (40 kW) versus the locked Python 25% (25 kW), and native controls do not establish separate 10% physical floor and 30% reserve equivalence. Evidence for exact DG-first, priority, clock and direct SOC or fuel inventory semantics is incomplete. The locked event time **1.192533333 h** is a Python reference. There is no integrated native MOF and no D1 numerical comparison. Conditional D1A in the audit is a proposal scoped to a single operating region, with execution subject to supervisor direction and observability [VAL08]. [Stage 7 method and tolerances](../week7/stage7/benchmark.py) · [Independent trace results](../week7/stage7/outputs/stage7_readonly_hourly_trace_audit.csv) · [Native scope](../week8/README.md) · [D1 gate](../week8/t17_dg_bess_native_v1/D1_GATE_STATUS.json)

The energy model assumes an energised AC reference. UPS ideal capacity is $30(15/60)=7.5$ kWh, with power limited to 30 kW. The instantaneous source or transfer availability needed to serve the entire 35–41 kW Critical tier was not verified. The approximate 1 h model DG delay begins at the start command. In the saved winter trace DG first generates at hour index 3, with prior energy service represented through other sources. Electrical continuity in the interval between UPS capability and DG availability depends on undocumented physical source, switching and protection performance. An hourly Critical ENS of zero therefore establishes full hourly service in the model subject to its assumptions. It cannot prove continuity, short interruption limits or frequency/voltage stability [VAL09–VAL10]. [Islanded architecture audit](../research_evidence/islanded_architecture_gate/ISLANDED_ARCHITECTURE_AUDIT.md) · [Continuity timeline](../research_evidence/islanded_architecture_gate/POWER_CONTINUITY_TIMELINE.csv)

## 2.15 Limitations, source hierarchy and reproducibility

Use the committed equipment assumptions and saved hourly demand for reported load values. Use the actual S3-v2 or Stage 6 entry points to identify controller settings, and label static scheduled or dynamic EV operation in every result. Use the cryptographic evidence register and existing preservation manifests for file identity. Treat outputs of other case studies as scoped literature proxies. Study occupancy, end uses, BESS limits, EV fleet, rates and fuel schedules are provisional. The single dated weather year and finite deterministic start sampling do not establish long-term weather or outage probabilities. Component failure data and equipment-matched failure/repair parameters are absent from the production experiments. Heating is energy-neutral reshaping with no field thermal calibration. Native controller non-equivalence, GFM, transient electrical behaviour and complete economic optimisation remain unresolved [SYS01, EV01, HDH01, VAL08–VAL10].

The Git evidence base is `3a585167f49f226d88bac82e529c5ccdcc98f1b3`. Earlier local research commits are recorded in the [workspace README](README.md). Historical assets remain outside the writing folder. Where an archive input is not published, the register provides an archive-relative locator, a SHA-256 where the file was accessible and the corresponding tracked provenance document. Definitive hardware, tariff and measured-demand statements require appropriate source verification. Important open decisions about study scope are recorded in the [supervisor review](Supervisor_Review.md).

For read-only checks in the established Python 3.12 environment, the regression invocation from each project version is `python -B -m pytest -q -p no:cacheprovider` with `PYTHONDONTWRITEBYTECODE=1`. From Week7Remake, `python -B week7/audit/check_preservation.py` checks the public subset; the established `--archive-root` option points to the frozen archive for the full check. For numerical reproduction in this draft, summation and independent ledger comparisons use saved rows and the equations above. A separate copy is needed for commands that regenerate outputs. These methods establish reproducible modelled energy quantities and the sensitivity of those quantities to the documented inputs. Claims about commissioned continuity, probabilistic resilience and a final design require additional evidence.
