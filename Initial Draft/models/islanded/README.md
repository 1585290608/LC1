# Islanded operation

From the repository root, run the 24-hour combined strategy example:

```powershell
python -c "from models.islanded.strategies import run_case; rows, settings = run_case('S3', 'MDT_DERIVED', 24); print(len(rows), sum(r['dg_fuel_consumed_l'] for r in rows))"
```

`strategies.py` selects S0–S3 and the fuel formulation. `contingencies.py`
defines C1–C4 and uses `service_dispatch.py` for segment-level energy and
service accounting. `config` holds the archived study protocols and active
fuel-curve data. The case factories retain the original definitions and IDs.
The shared winter trace is used from the archive when replaying the published
resilience study.

[Diesel and battery strategy evidence](../../validation/diesel-fuel-and-dispatch/) ·
[Outage resilience evidence](../../validation/outage-resilience/)
