# LC1 Draft 4 — Integrated Research Validation Report

**Research date:** 6 November 2026  
**Topic:** Hybrid Microgrids for Defence Applications  
**Lead author:** Jiahao Li  
**Research scope:** Numerical simulation and conditional techno-economic analysis of a **representative** (not measured or installed) Sennybridge-area microgrid.

## 1. Status and final decision

**D4 integration status: COMPLETE for the archived data and IEEE-format working outputs.**

The distinct Draft 3A, 3B and 3C experiments can now be discussed in one coherent report and an approximately 12–15-minute main presentation. There is no need to introduce a new simulation scenario merely to populate the manuscript. The study remains a **deterministic energy-accounting model**, not certified power-system or defence infrastructure engineering.

**University submission is not yet certified**: the formal EN3400 dissertation handbook, page/word limit, official format and generative-AI declaration instructions were not supplied. IEEE conference styling is a deliberate working format, not a verified Cardiff University final assessment requirement.

## 2. Primary evidence and counts

| Research package | Distinct cases | Scope |
|---|---:|---|
| Draft 3A | 24 | 4 dispatch strategies × 2 fuel formulations × 3 nested durations (24/72/168h); no shortage in reference 2,000L fuel case |
| Draft 3B | 12 annual dispatch + 16 financial computations | 8,760 hourly 2025 profiles (12 distinct annual scenarios) and sensitivity price recalculations (16 financial outcomes) |
| Draft 3C | 18 unique scenarios (17 new; one baseline reused) | Four separate 168h seasonal windows; fuel stock; starting SOC; 336h combined stress |
| D4 cross-study checks | **328 passed** | Aggregate ENS/EA, inventory and DG destination identities, scenario counts, cross-study baseline, finance and Scope 2 |
| D4 raw-trace and financial checks | **1,075 passed** | Re-read the 24 Draft 3A primary dispatch traces, 17 available new Draft 3C hourly traces, 12 Draft 3B annual traces and 16 financial 21-year cash-flow tables |

**Source integrity**: each of the three original ZIP archives passed zip-member integrity checks. SHA-256 values of original ZIPs and selected extracted source tables are preserved in `audit/SOURCE_PROVENANCE.csv`. This D4 build did **not** execute a new physical or software dispatch solver and did **not** run new native MDT calculations; it independently recomputed identities from original saved data. Archived source studies contain their own regression testing and replay records.

## 3. Final study definitions

| Term | Meaning and comparison boundary |
|---|---|
| Representative site | Sennybridge-area coordinates and NASA POWER gridded 2025 weather, not actual MOD site monitoring |
| Synthetic demand | 402,960 kWh/year / 1,104 kWh/day; C4ISR (priority 1), auxiliary (2), EV charging (3) |
| Nominal assets | PV 50 kWp DC, wind 50 kW, battery 300 kWh / PCS 90 kW, diesel 100 kW, starting tank up to 2,000 L, UPS 30 kW / 15 min |
| S0 / S1 / S2 / S3 | Reference dispatch / recover feasible diesel surplus to battery / modified generator commitment / combined commitment and surplus charging |
| P0 / P0R / P1 / P3 | Grid-only / grid+diesel+UPS / hybrid grid-connected self-consumption / P1 with different BESS reserve SOC. **P2 was not implemented.** |
| Fuel FIXED_025 | Constant assumed 0.25 L/kWh of **generated** DG energy, not energy only delivered to loads |
| Fuel MDT_DERIVED | Stored MDT-reference positive-power 25–100% curve; zero-load point is in different units and excluded from positive-power interpolation |
| C4ISR EA (%) | 100×served critical energy/required critical energy within one deterministic event; not instantaneous equipment availability |
| Grid-connected vs islanded | Annual economics (3B) separate from fuel-limited outage service (3A, 3C). They cannot be combined as one uncalibrated reliability/ROI model. |

**Time alignment**: The 3A nested 24/72/168h events all start 2025-01-01 00:00 saved LST. In 3C the 168h windows start January, April, July and October 2025, and the combined 336h window starts January 1. LST is not the same as UK electricity settlement time. Initial SOC and final SOC are not forced equal in islanded windows, unlike the 3B annual economic study (70%→70% for its hybrid cases).

## 4. Integrated results and interpretation

### 4.1 Fuel-model and dispatch effects (3A)

On the same frozen 168h reference generator trajectory, fixed-model consumption is **733.664 L** while the MDT-derived curve gives **1,059.074 L** (**+44.35%**). This difference is attributable to the fuel-model definition, not a fresh generator logging error.

In the 168h fixed-model comparison, combined S3 is **694.528 L** versus reference S0 **733.664 L** (**5.33% lower**), with modelled C4ISR/auxiliary/EV ENS ≈0. Yet S1 uses slightly less fuel **692.783 L** while worsening non-critical ENS. S3 is thus a **candidate under the stated multiple-load service objective**, not globally optimal. Under MDT-derived fuel, S3 **996.969 L** versus S0 **1,059.074 L**. At 24h under fixed fuel, S3 uses **30.288 L** against S0 **17.240 L**; the long-window fuel saving cannot be generalised to all outages. Initial and terminal battery stocks differ by strategy.

### 4.2 Economic evidence (3B)

Under an illustrative 20-year, **3% real discount**, **£0.24/kWh import** and conditional 20-kW export case, grid+standby P0R has estimated NPC **£1,645,514.97** versus Hybrid P1 **£1,421,946.61**, a modelled benefit of **£223,568.37**. Zero-export Hybrid also shows a conditional NPC benefit of approximately **£222,269.95**. Incremental nominal CAPEX is **£405,350**; sustained discounted payback **12.24 years**, allowing for the year-12 equipment replacement that reverses an earlier transient cash-flow crossing.

