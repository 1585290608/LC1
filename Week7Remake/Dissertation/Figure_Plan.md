# Dissertation figure plan

Eleven figures are proposed for the main text, followed by four appendix figures. Captions use provisional numbering. The figure library supplies the vector masters and PNG derivatives where available, plus the three original Critical 0/1/2 PNGs. [Selection and quality report](../research_evidence/dissertation_figures/FIGURE_QA_REPORT.md)

## 1 System architecture

### 01 Conceptual islanded electrical architecture

Introduce the modelled active-power boundary and identify the unverified AC reference and transfer interfaces.

**Figure X (proposed 01).** Functional energy flow for the hypothetical LC1 Central winter case (2025 source local solar time, LST). Solid links indicate implemented active-power accounting and the dashed utility link identifies the conceptual point of common coupling (PCC). The numerical AC reference is assumed. This figure does not describe commissioned switchgear, measured transfer times, grid-forming capability or electrical protection.

Evidence class **CONCEPTUAL**. Central winter 2025 LST. [SVG](../research_evidence/dissertation_figures/01_System_Architecture/01_islanded_energy_architecture.svg) · [architecture_overview.svg](../research_evidence/islanded_architecture_gate/figures/architecture_overview.svg)

## 2 Load modelling

### 02 Annual electricity by end use

Summarise the annual end-use mix and quantify the scale of the Central electricity demand.

**Figure X (proposed 02).** Annual AC electricity demand for the hypothetical 120-person camp, Central baseline, 2025 LST (763.90 MWh). Shares are calculated against the annual total across 14 infrastructure categories and EV charging. The chart shows modelled demand using the study equipment and schedules.

Evidence class **PYTHON_SIMULATION**. Original Central 2025 LST. [PDF](../research_evidence/dissertation_figures/02_Load_Modelling/02_annual_electricity.pdf) · [PNG](../research_evidence/dissertation_figures/02_Load_Modelling/02_annual_electricity.png) · [monthly_baseline.csv](../research_evidence/temperature_driven_load_calibration/monthly_baseline.csv)

### 03 Monthly electricity by end use

Show when each end use contributes energy throughout the year, using the same total as Figure 02.

**Figure X (proposed 03).** Monthly Central electricity consumption by end use in fixed 2025 LST (MWh per calendar month). Each segment integrates the saved one-hour mean electrical power. The end uses are identical to those in the annual breakdown and the monthly totals sum to 763.901 MWh. Heating and cooling follow the original calendar schedules.

Evidence class **PYTHON_SIMULATION**. Original Central 2025 LST. [PDF](../research_evidence/dissertation_figures/02_Load_Modelling/03_monthly_electricity.pdf) · [PNG](../research_evidence/dissertation_figures/02_Load_Modelling/03_monthly_electricity.png) · [monthly_baseline.csv](../research_evidence/temperature_driven_load_calibration/monthly_baseline.csv)

### 03a Monthly electricity composition by load group

Use the 100% view to show seasonal changes in composition alongside Figure 03.

**Figure X (proposed 03a).** Monthly shares of Central electricity demand in fixed 2025 LST. Each segment is its group's energy divided by the total electricity for that calendar month, including EV charging and other Auxiliary electricity. Critical 0 is command and communications (600 kWh/day), Critical 1 combines dedicated C4ISR cooling and medical refrigeration (240 kWh/day), and Critical 2 is security lighting (72 kWh/day). The three groups are a presentation breakdown of the existing modelled Critical tier. The dispatch priority remains the same.

Evidence class **PYTHON_SIMULATION** (presentation of saved outputs). Original Central 2025 LST. [PNG](../research_evidence/dissertation_figures/02_Load_Modelling/LC1_monthly_critical012_share_percent.png) · [Supporting CSV](../research_evidence/dissertation_figures/02_Load_Modelling/data/LC1_monthly_critical012_breakdown.csv)

### 04 Low, Central and High demand

Show how the modelling assumptions span the Low, Central and High daily demand cases.

**Figure X (proposed 04).** Mean daily electricity demand by month for the frozen Low, Central and High study cases (2025 LST). Monthly electricity is divided by the number of days in each month. The three scenarios vary auxiliary utilisation and illustrative EV journey assumptions. They describe research demand bounds rather than statistical confidence intervals.

Evidence class **PYTHON_SIMULATION**. Frozen Low, Central and High 2025 LST. [PDF](../research_evidence/dissertation_figures/02_Load_Modelling/04_low_central_high.pdf) · [PNG](../research_evidence/dissertation_figures/02_Load_Modelling/04_low_central_high.png) · [monthly_baseline.csv](../research_evidence/temperature_driven_load_calibration/monthly_baseline.csv)

## 3 PV and wind resources

### 05 2025 available PV and wind resources

Describe seasonal available output before dispatch, with the two normalisation boundaries stated explicitly.

**Figure X (proposed 05).** Monthly mean available PV and wind power from the frozen v6 resource profiles, aligned to the 2025 Sennybridge-area NASA POWER weather year. PV is stated per kW DC nameplate at the AC output boundary and wind per kW rated at the AC boundary. These are modelled resource-availability profiles before dispatch or curtailment.

