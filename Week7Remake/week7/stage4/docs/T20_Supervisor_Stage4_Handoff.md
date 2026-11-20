# LC1 Supervisor Review — Stage 4 Addendum

**Prepared 19 November 2026.** Status: **prepared for supervisor review, not submitted/approved**. This is an addendum to `week7/stage3/docs/T20_supervisor_handoff.md`; prior decisions D1–D9 all remain pending.

## Main finding for discussion

A 100/100 kW PV/Wind + 450 kWh BESS candidate, 100 kW DG and initial 2,000 L tank showed Critical ENS in 15 of 52 independent 168-hour start scenarios. Assuming 500 L refuels at hours 48, 96, and 144 reduced that to 0 of 52; missing any one of those deliveries raised it to 2 of 52. The three deliveries can be stopped by 2,000 L tank headroom; mean accepted = 1,196.8 L. Forced DG unavailability hours 24–48 despite all three deliveries produced Critical ENS in 41 of 52 starts.

This is a *model-conditional comparison* using provisional camp loads, resource year and idealised fuel-transfer logistics. No rate of failure, EENS or real 168h continuity is inferred; none of the new cases is native MDT/HOMER verified.

## Supervisor decisions to add

| ID | Decision required | Suggested disposition | Status |
|---|---|---|---|
| D10 | Can repeated hour-48/96/144 fuel replenishment be treated as an *assumed* stress scenario? | Accept as conditional analysis only; verify physical feasibility before primary recommendation | PENDING |
| D11 | What DG forced-outage/repair windows should represent generator availability? | Keep 24/48 and 0/72h as illustrative tests until evidence allows probabilistic reliability | PENDING |
| D12 | Should the dissertation use planned-load ENS or dynamic EV-SOC load feedback for the primary S1 figure? | Use planned demand for like-for-like capacity comparison, with separate EV readiness sensitivity | PENDING |
| D13 | Is conditional Critical Load Energy Autonomy preferable to overall ENS as the primary design performance target? | Report both critical and noncritical service, and explicitly distinguish mission readiness | PENDING |
| D14 | Is native MDT parity required for the revised 120-person hybrid model, and which EMS approximations are acceptable? | Require an agreed partial benchmark with written model-scope limitations | PENDING |
| D15 | What operational cost assumptions or permitted data should support fuel-resupply comparison? | No full NPC/economic ranking until evidence and HOMER setup are established | PENDING |

## Suggested discussion sequence

- Compare Stage3 original 15/52 critical shortfalls to the Stage4 logistics and DG downtime results.
- Explain why 0/52 *modelled* critical shortfalls under idealised refuelling is not 100% site reliability.
- Show Figure `stage4/figures/fuel_supply_critical_shortfall_windows.png` and archived Stage3 52-week plots.
- Show that PV/Wind/BESS size and fuel supply are related design choices; full NPC and maintenance costs are unavailable.
- Request written scope decisions D1–D15; do not record approvals before they occur.

## Handoff locations

- `week7/stage4/docs/T10_T16_Contingency_Results.md`
- `week7/stage4/docs/T17_Validation_Boundary_and_Next_Benchmarks.md`
- `week7/stage4/outputs/stage4_52start_contingency_summary.csv`
- `week7/stage4/outputs/stage4_13start_EV_mission_feedback.csv`
- `week7/stage4/figures/`