The economic result is **not robust across all tested assumptions**: electricity at **£0.168/kWh** yields a negative benefit of approximately **−£30,936**, and 60% of assumed wind generation gives about **−£28,051**. Raising the battery normal-operation SOC reserve from 30% to 70% increases annual modeled operating expenditure by **£1,007.75** in the E20 case. Grid export authorisation, real tariff, wind yields and vendor CAPEX are not established.

2026 UK corporate reporting Scope 2 factor **0.13096 kgCO2e/kWh** applied to **imported electricity only** gives **52.772 tCO2e/year** for P0R versus **21.656 tCO2e/year** for P1 under the modelled normal year. This is not full lifecycle carbon accounting and excludes Scope 1 emergency diesel, embodied equipment carbon and Scope 3 losses.

### 4.3 Resilience limits (3C)

The four selected seasonal 168h Hybrid cases yield C4ISR EA **100%** in the *hourly energy model*, with MDT-derived fuel from **319.138 L (April)** to **996.969 L (January)**. Only four selected weeks are sampled; all-year reliability inference is unwarranted.

In the January 168h case with **500 L initial diesel**, Hybrid C4ISR EA falls to **87.935%** (**608.070 kWh ENS**). With **1,000 L**, 100% critical energy is served but only **3.031 L** remains, far short of a robust fuel inventory allowance. The 2,000-L tank physical capacity is unchanged across these comparisons. In a distinct 336h control-vs-combined stress study (PV/wind usable output reduced to 60%, DG unavailable for elapsed hours 48–72), Hybrid EA decreases from **92.256%** to **72.527%**, while critical ENS rises from **780.568 kWh** to **2,769.284 kWh**. The first hour containing critical shortfall moves from **257–258 h** to **51–52 h**. Both cases exhaust the initial 2,000 L fuel stock. This is evidence of a modelling failure boundary, not a real-world measured availability percentage.

At winter initial SOC 30%/50%/70%, simulated C4ISR EA is 100% for all three; diesel differences partly reflect different starting/ending stored energy. This single scenario does not demonstrate a probabilistic reliability benefit from a higher grid-connected reserve floor.

## 5. Major consistency decisions and prohibited claims

1. **Do not pool fuel in L from FIXED_025 and MDT_DERIVED as though calibrated by the same generator data.** They are deliberately different formulations.
2. **Do not claim full Hybrid MDT/Python parity**: only the saved controlled DG-only positive-load protocol is matched to native toolkit evidence.
3. **Do not present 3B payback as the financial valuation of 3C ENS**; lost mission energy was not monetised and the normal year has a different dispatch regime.
4. **Do not present 100% C4ISR EA as a zero-interruption power-quality guarantee.** The model is hourly and relies on idealised supply and controls.
5. **Do not call the 336h stress 'all faults tested'**: PV/wind reduction and DG outage are simultaneous, not an individual-fault factorial study.
6. **Do not describe Sennybridge simulated demand as official MOD metered data, or cost assumptions as procurement offers.**

## 6. Limitations ranked by impact

**Critical deployment blockers**: Grid-forming ability and frequency/voltage reference; protection and short-circuit coordination; actual UPS handover vs 1h DG cold-start; OEM DG min load, fuel curve and transient start; field controls and black-start readiness. In the energy model, PV/wind can still be counted during DG outage without a validated autonomous reference source. That is a modelling assumption, not demonstrated islanding feasibility.

**High empirical uncertainty**: Site-load waveform and load-tier requirements; wind production uncertainty, turbine curve/wake, availability; PV yield and battery lifecycle; actual fuel delivery/storage; CAPEX, O&M, tariff, export permission, discounting and replacements. The modeled wind profile is particularly influential to economic results.

**Study-design uncertainty**: Selected weather windows rather than Monte Carlo; differing terminal stored energy for islanded strategies; one-factor economic sensitivity rather than joint distributions; no life-cycle reliability inference, uncertainty interval or actual fault probability.

## 7. Deliverables and inspection

- `manuscript/LC1_D4_paper.tex` + `references.bib` + `figures/`: reproducible 7-page IEEEtran working manuscript.
- `manuscript/LC1_D4_paper.pdf`: compiled and inspected; citations resolved and no overfull boxes in final build.
- `slides/LC1_D4_Final_Presentation.pptx`: 15 core slides + 3 backup, with editable slide objects and English presenter notes.
- `slides/LC1_D4_Final_Presentation.pdf`: visual PDF export.
- `audit/D4_INDEPENDENT_AGGREGATE_CHECKS.csv`: 328 passing result checks.
- `audit/D4_HOURLY_AND_CASHFLOW_CHECKS.csv`: 1,075 passing source-trace/cash-flow checks.
- `audit/SOURCE_PROVENANCE.csv`: original ZIP and selected source-member hashes.
- `sources/`: selected CSVs and source experiment reports used to build the paper and figures.

The original full 3A/3B/3C ZIP archives (including full code, hourly raw results and provenance receipts) remain separate to avoid duplicating hundreds of megabytes in this deliverable. Reproducing **the complete solver pipeline** still requires those original archives and their dependencies; this D4 bundle is a traceable presentation and manuscript package.

## 8. Remaining external decisions (not D4 calculation defects)

- Confirm with supervisor that both normal Grid-connected cost and Islanded Defence Resilience belong in the final scope; use Python alongside MDT transparently and state AI assistance honestly.
- Obtain official EN3400 final Dissertation handbook, required style/length, marking rubric, submission date and university generative-AI declaration format. The IEEE 2-column paper is **not automatically equivalent** to the required dissertation.
- If resources are available, seek site-representative measured loads, OEM fuel/UPS data, a verified AC-forming/control strategy and realistic tender costs for higher-confidence claims. Without them, retain model-bound wording.
