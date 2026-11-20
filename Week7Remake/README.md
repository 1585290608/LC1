# LC1 Week7Remake

Week7Remake extends the historical energy and dispatch models to address a larger **hypothetical** site. The historical load model peaks near **65 kW**. The revision tests a **provisional 120-person design basis** with **14 infrastructure categories** and a new set of vehicle-specific charging schedules. Both versions use a fixed 2025 source-LST weather year. No occupancy, equipment inventory, route or electricity meter data from an operating defence site were used.

| Revised demand | Annual energy | Peak |
| --- | ---: | ---: |
| Low | 682.5 MWh | 172.1 kW |
| Central | 763.9 MWh | 195.1 kW |
| High | 871.7 MWh | 225.0 kW |

The increased energy and peak demand change the required grid import headroom, renewable dispatch, storage capacity and power, DG operating time, and fuel inventory. The original equipment cases remain historical comparisons. The revised screening outputs are conditional research results and do not select a final equipment configuration. [Demand assumptions and results](week7/load_calculation_report.md)

## EV assumptions

The original fleet representation was 20 kW for four hours per day, 80 kWh/day. The revised fleet uses seven generic archetypes, with per-vehicle SOC and mission energy. The model assumes 92% AC-to-DC charging efficiency, a shared 70 kW AC cap, and 90% initial SOC. Vehicles charge only during modelled connection windows. A reserve gate checks that a vehicle can complete its scheduled mission before departure.

| Vehicle group | Count | Battery per vehicle | AC connection | Nominal scheduled travel | Minimum SOC |
| --- | ---: | ---: | ---: | --- | ---: |
| Light utility | 4 | 75 kWh | 11 kW | 50–65 km per mission, illustrative weekdays | 20% |
| Medium logistics | 2 | 160 kWh | 22 kW | 90–95 km per mission, illustrative weekday schedules | 25% |
| Mobile emergency support | 1 | 100 kWh | 11 kW | 20 km in one illustrative weekly exercise | 45% |

The input file records departure hours, return hours, duty days and specific energy use. Later islanded studies use delivered charging energy to assess subsequent synthetic missions. OEM capability and real mission readiness remain unverified. [Fleet configuration](week7/config/fleet.csv) · [Infrastructure configuration](week7/config/equipment.csv)

## Status

| Feature | Status | Scope |
| --- | --- | --- |
| Shared PV/Wind/DG/BESS/PCS and load models | TESTED | Historical resource series, equipment constraints and energy accounting. |
| Three demand scenarios and EV fleet | TESTED | Hourly synthetic accounting, vehicle SOC and mission-reserve checks. |
| Islanded timing, capacity and fuel sensitivity | TESTED | Multi-start deterministic windows and stress cases. |
| Normal annual dispatch and cost | TESTED | Stage 6 peacetime grid model and Stage 7 service-matched cash-flow proxy. |
| Reliability evidence and failure register | IMPLEMENTED | Evidence mapping with source-specific uncertainty. Site failure calibration is blocked. |
| Native MDT component benchmarks | PARTIALLY_VALIDATED | DG-only, BESS and available renewable-power cases. See separate aggregate, event and native clock results. |
| Integrated DG+BESS D1 | BLOCKED | Strict configuration feasibility NO-GO. 2 h native benchmark NOT RUN. |
| Full hybrid MDT / HOMER native validation | BLOCKED | Native equivalence and sufficiently detailed telemetry still needed. |
| Vehicle-to-grid and production stochastic reliability | PLANNED | Neither is part of the current dispatcher or validation. |

[Stage 3 multi-start study](week7/stage3/README_STAGE3.md) · [Stage 4 contingencies](week7/stage4/docs/README_STAGE4.md) · [Stage 5 conditional comparison](week7/stage5/docs/README_STAGE5.md) · [Stage 6 annual grid model](week7/stage6/README_STAGE6.md) · [Stage 7 analytical checks and cash flow](week7/stage7/README_STAGE7.md) · [Stage 8 native and literature evidence](week8/README.md)

## Run independently

Run these commands in this directory with Python 3.12.

```powershell
python -m venv .venv
$env:PYTHONDONTWRITEBYTECODE='1'
& ./.venv/Scripts/python.exe -B -m pip install -r requirements-test.txt
& ./.venv/Scripts/python.exe -B -m week7.prepare_regression_fixtures
& ./.venv/Scripts/python.exe -B -m pytest -q
& ./.venv/Scripts/python.exe -B week7/audit/check_preservation.py
```

Fixture preparation regenerates three public synthetic EV traces and verifies their frozen hashes before saving missing files. Existing fixtures are checked without replacement. The test suite covers the inherited model and all Stage 0–7 folders. The public baseline checker validates 142 files; a separate archive check validates all 166 historical digests. Archived stage commands and inputs remain linked above. Use isolated output locations for large or historical replay runs. [Reproduction and archive provenance](docs/publication-provenance.md)