Evidence class **PYTHON_MODELLED_METEOROLOGICAL_DERIVATIVE**. v6 derived available output, 2025 LST. [PDF](../research_evidence/dissertation_figures/03_PV_Wind_Resources/05_available_pv_wind_2025.pdf) · [PNG](../research_evidence/dissertation_figures/03_PV_Wind_Resources/05_available_pv_wind_2025.png) · [v6_solar_pu_index_value.csv](../data/v6_solar_pu_index_value.csv) · [v6_wind_pu_index_value.csv](../data/v6_wind_pu_index_value.csv)

## 4 Dispatch and storage

### 06 Diesel and battery dispatch during islanding

Show why hourly DG commitment and BESS discharge can be discussed even though the source of the AC reference is unverified.

**Figure X (proposed 06).** Generator active power, signed BESS AC power and BESS state of charge (SOC) during the first 48 h of the saved Original Central winter case (1–2 January 2025 LST, S3-v2). Positive BESS power denotes discharge and negative power denotes charge. Reference settings are 50 kW PV, 50 kW wind, 100 kW DG, 300 kWh DC BESS and 90 kW AC PCS. Grid-forming and transfer dynamics are assumed outside this numerical dispatch.

Evidence class **PYTHON_SIMULATION**. Original Central, S3-v2, 1–2 Jan 2025 LST. [PDF](../research_evidence/dissertation_figures/04_BESS_Diesel_Dispatch/06_dg_bess_dispatch.pdf) · [PNG](../research_evidence/dissertation_figures/04_BESS_Diesel_Dispatch/06_dg_bess_dispatch.png) · [winter_168h_original_equipment_plant_trace.csv](../week7/nextstage/outputs/winter_168h_original_equipment_plant_trace.csv)

## 5 Outage resilience

### 07 Winter outage sensitivity to heating timing

Keep 24, 72 and 168 h Critical ENS, total ENS, Critical Energy Autonomy and diesel together so their denominators and units stay clear.

**Figure X (proposed 07).** Critical and total Energy Not Served (ENS, kWh), Critical Energy Autonomy (EA, percentage of critical demand served), and diesel consumed (L) across three nested outages starting 1 January 2025 LST. Original and synthetic HDH (15.5°C) retain 72.768 MWh annual heating electricity, identical hardware and dynamic EV feedback. The windows are deterministic. Their energy metrics do not establish uninterrupted power or event probabilities.

Evidence class **PYTHON_SIMULATION**. Original Central vs HDH 15.5°C; 1 Jan 2025 fixed LST; 24/72/168 h. [PDF](../research_evidence/dissertation_figures/05_Outage_Resilience/07_winter_outage_energy_service.pdf) · [PNG](../research_evidence/dissertation_figures/05_Outage_Resilience/07_winter_outage_energy_service.png) · [RESILIENCE_COMPARISON.csv](../research_evidence/hdh_heating_sensitivity/RESILIENCE_COMPARISON.csv)

## 6 Economic analysis

### 08 Normal-year cost and outage energy shortfall

Separate the normal-year cost proxy from the deterministic 168 h outage shortfall across service-matched candidates.

**Figure X (proposed 08).** Normal-year discounted cash proxy over 20 years (£m) versus mean total ENS (MWh) across 52 separately simulated 168 h islanded starts. The nine Stage 6 Central candidates have equivalent normal-year requested service under the assumed 250 kW import cap and reuse the 2025 LST load and weather. Markers distinguish equal PV/wind nameplates and colours distinguish BESS capacity. The cash proxy excludes outage costs and probability weights.

Evidence class **PYTHON_SIMULATION**. Central, Stage 6, fixed 2025 LST, 250 kW assumed limit. [PDF](../research_evidence/dissertation_figures/06_Economic_Analysis/08_cost_resilience_screen.pdf) · [PNG](../research_evidence/dissertation_figures/06_Economic_Analysis/08_cost_resilience_screen.png) · [stage6_central_peacetime_outage_comparison.csv](../week7/stage6/outputs/stage6_central_peacetime_outage_comparison.csv)

## 7 Sensitivity analysis

### 09 Annual heating energy redistributed within 2025

Show how the synthetic 15.5°C HDH setting redistributes the conserved annual heating electricity.

**Figure X (proposed 09).** Space-heating electricity by month for Original Central and the synthetic Heating Degree Hours (HDH) sensitivity (2025 LST). The assumed 15.5°C balance point weights only permitted heating hours. Both series conserve 72.768 MWh of annual heating electricity, with the HDH series capped at 30 kW. No building thermal calibration or field heat-meter observations are used.

Evidence class **PYTHON_SIMULATION**. Central Original vs synthetic HDH, 15.5°C, 2025 LST. [PDF](../research_evidence/dissertation_figures/07_Sensitivity_Analysis/09_hdh_heating_sensitivity.pdf) · [PNG](../research_evidence/dissertation_figures/07_Sensitivity_Analysis/09_hdh_heating_sensitivity.png) · [MONTHLY_ENERGY_COMPARISON.csv](../research_evidence/hdh_heating_sensitivity/MONTHLY_ENERGY_COMPARISON.csv)

