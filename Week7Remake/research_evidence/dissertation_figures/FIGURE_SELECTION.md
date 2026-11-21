# Dissertation figure selection

Use the vector master for typesetting. Each numbered entry is one figure. The PNG is a second format for the same graphics. Use the same section order in the text and the caption file.

## Main text

| Figure | Section and title | Reason for inclusion | Artwork |
| --- | --- | --- | --- |
| 01 | 1 System architecture · Conceptual islanded electrical architecture | Introduce the modelled active-power boundary and identify the unverified AC reference and transfer interfaces. | [SVG](01_System_Architecture/01_islanded_energy_architecture.svg) |
| 02 | 2 Load modelling · Annual electricity by end use | Summarise the annual end-use mix and quantify the scale of the Central electricity demand. | [PDF](02_Load_Modelling/02_annual_electricity.pdf) · [PNG](02_Load_Modelling/02_annual_electricity.png) |
| 03 | 2 Load modelling · Monthly electricity by end use | Show when each end use contributes energy throughout the year, using the same total as Figure 02. | [PDF](02_Load_Modelling/03_monthly_electricity.pdf) · [PNG](02_Load_Modelling/03_monthly_electricity.png) |
| 04 | 2 Load modelling · Low, Central and High demand | Show how the modelling assumptions span the Low, Central and High daily demand cases. | [PDF](02_Load_Modelling/04_low_central_high.pdf) · [PNG](02_Load_Modelling/04_low_central_high.png) |
| 05 | 3 PV and wind resources · 2025 available PV and wind resources | Describe seasonal available output before dispatch, with the two normalisation boundaries stated explicitly. | [PDF](03_PV_Wind_Resources/05_available_pv_wind_2025.pdf) · [PNG](03_PV_Wind_Resources/05_available_pv_wind_2025.png) |
| 06 | 4 Dispatch and storage · Diesel and battery dispatch during islanding | Show why hourly DG commitment and BESS discharge can be discussed even though the source of the AC reference is unverified. | [PDF](04_BESS_Diesel_Dispatch/06_dg_bess_dispatch.pdf) · [PNG](04_BESS_Diesel_Dispatch/06_dg_bess_dispatch.png) |
| 07 | 5 Outage resilience · Winter outage sensitivity to heating timing | Keep 24, 72 and 168 h Critical ENS, total ENS, Critical Energy Autonomy and diesel together so their denominators and units stay clear. | [PDF](05_Outage_Resilience/07_winter_outage_energy_service.pdf) · [PNG](05_Outage_Resilience/07_winter_outage_energy_service.png) |
| 08 | 6 Economic analysis · Normal-year cost and outage energy shortfall | Separate the normal-year cost proxy from the deterministic 168 h outage shortfall across service-matched candidates. | [PDF](06_Economic_Analysis/08_cost_resilience_screen.pdf) · [PNG](06_Economic_Analysis/08_cost_resilience_screen.png) |
| 09 | 7 Sensitivity analysis · Annual heating energy redistributed within 2025 | Show how the synthetic 15.5°C HDH setting redistributes the conserved annual heating electricity. | [PDF](07_Sensitivity_Analysis/09_hdh_heating_sensitivity.pdf) · [PNG](07_Sensitivity_Analysis/09_hdh_heating_sensitivity.png) |
| 10 | 8 Model validation · Native MDT component evidence and D1 gate | Close by summarising the native component verdicts by dimension and showing that the integrated D1 experiment remains NOT RUN. | [PDF](08_Model_Validation/10_native_validation_scope.pdf) · [PNG](08_Model_Validation/10_native_validation_scope.png) |

## Appendix

- **A01 Original and HDH demand in the winter week.** Show the detailed change in timing in the first winter week before dynamic islanded EV feedback. [PDF](07_Sensitivity_Analysis/A01_hdh_winter_week.pdf) · [PNG](07_Sensitivity_Analysis/A01_hdh_winter_week.png)
- **A02 Dependence on the assumed grid import limit.** Support the assumed 250 kW import context for Figure 08 and show the sensitivity to grid capacity. [PDF](07_Sensitivity_Analysis/A02_grid_import_sensitivity.pdf) · [PNG](07_Sensitivity_Analysis/A02_grid_import_sensitivity.png)

## Duplicate and excluded graphics

- Repository originals and identical archive copies remain searchable by SHA-256 and `duplicate_of`. The `same_stem_format_peer` column connects like-named vector and raster originals. Figure 01 is an `ORIGINAL_COPY` of the new audit artwork. The other selections were regenerated from unchanged tables, with links to the source files in the captions.
- Use Figures 02 and 03 together for end-use composition and timing. Keep the 24/72/168 h, Critical ENS, autonomy and fuel panels together in Figure 07. The Central heating comparison and winter-week comparison supersede stylistically inconsistent companion versions. The earlier daily-temperature and scheduled-HVAC plots are traceable, but require consistent units and a layout review if taken forward.
- Keep the historic Initial Draft economics, generic EV SOC, dispatch and reserve plots as background. They use earlier settings, provisional assumptions or wider study scopes. They need exact source-to-series linkage and a scope review before reuse as quantitative evidence.
- Keep the private P2 discrepancy figures as quarantined diagnostics. The private P3 schematic and UPS/feeder figures concern functional or abstract tests. The vendor extracts, research-page crops and legacy screenshots require permission or reliable provenance before further use. None of those files was copied into this library.

[Searchable inventory](FIGURE_INDEX.csv) · [English captions and data links](FIGURE_CAPTIONS.md) · [Publication QA](FIGURE_QA_REPORT.md)
