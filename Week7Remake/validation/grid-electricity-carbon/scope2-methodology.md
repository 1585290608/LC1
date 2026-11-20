# Draft3B carbon supplement,2026 official factor

Only Scope2 results updated in this separate folder. No physical/economic simulation rerun, no original output overwritten. Eight original2025 hourly annual cases,8760LST hours each, were copied byte-identically and checked with Decimal arithmetic from every grid_import_kw*dt_h row. Source/rawdata/hashes are retained.

## Factor and boundary

DESNZ2026 methodology Table9, data2025, PDFpage35, gives0.13096kgCO2e/kWh generated/supplied to grid includingimports. Official revisedJuly flat file independently confirms the Scope2/UK electricity/Electricity generated/totalkgCO2e row. Original0.17700 is retained as archived2025 edition (underlying2023data), not silently replaced. Table8's0.15564 excludesimports and is not used. Scope3 T&D0.01299 and consumed total0.14396 are not added; WTT and embodied carbon excluded. No export avoided-emissions credit. DG Scope1 is separate; normal-year modeledDGfuel is0, but actual exercise/testing emissions are not certified or inferred.

Annual Scope2=existing purchasedkWh*factor. Absolute avoidedScope2 relative to same-yearP0R=baselineScope2-caseScope2. Percentage=(baseline-case)/baseline*100. P0 andP0R have identical normal electricity demand; both are provided. All percentage reductions remain identical under a common positive factor; changed absolute tonnes reflect factor/boundary/data-edition selection, not an improvement in physical dispatch.

For P1 E20/R30, updatedScope2=21.656497tCO2e/year, absolute reductionvsP0R=31.115145t and percentage=58.961867%. Original and updated values for everyP0/P0R/P1/P3 case are in CARBON_COMPARISON.csv.

## Economics and preservation

All310 originally sealedDraft3B files and original economic ZIP reverified unchanged. NPC/payback/CAPEX/O&M remain byte-identical; this supplement creates no revised financial result. Initial/terminalSOC and export-approval limitations from Draft3B remain. OriginalScope2 fields in oldSCENARIO_COMPARISON.csv intentionally keep0.177; consult the separately versioned supplement when using the updated estimate.

Official HTML, methodologyPDF, revised-flatExcel, access/publication dates, SHA256 and BibTeX are in Reference/Research documents. Evidence includes full relevantPDF pages, exactflatrow, rowwise-vsaggregate checks and financial-file hashes. This is a normal-year location-based carbon accounting update, not a complete life-cycle or military emissions assessment.
