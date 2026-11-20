# LC1 Week 7 / Stage 6 — Supervisor discussion handoff

**Prepared 19 November 2026; no approval or response yet recorded.**

## Decisions needed

- **D21 Site operating regime:** Is a representative camp primarily grid-connected, normally islanded, or connected only intermittently? Stage 6 normal-year economics assumes continuous grid availability, while Stage 3–5 outage cases assume islanded operation for 24/72/168h.
- **D22 Grid rating:** Is the original 100 kW import limit a genuine site constraint, or only a research scenario? The study scanned 100/150/250 kW and additional 125/175/200/225 kW for 100/100/450. No grid upgrade cost or permission is included.
- **D23 EV demand evidence:** Confirm whether seven EV archetypes and their duty cycles should remain illustrative. Approve separate reporting of deferred charging versus missed departures; no OEM-backed bidirectional claim has been made.
- **D24 Cost boundary:** Approve/replace project-inherited PV, wind, battery, grid tariff, O&M and replacement assumptions using sourced UK quotes or published evidence. The output is **not NPC**; no full grid tariff, charging infra, connection upgrades, outage event time weighting or lifetime degradation model is validated.
- **D25 Native validation plan:** Supply licensed MDT/HOMER environments or authentic exports and confirm matching control semantics and measurable metrics. Current new native runs: zero.
- **D26 Dissertation scope:** Decide whether annual grid adequacy is within final EN3400, and keep V2B/V2M as Future Work unless actual vehicle, charger and grid-forming evidence emerges.

## What is ready for review

- 81×8,760h annual grid-limited supply simulations, 14 additional feeder sensitivities, two full hourly traces, 243 conditional tariff scores.
- Energy-balance/EV mission feedback tests, unmodified original baseline files, Stage 5 deterministic outage comparison joined without merging monetary costs.
- New Methodology v0.6 addendum and T17 native validation gate document.

**No final design recommendation, native-solver validation, site commitment, tariff contract or supervisor agreement is claimed.**
