# EN3400 LC1 — Methodology v0.6 Addendum: Annual Grid Adequacy and Economic Boundary

**Draft; supervisor approval outstanding.** This section extends the Stage 5 methodology v0.5 and does not replace it.

## Normal-year research question

Can the revised hypothetical 120-person operational support camp and planned EV fleet be supplied under the inherited 100 kW grid import limit, and how do imported electricity, storage dispatch and vehicle readiness change as assumed grid headroom, PV/Wind rating and BESS capacity vary?

## Model

At each source-LST hour, compute available PV and Wind from the frozen per-unit resource series. The three requested demand tiers are critical/C4ISR, Auxiliary, and the individual-EV fleet aggregate. For EVs, update departure and return, traction energy, SOC, connected state, charging request and delivered charging energy at the end of each hour. Vehicles below mission reserve plus traction requirement cannot depart.

`P_renewable,used + P_grid,import + P_BESS,discharge = P_load,served + P_BESS,charge + P_grid,export`

`E_BESS(t+1) - E_BESS(t) = eta_charge * E_charge,AC - E_discharge,AC / eta_discharge`

The battery is dispatched before grid purchases under an explicitly unoptimised legacy-style self-consumption strategy; the import power is then limited to the scenario feeder assumption. The served energy is allocated in strict C4ISR→Auxiliary→EV tier order. Unserved hourly requests are recorded; no generator or UPS service is manufactured in the normal connected state. During the final 48 hours, the model attempts to restore the initial 70% BESS SOC using remaining import headroom and renewable energy.

## Evaluation metrics and cautions

- Nondeferrable C4ISR/Auxiliary unserved energy is reported separately.
- EV Charging Slot Deficit is a **deferred energy-service request metric**, which can recur in later hours for the same battery SOC deficit; it is **not** an independent energy loss and must **not** be called reliability EENS.
- Vehicle readiness is number of fulfilled scheduled departures divided by scheduled opportunities, under provisional fictional mission calendars.
- Normal connected-year grid purchases and grid-service-based cost proxies are separate from deterministic islanded 168-hour ENS and replenishment scenarios. Combining them into an NPC requires a non-overlapping event model, site connection/tariff evidence, credible normal operating strategies, and independently justified failure rates.
- Although a grid-limit sensitivity of 100/125/150/175/200/225/250 kW was tested for two cases, no power-system compliance studies, transient stability, voltage regulation, grid-forming or site approvals were performed.

## T17 evidence boundary

All physical checks are Python accounting checks. None of the new Annual Grid study is externally cross-validated in native MDT/HOMER Pro. Historical DG-only 24h MDT evidence cannot validate this multi-component year-long model. New native benchmark evidence and supervisor approval remain mandatory before final design recommendation.
