# LC1 Week 7 Next Stage — Validation Update

**Review date:** 2026-11-19. **Scope:** versioned Python numerical screening only.

## Evidence completed

- Original source integrity: `python week7/audit/check_preservation.py` -> **166/166 SHA-256 preserved**.
- Regression: `python -m pytest -q -p no:cacheprovider tests week7/tests week7/nextstage/tests` -> **78 tests passed**, including 53 historical tests, 13 previous Week7 test instances and 12 next-stage test instances.
- New screened cases: **177/177 complete** = 9 size candidates + 108 four-season duration/size cases + 48 EV mission-coupled cases + 6 fixed-demand contingency cases + 6 dynamic EV contingency cases.
- AC conservation and BESS DC energy residuals under **1e-6 kWh** in all output cases, no BESS charge/discharge in the same hour, fuel within configured initial stock (small floating-point tolerance), BESS SOC in bounds, no EV battery discharge below its protected propulsion reserve.
- The six originally valid historical capacity screenings reproduce Critical ENS, Total ENS, fuel and end-SOC within **1e-6** under versioned S3-v2. The three previously quarantined cases now produce valid numerical energy ledgers.
- EV feedback charging, with no supply shortfall, reproduces each hour of the previous 8,760h Central EV demand schedule, 1,513 annual mission departures and 40,442 kWh of propulsion energy.
- During outages, unserved EV charging is not credited to vehicle SOC. A deliberate no-charge negative test forces mission misses and preserves SOC reserves.

## Validation still missing

1. **No new native Microgrid Design Toolkit (MDT) execution.** Limited prior DG-only parity does not establish controller/BESS/PV/Wind model equivalence.
2. **No HOMER Pro run.** The nine-capacity Python screen is not a HOMER re-optimisation or a globally optimal NPC solution.
3. No real 120-person military site energy survey, OEM vehicle/charger evidence, or normal grid import connection confirmation.
4. No voltage/frequency, grid-forming, black-start, protection relay, earthing, transient UPS ride-through or equipment-level deployment certification.
5. No EENS: scenario probabilities and repair/fuel logistics data are absent. Four seasonal samples are not statistical weather coverage.
6. No bidirectional V2B/V2M discharge; costs exclude EV retrofit/bidirectional charger and degradation pricing.

## Required next external verification

- Native MDT / HOMER Pro project files, tool versions, system settings, input met/weather traces, fuel models, controller strategies, output CSVs/logs, and an agreed tolerance schedule.
- Original A/B/Integration frozen results if full historical replay is needed (only archived limited evidence available).
- Supervisor approval of design basis, critical-tier definitions and whether V2B/M should remain Future Work.
