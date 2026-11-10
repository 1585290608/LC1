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