## 8 Model validation

### 10 Native MDT component evidence and D1 gate

Close by summarising the native component verdicts by dimension and showing that the integrated D1 experiment remains NOT RUN. Fixed-clock and direct-state verdicts are presented separately.

**Figure X (proposed 10).** Reported acceptance status for the MDT 1.4.2513.0 component fixtures and the locked integrated D1 gate. Aggregate energy, each fixture’s event/state verdict and visible fixed hourly output are scored separately. The DG 24 h event timer agrees while direct tank state remains inconclusive. The 24 h PV/wind tests concern available-power inputs, and B1/B2 end SOC is derived. D1 is NO-GO and the integrated native test was not run.

Evidence class **NATIVE_MDT_EVIDENCE_STATUS**. Stage 8 synthetic component fixtures; MDT 1.4.2513.0; gates 2026. [PDF](../research_evidence/dissertation_figures/08_Model_Validation/10_native_validation_scope.pdf) · [PNG](../research_evidence/dissertation_figures/08_Model_Validation/10_native_validation_scope.png) · [BESS_VALIDATION_STATUS.json](../week8/t17_bess_native_v1/BESS_VALIDATION_STATUS.json) · [PV_WIND_VALIDATION_STATUS.json](../week8/t17_pv_wind_native_v1/PV_WIND_VALIDATION_STATUS.json) · [D1_GATE_STATUS.json](../week8/t17_dg_bess_native_v1/D1_GATE_STATUS.json)

## Appendix

### A01 Original and HDH demand in the winter week

Show the detailed change in timing in the first winter week before dynamic islanded EV feedback.

**Figure A.X (proposed A01).** Mean hourly total electricity over the representative week of 1–7 January 2025 fixed LST, before islanded EV feedback. The synthetic HDH case assumes a 15.5°C balance point and preserves 72.768 MWh of annual heating electricity. The weekly energy may change because the annual constraint redistributes energy between allowed hours and months.

Evidence class **PYTHON_SIMULATION**. Central Original vs synthetic HDH, 15.5°C, 1–7 Jan 2025 LST. [PDF](../research_evidence/dissertation_figures/07_Sensitivity_Analysis/A01_hdh_winter_week.pdf) · [PNG](../research_evidence/dissertation_figures/07_Sensitivity_Analysis/A01_hdh_winter_week.png) · [HDH_HOURLY_8760.csv](../research_evidence/hdh_heating_sensitivity/HDH_HOURLY_8760.csv)

### A02 Dependence on the assumed grid import limit

Support the assumed 250 kW import context for Figure 08 and show the sensitivity to grid capacity.

**Figure A.X (proposed A02).** Annual requested-service shortfall (MWh) versus assumed import capacity for Stage 6 Central and High demand, using 100 kW PV, 100 kW wind, 450 kWh BESS and a 90 kW PCS over 8,760 hours in 2025 LST. Dynamic EV charging requests may recur. The curves describe this numerical service screen and do not establish an approved grid connection or EENS.

Evidence class **PYTHON_SIMULATION**. Stage 6 Central/High, 2025 LST, 100–250 kW, PV/Wind 100/100 kW, BESS 450 kWh, PCS 90 kW. [PDF](../research_evidence/dissertation_figures/07_Sensitivity_Analysis/A02_grid_import_sensitivity.pdf) · [PNG](../research_evidence/dissertation_figures/07_Sensitivity_Analysis/A02_grid_import_sensitivity.png) · [stage6_grid_limit_sweep_14.csv](../week7/stage6/outputs/stage6_grid_limit_sweep_14.csv)

### A03 Monthly Central electricity by load group

Show the corresponding absolute energy in kWh per calendar month.

**Figure A.X (proposed A03).** Monthly Central electricity in fixed 2025 LST (kWh per calendar month), stacked by the three Critical presentation groups, EV charging and other Auxiliary demand. The bar totals reconcile to the frozen monthly demand within 0.0005 kWh at the supplied CSV precision.

Evidence class **PYTHON_SIMULATION** (presentation of saved outputs). Original Central 2025 LST. [PNG](../research_evidence/dissertation_figures/02_Load_Modelling/LC1_monthly_critical012_stacked_kwh.png) · [Supporting CSV](../research_evidence/dissertation_figures/02_Load_Modelling/data/LC1_monthly_critical012_breakdown.csv)

### A04 Monthly electricity within the Critical tier

Show how different month lengths affect the three Critical presentation groups.

**Figure A.X (proposed A04).** Monthly electricity for Critical 0, 1 and 2 under the frozen Central case in fixed 2025 LST. The vertical axis is electricity in kWh per calendar month. The lines vary with month length because each group has a fixed daily schedule. They describe the existing Critical end uses and carry no separate dispatch priorities.

Evidence class **PYTHON_SIMULATION** (presentation of saved outputs). Original Central 2025 LST. [PNG](../research_evidence/dissertation_figures/02_Load_Modelling/LC1_monthly_critical012_lines.png) · [Supporting CSV](../research_evidence/dissertation_figures/02_Load_Modelling/data/LC1_monthly_critical012_breakdown.csv)
