
# Supervisor review | EN3400 LC1

**Research aim.** Assess how renewable availability, stationary storage, diesel stock and demand timing affect hourly electricity service for a representative 120-person operational support camp. The Sennybridge-area setting provides a dated temperate resource year. The study uses hypothetical demand, equipment and operating assumptions, with separate normal-year and islanded assessments. This note requests agreement on the dissertation boundary and evidence standard.

## Completed work and material findings

| Study question | Retained finding | Evidence boundary |
| --- | --- | --- |
| Scale and seasonality of electricity | Central uses 763.90 MWh annually, 2,092.88 kWh/day and a 195.09 kW hourly peak. Low/High span 682.54–871.66 MWh/year. The Critical tier totals 332.88 MWh/year. | Transparent scheduled demand. The US Army fixed-C2 arithmetic comparator gives 2,062.83 kWh/day, with different heating and service boundaries. The 1.46% difference does not measure prediction accuracy. |
| Winter continuity and storage | Original dynamic January Critical ENS is 0, 0 and 259.58 kWh over 24, 72 and 168 h. The longest case uses 2,000 L. At hour 0 wind and BESS supply the demand in the energy ledger. | The model assumes an AC reference. The ideal 30 kW UPS cannot by itself cover the entire 35–41 kW tier. Physical feeder transfer, ride-through and DG synchronisation are unverified. |
| Heating timing | The synthetic 15.5°C HDH case retains 72,768 kWh of heating and the same annual total. Peak rises by 6 kW, and 168 h Total ENS rises from 6,555.40 to 7,098.94 kWh (+8.29%). Critical EA falls from 95.93% to 95.65%. | A paired sensitivity with the same plant, initial fuel and dynamic EV rules. The HDH curve is energy-neutral and lacks measured building calibration. |
| Cost and service | For 100/100 kW PV/wind at a hypothetical 250 kW feeder, going from 300 to 600 kWh BESS raises the selected 20-year discounted cash proxy from £2.313m to £2.492m. Separate 52-start mean 168 h Total ENS falls from about 846 to 719 kWh. | Conditional comparison across a finite design set. The annual cash proxy does not include outage costs or probabilistic expected loss. |

Numerical assurance includes the 143-test regression, six closed-form fixtures with 22 metric passes, independent AC/DC and fuel accounting, and source preservation. Genuine Stage 8 native MDT outputs support scoped component claims. The locked integrated D1 fixture remains **NO-GO / NOT RUN**. The native DG minimum is 40% versus Python's 25%, and equivalence for the BESS physical SOC floor and reserve has not been established. Direct telemetry is incomplete for several component events. HOMER import inputs exist, but no equivalent validated full economic run is available. [Validation boundaries](Methodology.md#214-validation-design-and-interpretation) · [D1 gate](../research_evidence/islanded_architecture_gate/VALIDATION_GATE_DECISION.md)

## Four figures for the review meeting

| Figure | Review purpose |
| --- | --- |
| 01 | Inspect the assumed AC reference and the functional load and UPS boundaries. [Architecture SVG](../research_evidence/dissertation_figures/01_System_Architecture/01_islanded_energy_architecture.svg) |
| 03 | Review the scheduled end-use contributions and winter load assumptions. [Monthly electricity PDF](../research_evidence/dissertation_figures/02_Load_Modelling/03_monthly_electricity.pdf) |
| 07 | Compare deterministic Critical ENS, Total ENS, Critical EA and fuel over the three outage durations. [Winter results PDF](../research_evidence/dissertation_figures/05_Outage_Resilience/07_winter_outage_energy_service.pdf) |
| 10 | Agree how the component evidence and integrated gap should be described. [Native scope PDF](../research_evidence/dissertation_figures/08_Model_Validation/10_native_validation_scope.pdf) |

## Decisions requested

1. **Representative case.** Approve the 120-person conceptual boundary, fuel stock, end-use inventory and mixed evidence basis, or identify a replacement design envelope and permissible data.
2. **Critical service.** Confirm which command, cooling, medical and security services belong in the Critical tier, and whether the dissertation criterion should be expressed as hourly ENS/EA, a maximum interruption time, or both. No field interruption threshold is assumed.
3. **Physical validation scope.** Determine whether commissioned or laboratory evidence for Grid-forming control, Black-start and UPS transfer is required for EN3400. If required, agree what equipment access and measurement evidence would count.
4. **Native D1 scope.** Decide whether reporting the strict D1 gate and existing component evidence is sufficient. A limited 1 h follow-on is a separate scope choice conditional on equivalent settings, observable signals and explicit approval.
5. **Economic scope.** Decide whether the conditional service-matched 20-year cash proxy meets the project requirement or whether a fully documented HOMER or equivalent NPC study must be added.

The [writing roadmap](Writing_Roadmap.md) assigns drafting priorities to these decisions. Course submission format and assessment requirements should be checked against the authorised Cardiff brief.
