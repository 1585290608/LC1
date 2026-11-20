# Stage 8 validation and evidence

The tables below describe saved controlled component tests in MDT 1.4.2513.0 and one integrated controller gate. The public distribution contains reviewed result tables and status records, with raw MOF/MBF, SQL catalogues, original logs and solver diagnostics retained in the local research archive. Native records, interval reconstructions and independent Python data retain their source designations.

| Case | Results and limits |
| --- | --- |
| DG only | [Comparison](t17_native_mdt_v1/comparison.csv). 1 h and 24 h aggregate agreement. The 24 h fuel-depletion test has visible 10 h + 14 h native intervals and fails the fixed 1 h stepping requirement. [Temporal reconstruction](t17_temporal_v1/derived_hourly_comparison.csv) uses exact overlap. |
| BESS B1 / B2 / B3 | [Native status](t17_bess_native_v1/BESS_VALIDATION_STATUS.json). Aggregate PASS for all three. Event/physical state INCONCLUSIVE for B1/B2 and PASS for the B3 3.5776 h reserve cutoff. Fixed 1 h PASS for B1/B2 and FAIL for B3. Terminal SOC is derived when no direct endpoint is exported. |
| PV/Wind P1/P2/W1/W2 | [Native status](t17_pv_wind_native_v1/PV_WIND_VALIDATION_STATUS.json). Validates available-power fixtures. P2/W2 event and physical state remain INCONCLUSIVE. Irradiance-to-PV and wind-speed-to-power-curve conversion are outside these available-power tests. |
| PV 2 h observability | [Status](t17_pv_observability_v1/PV2H_STATUS.json). Aggregate and visible 1 h clock PASS; directly timestamped power state INCONCLUSIVE. |
| DG+BESS D1 | [Gate status](t17_dg_bess_native_v1/D1_GATE_STATUS.json). Native DG minimum is 40 kW versus 25 kW in the locked Python fixture. Independent 10% hardware floor plus 30% operating reserve could not be mapped. Controller feasibility NO-GO and native NOT RUN. The [Python event reference](t17_dg_bess_fixture_v1/DG_BESS_PYTHON_EVENT_REFERENCE.csv) predicts a 1.192533333 h cutoff. |

[Selected literature evidence](../research_evidence/README.md) · [Archive provenance](../docs/publication-provenance.md)
