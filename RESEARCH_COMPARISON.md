# Initial Draft and Week7Remake

The historical studies and the revised demand scenarios address different design assumptions. Comparisons below use the preserved input bundles and their own validation scopes.

| Topic | Initial Draft | Week7Remake |
| --- | --- | --- |
| Study demand | 402,960 kWh/year, 1,104 kWh/day and 65 kW peak. | Provisional 120-person design basis with fourteen infrastructure load categories. Low, Central and High peaks are 172.1, 195.1 and 225.0 kW. |
| EVs | Fixed 20 kW over four hours per day, 80 kWh/day. | Four light utility, two medium logistics, one mobile emergency support archetype. Vehicle SOC, mission draw, charging windows and reserve gates. Bidirectional export is future work. |
| Equipment and capacity | Original site studies use configurations such as 50 kW PV, 50 kW wind, 100 kW DG, 300 kWh BESS and 90 kW PCS. The separate published native C2 fixture uses 75/75 kW PV/wind and 120 kW PCS. | Exploratory PV/wind and storage sizing sensitivities under revised demand, with explicit 90 kW PCS, SOC reserve and finite diesel stock. Historical capacities need reassessment when peak and energy rise. |
| Islanding | Historical seasonal and synthetic contingency studies. | Deterministic 24/72/168 h windows over multiple starts, fuel stock and resupply stresses, DG unavailability and EV mission feedback. ENS remains conditional on each window. |
| Normal grid operation | Existing reserve and import/export scenarios and conditional modelled economics. | Stage 6 import headroom and annual SOC/charge accounting. Stage 7 separately replays comparable cash flows at matched modelled service. No approved tariffs or capacity permissions are inferred. |
| Verification | 53 Python regression tests. Published native and independent cases remain with their original scope. | 143 Python tests, analytical/trace checks, and limited Stage 8 native component evidence. Integrated DG+BESS D1 was blocked at the native controller gate. Full hybrid interoperability and HOMER validation remain open. |
| Reliability | Historical fixed outages and scoped engineering evidence. | Literature register and parameter conflicts inform possible sensitivity cases. Site failure rates, probabilities and EENS require independent site evidence. |

[Historical load ledger](Initial%20Draft/data/hourly-load-checks.json) · [Revised load report](Week7Remake/week7/load_calculation_report.md) · [Stage 8 outcomes](Week7Remake/week8/README.md) · [Public source provenance](Week7Remake/docs/publication-provenance.md)
