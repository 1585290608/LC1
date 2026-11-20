# LC1 EN3400 — Supervisor decision handoff (proposed)

**Prepared 19 November 2026.** Decision owner: **Project Lead / University supervisor**. None of the decisions below are recorded as approved, and no supervisor meeting or message is claimed.

## Summary for review

The 120-person Sennybridge camp and seven EVs are representative *research design assumptions*, not MOD measurements or real vehicle specifications. An expanded Python energy-resilience study now covers **nine candidate stationary configurations**, **52 weekly outage start positions**, and **24/72/168 h** durations (**1,404 additional tests**). Earlier four-season results are retained, not replaced. All 84 Python regression/physics tests pass and 166 original source files retain their hashes. New native MDT/HOMER cross-validation has not been executed.

The critical change to the interpretation is that one winter/seasonal window can materially understate the deficit: even the 100 kW PV + 100 kW wind + 600 kWh BESS candidate has critical ENS in **15 of 52 independently initialised 168 h windows**. This is **not** 15/52 probability of an outage or an EENS calculation. The 24/72 h weekly starts have no critical ENS under the modelled controller, but still have non-critical ENS and are not certified continuous power supply.

## Required supervisor decisions (not yet approved)

| ID | Question for supervisor | Current recommendation | Approval/notes |
|---|---|---|---|
| D1 | Is a 120-person representative camp acceptable? | Keep as hypothetical envelope; request building/occupancy evidence | PENDING |
| D2 | Are C4ISR, medical and perimeter security in the defined critical tier? | Retain explicit research priorities pending permitted operations evidence | PENDING |
| D3 | Are generic 7-EV archetypes adequate for S1? | Keep EV charging/readiness sensitivity; do not claim OEM deployment | PENDING |
| D4 | Should thesis main question focus on islanded resilience? | Yes; keep normal-grid constraints a diagnostic unless connection validated | PENDING |
| D5 | Does the 52-week/24-72-168h comparison satisfy the outage sensitivity study? | Use as deterministic robustness evidence; avoid event frequency interpretation | PENDING |
| D6 | Which external validation is mandatory? | Request native MDT partial matched benchmark and HOMER Pro NPC separately | PENDING |
| D7 | Should 10/20/30 kW V2B/V2M be implemented? | Future Work unless exact certified vehicle/charger/islanding interface and costs supplied | PENDING |
| D8 | Is 100/100/450 vs 100/100/600 an acceptable sensitivity comparison? | Yes, but no optimal-capacity claim without NPC and broader reliability objective | PENDING |
| D9 | Are project research/source citations sufficient for provisional load estimates? | No: add public equipment/vendor references and permissible real-site data where available | PENDING |

## Short proposed demonstration order

1. Show S0 original 1,104 kWh/day versus 120-person S1 central 2,092.9 kWh/day (not a like-for-like real-site observation).
2. Show why original 50/50/300 fails the revised 168h demand in winter and why increasing capacity can help some, not all, conditions.
3. Show 52-week sensitivity table and highlight weather-start spread and fuel depletion; explain “15 of 52 shortfall windows” is **not a probability**.
4. Show EV charging-to-SOC mission feedback; no bidirectional EV discharge is claimed.
5. Show explicit limitations and request D1–D9 decisions, especially whether native MDT/HOMER runs are a graduation requirement.

## Evidence files to present

- `week7/stage3/docs/EN3400_methodology_draft_v0.3.md`
- `week7/stage3/docs/T19_results_comparison.md`
- `week7/stage3/docs/T17_MDT_HOMER_validation_runbook.md`
- `week7/stage3/outputs/weekly_52_starts_summary.csv`
- `week7/stage3/figures/` for two exploratory plots
- `week7/nextstage/outputs/mission_readiness_feedback_matrix.csv`

## Decision record status

The handoff is ready for **review**, not confirmed as reviewed. Record the meeting date, exact comments, acceptance/rejection per D1–D9 and action owners only **after** the actual supervisor discussion. User submission remains the responsibility of the Project Lead.
