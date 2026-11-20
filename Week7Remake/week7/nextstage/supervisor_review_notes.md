# LC1 Week 7 — Supervisor Discussion Checklist

**Project:** Hybrid Microgrids for Defence Applications — EN3400

## Decisions requested (not yet approved)

1. Approve use of a **representative 120-person Sennybridge operational support camp**, rather than suggesting the proposed electrical load is an actual MOD site survey. Confirm population/occupancy, buildings, heating arrangements and C4ISR critical-load scope.
2. Confirm which critical vs non-critical load priorities should be retained (the current study protects C4ISR first, then Auxiliary, then EV charging) and whether any critical EV charging should be reclassified.
3. Confirm whether 100 kW should be treated as the illustrative *grid import limit* and whether site infrastructure studies exist; current 100 kW import diagnostic is not a network load flow.
4. Confirm the acceptability of using **illustrative seven-vehicle EV archetypes** and whether real OEM vehicles need to be selected before dissertation submission.
5. Approve the core S1 + stationary-BESS S4 research comparison and the **24/72/168-hour** resilience study; treat islanded EV-to-critical-load support as conditional/Future Work unless hardware evidence emerges.
6. Decide whether the final dissertation requires native MDT/HOMER Pro runs and which cases must match; available results are Python numerical-only.
7. Review the non-monotonic battery result (100/100/450 has lower winter ENS than 100/100/600) as a dispatch-policy sensitivity, not an unqualified hardware conclusion.

## Evidence supplied

- `technical_report.md`: full nine-point comparison, four-season 168h comparisons, EV mission readiness, contingency sensitivity, grid-limit diagnostic.
- `validation_update.md`: 78 software tests and limits to validation evidence.
- `outputs/`: machine-readable output and traces.
- `figures/`: dissertation-ready *exploratory* comparison figures, requiring source/reference labels in final thesis.

**Status:** prepared for supervisor review, but no review/approval or message to supervisor is claimed.
