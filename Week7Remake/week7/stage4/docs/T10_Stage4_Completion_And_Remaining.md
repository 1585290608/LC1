# Stage 4 Implementation Status and Source-Preservation Declaration

## Completed code and analysis

- T10: 52 matched starts × 17 policy interventions on primary 100/100 kW + 450 kWh; plus 52 starts × 6 policy interventions on 75/75 + 450 and 100/100 + 600 = **1,508 deterministic 168h cases**, all internally valid.
- T06/T16: 13 starts × 4 contingencies = **52** additional unidirectional 7-EV SOC/mission readiness cases, all internally valid; separate from planned EV demand comparisons.
- T16: 52-paired deterministic mean/median/p90/worst ENS and critical service frequency *across sample starts*. Not EENS or probabilistic reliability.
- T17: 780 metric comparisons to previously generated Stage3 baselines at corresponding 52 starts, 96 Python tests, and frozen 166-source hash verification, all passed.
- T18/T19: methodology v0.4 and T10/T16 results interpretation drafted, assumptions and limitations clearly marked.
- T20: supervisor addendum D10–D15 prepared, not approved.

## Partial / not completed

- T09: no HOMER Pro native optimisation or full NPC; no cost of fuel deliveries, diesel repairs/maintenance or batteries included.
- T17: no new native MDT or HOMER Pro runs, no final hybrid-model parity.
- T03–T05: Sennybridge and 7 EV archetypes still unverified preliminary assumptions.
- T11–T14: V2B/V2M remains disabled, awaiting verified OEM capability, permitted islanded use, charging hardware and costs.
- T20: scope approval still outstanding.

## What to do next

1. Share Stage4 T10/T16 results and D10–D15 with the supervisor for scope and scenario acceptance.
2. Obtain defensible site inventory and fuel-logistics assumptions and adjust source assumptions *only in a new version*.
3. In authorised native MDT/HOMER software, perform matched DG, PV/wind, BESS and integrated benchmarks with archived source/input hashes.
4. Build evidence-based lifetime NPC model, include replacement and logistics costs, then reassess robust capacity vs fuel logistics.
5. Keep EV emergency export (V2B/V2G) as optional/future until verified technical evidence is available.
