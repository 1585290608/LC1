# Draft3B validation report

Status: PASS_SCOPED_NUMERICAL_STUDY. Cost/permission/equipment assumptions remain unverified.

- 28 tests passed (15 unchanged Draft2 tests included);0 failures/errors.
- 12 distinct8760h annual cases;105120 time steps independently re-read from saved CSVs.
- Maximum hourly AC residual 1.776e-14kWh;DC 2.132e-14kWh. No terminal SOC reset; every hybrid starts/ends0.70.
- Every physical case checks finite inputs, exact2025 sourceLST timeline/index alignment, input weather/load hashes, power/energy balance, efficiencies,90kW PCS,100kW assumed import cap,0/20kW assumed export cap, no simultaneous import/export or battery directions, no routineDG/UPS output.
- P0/P0R have no BESS; SOC is not applicable. No fictitious battery state imposed.
- Independent CAPEX quantity/rate/boundary checks; generic O&M on CAPEX excludes working inventory; BESS_DC and PCS line items disjoint by explicit assumption.
- 16 independent21year cashflow checks: closed-form annuityNPC plus replacement/working-capital flows, matched-priceP0R comparator, undiscounted/discounted sustained payback. MaximumNPC difference GBP1.397e-09.
- 12 annual traces replayed byte-identically,16 economic records reproduced. Archive extraction/independent-path test recorded beside final ZIP.
- No quarantined main result; low-price/weak-wind failure to pay back is an economic finding, not a result to delete.
- Official grid factor archived and traced to Scope2 totalCO2e J3066, not CO2-only row; underlying data2023/reporting edition2025.
- Frozen input/core/source preservation proof: Evidence/FINAL_PRESERVATION.json. No external physical/MDT/HOMER/economic-quotation validation claimed.

Evidence: Processed_Data/ENERGY_VALIDATION.csv; FINANCIAL_VALIDATION.csv; Results/Annual/*/CONFIG.json,DISPATCH.csv; Results/Financial/*/CASHFLOWS.csv,INCREMENTAL_VS_P0R.csv; Evidence/REPRODUCIBILITY.json; TEST_RESULTS.xml.

Limitations: flat prices and constant real costs, one repeated2025year, no aging/standby/test fuel data, no independently verified EPC/package scopes or warranties, no actual grid export agreement or MOD tariff, no monetised outage benefit. 48h terminal management is a prescribed accounting control, not P2 price optimisation. Fractional payback interpolates annual snapshots; first sustained nonnegative year-end is the ceiling year where applicable.
