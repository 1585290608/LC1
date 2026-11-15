# LC1: Hybrid microgrids for defence applications

This project uses a representative Sennybridge-area microgrid to study
outage resilience and grid-connected economics. The two operating modes
share equipment models and input data. Research labels remain traceable
to the original model versions and archived results.

| Location | Purpose |
| --- | --- |
| [models/core](models/core/) | Shared equipment and energy accounting |
| [models/islanded](models/islanded/) | Dispatch strategies, fuel formulations, outage and equipment contingency cases |
| [models/grid_connected](models/grid_connected/) | Annual grid dispatch, electricity bills and lifecycle cost analysis |
| [data](data/) | Shared hourly inputs and source weather |
| [tests](tests/) | Existing regression checks, with identical copies consolidated |
| [validation](validation/) | Research reports, saved results, engineering evidence index and archive replay |
| [Image](Image/) | Selected existing figures by research purpose |

[Maintenance guide](docs/workspace-guide.md) · [Scenario and history index](docs/scenario-index.md) ·
[Source and hash map](docs/source-map.csv) · [简体中文](README.zh-CN.md)

## Research status · 15 November 2026

### Completed

| Validation | Result |
| --- | --- |
| Grid loss and islanding | Sandia MDT represents loss of upstream utility supply. Independent OpenDSS snapshots check steady-state PCC opening, islanded supply and explicit reclosure. |
| Diesel-only cross-validation | Controlled constant-load MDT and Python cases agree on event energy and fuel over 24, 72 and 168 hours. |
| Load priority and recovery | A 40 kW diesel test confirmed that the EV and interruptible auxiliary feeders resumed service when demand fell from 78 to 39 kW. In a separate hybrid stress case, the feeder-breaker layout reduced C4ISR unserved energy from 11.765 kWh to zero. Total unserved energy increased from 30.588 to 38.551 kWh, with the remaining shortfall on the EV feeder. |
| C2 hybrid and battery limits | Native reruns of the 75 kW PV, 75 kW wind, 300 kWh BESS and 120 kW PCS configuration reported zero unserved energy across all tiers in the three tested 24-, 72- and 168-hour outage windows. A separate overload case confirmed a 120 kW active battery discharge limit in the model. |
| Solver timing and battery SOC distribution | Five native reruns yielded 309 solver intervals and time-of-day SOC histograms. In the 24-hour C2 comparison, MDT recorded about 23.42 hours of time weight in bins above 80% SOC, compared with zero in the aligned Python trace. The histogram is captured during the run and is absent on reopening the saved MOF. |
| Python dispatch and economics | Dispatch, reserve strategies and modelled financial outputs were reproduced under the study assumptions. |

### Open

- **Step-by-step hybrid cross-validation.** Simultaneous native records of
  exact SOC, component power and breaker contact states are still required
  for a chronological MDT–Python comparison.
- **Site engineering.** Measured loads, the approved feeder schedule and
  single-line diagram, PCS parallel and grid-forming behaviour, UPS hold-up,
  protection coordination and PCC transfer remain unverified at Sennybridge.
  The 10 kW essential auxiliary threshold is a modelling assumption.
- **Commercial and design decisions.** Actual payback and final equipment
  selection require verified quotations, tariffs, export terms and permission,
  and site equipment evidence.

The latest native runs and their private catalogues are retained in the local
research archive. The public [validation index](validation/) links the
reports and replay material available in this repository.

## Quick start

Open a terminal at the repository root with Python 3.12. The model uses the
Python standard library. Install pytest for the regression suite.

```powershell
python -m pip install -r requirements-test.txt
python -m pytest -q
```

The [islanded](models/islanded/) and [grid-connected](models/grid_connected/)
pages show the entry points and inputs. For the archive comparison, see the
[replay guide](validation/archive-replay.md).

The research concerns modelled energy, service and conditional economics.
Consult the linked validation reports for the scope of native MDT evidence,
equipment assumptions and modelled export limits.
