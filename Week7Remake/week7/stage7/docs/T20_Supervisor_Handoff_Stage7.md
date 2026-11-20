# LC1 EN3400 — Stage 7 Supervisor Decision and Evidence Handoff

**Prepared:** 19 November 2026. **For:** Project Lead / LC1 Supervisor. **Supervisor approval:** not yet obtained.

## Evidence to present

1. Original LC1 A/B and stage archives remain preserved; 166 original file SHA-256 checks hold.
2. Revised 120-person site and 7-vehicle loads are **provisional assumptions**, not real military facility or fleet audit.
3. Stage 7 adds six independent analytical checks, five archived trace audits (18,024 hourly rows), four 8,760-row HOMER-primary-load inputs, and 27 year-by-year cost PV reconciliations.
4. The 52-start 168h scenarios and fuel delivery tests remain deterministic; there are no approved failure probabilities or EENS.
5. **No new native MDT or HOMER Pro run has occurred.** The existing archival 24h DG-only validation is not transferred to the new hybrid results.

## Decisions to seek (none assumed decided)

| ID | Decision requested | Why it is needed | Default until approved |
|---|---|---|---|
| D27 | Approve 120-person representative design basis as a *hypothetical* site? | Fixes load-sizing study scope | All site values provisional |
| D28 | Is the site normally grid connected, intermittently connected or normally islanded? | Determines whether Stage 6 operating-cost proxy is relevant | Do not select design on NPC |
| D29 | Are EV models/mission schedules and electric heating justified by supplied evidence? | Avoids unsubstantiated load and resilience claims | 7 vehicle archetypes only |
| D30 | Which native solver/version and licenced project can be used for the first true benchmark? | T17 blocked until an actual run | No native parity claim |
| D31 | Is the actual MDT_DERIVED generator fuel curve accepted for HOMER approximation, and what error is tolerable? | HOMER linear fuel model may not match piecewise Python | Report as not comparable until checked |
| D32 | What counts as critical load, and what is the accepted resilience threshold? | Avoids declaring reliability from selected 52 windows | Report tier-specific ENS only |
| D33 | Are fuel resupply reliability, generator outage statistics and travel costs available? | Needed for EENS, risk model and complete economics | Treat deterministic contingencies only |
| D34 | Keep WP3 bidirectional EV support as Future Work? | No confirmed EV/chg capability | V2B/V2M uncredited |

## Handoff acceptance test

For genuine T17 cross-validation, return an untouched original native project file (or verifiable native export), native software/version details, the exact fuel and BESS dispatch configuration, 1h/24h comparison metrics and output screenshot or log. Use `stage7/external_handoff/USER_FILL_native_component_results_template.csv` and metadata JSON to record values and source checksums. The Python comparison function is a numerical aid, not an authenticity certificate.
