# Annual grid-connected operation

From the repository root, calculate the annual hybrid case at 20 kW of modelled
export capacity and 30% operating reserve:

```powershell
python -c "from models.grid_connected.dispatch import cases, run; case = next(c for c in cases() if c.name == 'P1_E20_R30'); _, metrics, _ = run(case); print(metrics['grid_import_kwh'], metrics['soc_final'])"
```

`dispatch.py` produces hourly energy flows and an annual metrics record.
`economics.py` evaluates those metrics at the selected price and with the
lifecycle assumptions in `config/economic-parameters.json`. Case definitions
remain in the original factories and the annual protocol is in `config`.

[Grid-connected economics evidence](../../validation/grid-connected-economics/) ·
[Grid electricity carbon evidence](../../validation/grid-electricity-carbon/)
