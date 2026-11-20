# EN3400 LC1 — Stage 5 Supervisor Handoff

**Prepared:** 19 November 2026 · **not yet sent or approved**  
**Study:** Representative 120-person Sennybridge camp, seven provisional EV models, 2025 fixed-LST source year.  
**Relevant earlier handoffs:** Stage 3 D1–D9, Stage 4 D10–D15. Every earlier item is still pending unless the supervisor separately supplies an approval.

## Results for discussion

- With PV/Wind 100/100 kW and initial fuel 2,000 L, increasing BESS 450→600 kWh adds £60,000 illustrative CAPEX, improves mean 168h total ENS by ~48.0 kWh, and leaves Critical ENS shortfall windows at 15/52.
- For PV/Wind 100/100 + BESS 450, three idealised fuel deliveries reduce Critical ENS-shortfall starts to 0/52, but missing a delivery restores 2/52 and DG offline 24–48h with deliveries causes 41/52.
- Inherited economics support an illustrative 20y selected cost-stream PV, **not full NPC**. Across 486 price/valuation parameter sets, the winner changes with the non-cash value attributed to Critical Load loss.
- The Stage 5 integrity preflight passes source and output checks, but new native MDT/HOMER Pro executions are both zero.

## Decisions to request (not approvals)

| ID | Pending supervisor decision | Suggested boundary pending response |
|---|---|---|
| D16 | Do 20y horizon, 3% discount and inherited replacements remain suitable for site-level screening? | Retain as explicit historical assumptions, not estimates of procurement cost. |
| D17 | Which UK-appropriate supplier-price ranges and lifecycle maintenance/fuel logistics quotes are acceptable? | Do not claim economic optimality before credible, compatible prices and whole-year operating costs. |
| D18 | How should emergency outage frequency and critical-load shortage consequences be represented? | Keep deterministic ENS and shadow-cost alternatives separate unless evidence supports probabilities/valuation. |
| D19 | Can 48/96/144h fuel deliveries be assumed physically accessible and budgeted? | Keep as contingency counterfactual only until access, safety, convoy and fuel-transfer feasibility are checked. |
| D20 | What native MDT/HOMER benchmarks are compulsory and which EMS/AC-reference differences preclude parity? | Sign off partial tool comparison with explicit unsupported features; never claim full parity by inference. |

## Suggested meeting order

Review (i) paired physical ENS, (ii) delivery failure and DG availability dependencies, (iii) conditional CAPEX/20y selected-cost ledger, (iv) the shadow-value ranking reversal, and (v) the unanswered native validation requirements. Explicitly decide whether the paper should continue with WP3 V2B as conditional future work or attempt an evidence-gated vehicle/charger feasibility study. **No OEM V2B support has yet been established and none is credited to the microgrid.**

## Attached evidence for another reviewer

- `week7/stage5/docs/T09_T16_Integrated_Cost_Resilience_Report.md`
- `week7/stage5/docs/T17_Native_Validation_Preflight.md`
- `week7/stage5/docs/EN3400_methodology_draft_v0.5.md`
- `week7/stage5/outputs/stage5_conditional_economic_comparison.csv`
- `week7/stage5/outputs/stage5_key_option_pairs.csv`
- `week7/stage5/outputs/stage5_cost_sensitivity_full.csv`
- `week7/stage5/figures/`

**Supervisor sign-off status: PENDING.**
