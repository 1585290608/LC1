# WP0/T02 & WP4/T17 - LC1 Validation Gap Report

**Audit date:** 2026-11-19. **New work class:** deterministic exploratory Python energy-system modelling. This is not deployment validation.

## Evidence checked

1. Original LC1 repository import: 166 original files hashed; all 166 unchanged in the development checkout. Uploaded source ZIP CRC check passed. Original repository regression: **53/53 tests passed**.
2. Current Week 7 extension regression: **66/66 tests passed** when explicitly invoking both `tests` and `week7/tests` (53 inherited + 13 new collected test instances). Passing code tests are not equivalent to independently validated energy system hardware.
3. Original repository `validation/diesel-energy-accounting/validation-report.md` and `validation/cross-study-integration/integration-and-validation-report.md`: native MDT parity is **limited to a saved controlled diesel-generator-only case** under parameter-matched positive-load conditions. Full mixed PV+wind+DG+BESS dispatch equivalence is **NOT** claimed.
4. Cloud A recovered numerical results are explicitly historical/transcribed; the uploaded cloud AB package says the authentic 144-design and 359-window source matrix was not materialised in that work. Cloud B trace names and README explicitly say **SYNTHETIC** and use different capacities/fuel/efficiencies.
5. The present repository has an archive-replay utility, but requires complete frozen `Draft3A`, `Draft3B`, `Draft3C` folders with original manifests. Those folders are **not present** in the supplied GitHub checkout; replay cannot be claimed complete.

## Validation matrix

| Subject | New result | Evidence status | Remaining work |
| --- | --- | --- | --- |
| Baseline integrity | 166 source files with matching SHA-256 | **VERIFIED file identity** | Keep source ZIP accessible for future audits |
| Baseline Python tests | 53 regression tests pass | **VERIFIED software regression** | Does not validate original field assumptions |
| Baseline complete archive replay | Not executed | **NOT VERIFIED** | Obtain full sealed Draft3A/B/C traces and manifests |
| Original DG-only native MDT comparison | Archived reports show limited matched controlled case | **PREVIOUSLY DOCUMENTED LIMITED PARITY** | Fresh native run and fresh published evidence if required |
| Week 7 8,760-hour load accounting | Hourly power sums and per-equipment totals | **PYTHON VERIFIED** | Site survey; 120-person building and installed-load evidence |
| EV charging physics | Battery energy, mission reserve and charger limits | **PYTHON VERIFIED** | Real OEM batteries, charger integration, route/mission schedules and charging logs |
| Updated site normal grid adequacy | Original normal grid assumption 100 kW; new peak up to 225 kW | **NOT EVALUATED as grid-connected system** | Re-run grid-connected dispatch with import limits and connection policy |
| New islanded dispatch and ENS | Original S3 solver and source weather, same 24/72/168-hour start | **PYTHON VERIFIED energy balance** | Independent solver review, DG load-fuel calibration and electrical constraints |
| New capacity screen | Six of nine complete, three quarantined with exception | **PARTIAL** | Resolve same-hour charge/discharge dispatch conflict without violating model physics; repeat multi-season trials |
| New MDT/HOMER cross-validation | 0 new native solver executions | **NOT VERIFIED** | Set matching inputs; run actual software, save files/logs and quantify discrepancies |
| EV bidirectional power | No Vehicle-to-Grid discharge performed | **NOT IMPLEMENTED** | Confirm actual charger/vehicle islanding operation and reserve interlocks |
| Probability-weighted EENS | Not reported | **NOT JUSTIFIED** | Obtain probability-of-outage and scenario distribution before claiming EENS |
| Financial NPC/NPV | Not recalculated | **NOT DONE** | Approved tariffs, economic boundary, costs, asset replacement and scenario-year logic |
| Grid-forming and power quality | Hourly model assumes an AC reference | **NOT VERIFIED** | Stability, protection, black-start, voltage/frequency and transfer testing |

## Quarantine mechanism

`outputs/capacity_quarantined_issue_details.json` records the affected candidate, first failing hour and exception. None of these are assigned successful ENS or Critical EA figures. The inherited `Battery` model rejects charging and discharging in the same outer hour; the three failures are therefore code/model feasibility limits, **not proof the physical design is intrinsically impossible**. No controller bypass, silent capacity increase or error suppression was applied.

## Scientific reporting rules

- Use **scenario ENS** (kWh), **Critical Load Energy Autonomy** (fraction or percent), fuel (L), end SOC and indicative costs; do not use EENS unless probabilities are documented.
- Mark all demand inputs and vehicle capabilities as assumed design parameters, not MOD measurements or OEM guaranteed values.
- Report critical and non-critical service separately; do not treat a 100% *hourly* critical EA as uninterruptible real-time service.
- All Week 7 capacity/risk comparisons use a common 2025 winter start and 70% initial BESS SOC; they are neither weather statistics nor deployment-grade results.
