# Results and discussion

## Results

### Event-level cross-validation

The LC1 case study represents a hybrid microgrid serving a 30 kW command, control, communications, computers, intelligence, surveillance and reconnaissance (C4ISR) load, auxiliary demand and EV charging in the Sennybridge area. The D0 load profiles are representative inputs. Full-event energy availability (EA) is served energy divided by required energy for the stated tier. Energy not served (ENS) is the difference between those energies. Each outage below is deterministic.

The controlled diesel-only comparison used constant loads of 30 kW C4ISR, 8 kW auxiliary and 5 kW EV. Across the 24-, 72- and 168-hour events, Sandia MDT and Python agreed on generator output, fuel use and critical service to the reported precision. The 24-hour D0 comparison also agreed when both models used the same input window and catalogue fuel formulation. It produced 1,103.894 kWh from the generator and used 360.842 L. Full-event C4ISR ENS was 0.08333 kWh, consistent with 30 kW unserved for the configured 10 s start delay. [Diesel comparison data](../validation/native-mdt/diesel-parity.csv).

### Hybrid outage service and feeder control

The C2 native feeder model used 75 kW PV, 75 kW wind, 300 kWh nominal storage with a 120 kW power limit, and one available 100 kW diesel generator. The three D0 runs share the same input start at index 24. The model separated auxiliary demand into an essential component capped at 10 kW and an interruptible remainder. Normally closed breakers were placed on the interruptible auxiliary and EV feeders. The three reruns reproduced the archived generator, renewable, battery and fuel event totals and delivered the full required energy to every tier.

| D0 outage (h) | C4ISR supplied (kWh) | All-tier ENS (kWh) | Diesel generation (kWh) | Diesel used (L) |
| ---: | ---: | ---: | ---: | ---: |
| 24 | 720 | 0 | 686.071 | 237.958 |
| 72 | 2,160 | 0 | 1,788.457 | 629.800 |
| 168 | 5,040 | 0 | 2,866.871 | 1,018.107 |

[Native event results](../validation/native-mdt/event-results.csv) · [Per-feeder demand and service](../validation/native-mdt/section-service.csv).

The separate variable-load diesel trial imposed a 78–39–78 kW demand sequence against a 40 kW generator. In the switched case the lowest-load window delivered at least 39.889 kWh to the interruptible auxiliary feeder and 15.889 kWh to EV. These lower bounds follow from the two essential feeders requiring the full 40 kW in the high-load blocks and their combined full-event ENS of 0.111 kWh. Thus the event records establish recovery of lower-tier energy within the low-load window without resolving exact breaker action times.

In the corresponding hybrid stress trial, available diesel capacity was reduced to 40 kW. The direct-feed model gave 11.765 kWh of C4ISR ENS. With independent feeder breakers, C4ISR and both auxiliary sections received their full required energy. The EV feeder carried all 38.551 kWh of remaining ENS. Total ENS increased from 30.588 kWh in the direct-feed model, quantifying the trade-off between protection of the critical load and aggregate service in this trial. In an independent BESS-only trial with 190 kW of demand, the model's sampled maximum active discharge rate was 120 kW. [Case configurations](../validation/native-mdt/case-manifest.csv) · [Event results](../validation/native-mdt/event-results.csv).

### Storage use in MDT and Python

Five instrumented native reruns produced 309 solver intervals and time-of-day SOC distributions. For the C2 D0 cases, modelled time in SOC bins above 80% totalled 23.42, 71.42 and 167.42 h over the 24-, 72- and 168-hour windows respectively. The corresponding values from the aligned V15 Python traces were 0.00, 35.06 and 131.06 h. The native model recorded 67.306 kWh of battery charging and 0.178 kWh of discharge in the 24-hour event. These results show that the native control held the battery in a higher SOC range for more of the tested periods. [SOC distribution comparison](../validation/native-mdt/soc-comparison.csv) · [Native solve intervals](../validation/native-mdt/solver-intervals.csv).

### Conditional grid-connected economics

The separate Draft 3B annual study compared the grid-plus-standby reference P0R with P1, a 50 kWp PV, 50 kW wind, 300 kWh BESS and 90 kW PCS design. The annual hybrid cases used a 70% starting and ending SOC. Under the study's 20-year horizon, 3% real discount rate and £0.24/kWh import assumption, P1 reduced net present cost by about £222,270 in the zero-export case. A scenario with a 20 kW export cap and a £0.05/kWh export price gave a saving of about £223,568 and a sustained discounted payback of 12.24 years. Lower import rates and reduced wind yield reversed the net-present-cost benefit in the published sensitivity cases. These results describe the Draft 3B design under its declared assumptions. [Economic model and assumptions](../validation/grid-connected-economics/) · [Cost and payback results](../validation/grid-connected-economics/discounted-cost-and-payback.csv) · [Sensitivity results](../validation/grid-connected-economics/economic-sensitivity.csv).

## Discussion

### What the combined methodology establishes

Agreement under controlled diesel-only conditions supports the use of the Python model for explicit energy, fuel and load-service accounting. The one-generator case avoids several confounding mechanisms in hybrid operation, including storage conversion, generator commitment, reserve management and available renewable power. The native hybrid reruns add evidence that the C2 topology can serve the tested D0 events and that separate switched paths affect load allocation when power is scarce. Both strands support a scoped model claim. The C2 windows are nested from one source-index start, which limits the range of weather and demand conditions covered by those three native results.

The native Standard controller and the research Python dispatch use different charging logic. The battery results are consistent with those differences and with unequal terminal stored energy. The SOC histogram weights reflect whole-step SOC distributions. The battery-only control reproduced how those weights are allocated when a solver interval spans several clock hours. The 72- and 168-hour histograms also pool corresponding times across days. Direct comparison of per-step battery SOC or switch states will require a simultaneous native state export with the same time origin and interval definitions. [Native evidence and replay scope](../validation/native-mdt/).

### Design implications and remaining evidence

The native priority result supports separating critical and discretionary feeders in the research design. The 10 kW essential auxiliary split remains illustrative until it can be checked against a feeder schedule and measured coincident demand. OpenDSS cases confirm the intended steady-state connectivity of the modelled PCC and load paths. Field acceptance still requires the actual single-line diagram, equipment selection and evidence for PCS paralleling and grid forming, UPS ride-through, and protection and transfer coordination. [Electrical snapshot ledger](../validation/native-mdt/electrical-snapshots.csv).

The C2 design is a supported resilience candidate under the tested conditions. A final capacity decision also depends on contingency coverage, site limits, capital and operating costs and verified equipment characteristics. The annual Draft 3B results describe a distinct grid-connected design and do not establish C2 payback or monetise avoided critical-load interruption. Contracted rates, export permission and installation costs remain required for a site investment decision.
