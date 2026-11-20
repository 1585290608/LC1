# T17 — Cross-software validation execution runbook

**Status:** an auditable *preflight/interchange package*, not a completed native MDT or HOMER Pro run. Native execution count for Week7 extensions: **zero**. This is a test protocol to run when licensed/accessible tools and the correct native input files are available.

## 1. Input data, provenance and unit semantics

Under `week7/stage3/external_inputs/`:

- `LC1_reference_profiles_8760.csv`: common **zero-based 2025 fixed LST** time axis, original PV/Wind normalized capacity factors, and provisional 120-person low/central/high requested critical/auxiliary/EV demand in kW. 1-hour intervals; no civil DST jump. This is a generic interchange CSV, **not a direct native MDT/HOMER project**.
- `LC1_108_external_case_manifest.csv`: 4 seasons × 3 durations × 9 candidates, all nameplate capacities, stationary BESS SOC/efficiency, diesel 100 kW, UPS, starting fuel, and controller assumptions. A separate 52-week sensitivity output exists and is not included in this 108-case native handoff.
- `LC1_DG_MDTCatalogue_Fuel_Curve.csv`: **actual** piecewise archived MDT-derived diesel ON-power fuel curve at 25/50/75/100 kW. Reject any substitution of the inactive `Settings.fuel_l_per_kwh=0.25` as if it were used for Stage3 model fuel consumption.
- `LC1_external_input_provenance.json`: SHA-256 of each input file.
- `external_native_results_template.csv` and `external_native_metadata_template.json`: empty result schema and **unattested** metadata; do not fill without an actual external solver run.

Every case requires exact source-hour alignment (`hour_index_zero_based`, first hour inclusive; duration 24/72/168), initial BESS SOC 0.70, 2,000 L fuel and identical tier definitions. Full `grid-connected` runs or inverter transients require a *separate* acceptance protocol.

## 2. Matching limitations that must be resolved before comparisons

| Topic | Python S3-v2 assumption | MDT/HOMER requirement |
|---|---|---|
| Load and weather | Fixed 2025 LST 8760h, centre case, PV/Wind scaling | Align time index, unit conversion and duration; no 1-based shift |
| Diesel | 100 kW; min ON 25 kW; 1 h start; segment-aware fuel exhaustion | Reproduce start and minimum/dump behaviour; archived piecewise catalogue curve, not 0.25 L/kWh constant |
| Stationary battery | 300/450/600 kWh, 90 kW PCS, SOC0.70 initial; 0.10/0.90 bounds; 0.30 dispatch reserve | Match battery throughput, losses and dispatch policy |
| Storage efficiency | 0.8944 charge × 0.8944 discharge per cycle | Ensure AC/DC round-trip definition is not applied twice |
| UPS | Nominal 30 kW/15 min interpreted as ideal AC 7.5 kWh | Explicitly model or exclude comparably; no transfer-time certification |
| Priority | C4ISR / medical / perimeter → Auxiliary → EV | Priority load shedding must be supported; no proportional native shortage if claiming tier parity |
| Control | S3-v2 hysteresis/commitment and preemptive no simultaneous same-hour BESS direction | Generic economic-tool default EMS is **not** equivalent; document deviation |
| Grid reference | Assumed AC reference in island operation; no grid-forming physics | Do not claim black-start, fault ride through or voltage/frequency parity |
| V2B | Disabled; EV charge-only mission coupling | No bidirectional discharge credit in base comparisons |

**Important:** Different control algorithms can give different energy balances despite identical capacities and weather. Mark `NOT_COMPARABLE_CONTROLLER` unless equivalent settings are demonstrated, then report numerical differences rather than forcing agreement.

## 3. Suggested native run order

1. Repeat controlled **DG-only** 24h using preserved historical case definitions to ensure the installed native software can open/export results. Historical parity is source evidence but is not new Week7 validation.
2. Run single-tier critical demand and no storage to check energy units and clock. Progress to three-tier priority dispatch, then add PV/Wind and BESS in separate matched benchmark increments.
3. For central provisional load, run 24h / 72h / 168h at 50/50/300, 75/75/450, 100/100/450 and 100/100/600 with the same full initial state. Extend to all 108 fixed-season cases once the smaller comparisons meet agreed tolerances and parameter policy.
4. Export *native* project files, solver version/settings screenshots or machine-readable settings, original output CSV, run log and relevant hashed results. Record how the native EMS differs if full policy matching is impossible.
5. For HOMER Pro, separately define permissible load priorities, resource year, lifetime, capital/replacement/O&M costs, fuel price and dispatch strategy. Only then run NPC sizing/optimal system search. Do not substitute nine-option illustrative CAPEX Pareto for NPC optimisation.

## 4. Conservative numeric comparison helper

`python -m week7.stage3.compare_external --native /path/to/native-export.csv --metadata /path/to/attested-export.json --out /path/to/comparison`

The comparator **rejects blank/inconsistent provenance** and checks profile, 108-case manifest and diesel-curve SHA-256 equality. Requires a manually signed-off equivalence flag, explicit native solver version and a checksum matching the actual exported CSV. The tool reports row-wise differences for Critical ENS, Aux ENS, EV ENS, Total ENS, Fuel, end SOC, and Critical EA. Default numerical comparison tolerance is max(0.001 kWh, 0.1% of magnitude), or max(0.0001, 0.1%) for SOC/EA fractions.

A user-supplied file and self-declared metadata are **not authentication** that native MDT or HOMER was actually used. Result status remains *reported native numerical comparison pending independent evidence review*. A failed or missing equivalence gate is recorded as NOT COMPARABLE rather than treating equal numeric values as validation.

## 5. Minimum acceptable validation evidence

- Original native input and source output files with matching SHA-256 and tool version.
- Evidence of matched clock, energy units, initial conditions, priority, dispatch, fuel law, and SOC limits.
- Per-case `native vs Python` residual table, with missing metrics explicitly marked.
- Explanation for any differences due to native control constraints, instead of re-fitting parameters until results match.
- If native functionality cannot reproduce the proposed controller, report **structural model limitation** and compare only supported benchmarks.

**Current outcome:** no native software available/used in this package, so T17 is **advanced preflight, external parity pending**.
