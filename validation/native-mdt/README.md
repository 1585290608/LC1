# Native MDT cross-validation evidence

These tables accompany the [EN3400 results and discussion](../../docs/en3400-results-and-discussion.md). The study uses representative Sennybridge-area load and weather inputs. The stress cases deliberately vary source availability, load and controller settings.

## Reproduce the published checks

Run this command from the repository root with Python 3.12.

```powershell
python validation/native-mdt/verify_evidence.py
```

The script uses the Python standard library to verify public CSV hashes, reconcile supply with feeder service and battery charging, check contiguous native time intervals and recover the reported native SOC weight above 80%. It also checks the archived diesel metric pairs and OpenDSS snapshot balances. For the Python model tests and existing archive replay, use the [repository instructions](../../README.md#quick-start).

The published checks replay the reported calculations from the tables. A native rerun requires the locally archived MBF and matching private specification catalogue, Sandia MDT 1.4.2513.0, Sandia PyMDT 1.4.2520 and SQL Server LocalDB. The native runs used a fixed seed of 20261104. The local archive retains the inputs, MOFs, solver logs, admission receipts and separate-process readbacks. The manifests identify these files by SHA-256.

## Evidence inventory

| Table | Coverage |
| --- | --- |
| [Case manifest](case-manifest.csv) | Native version, seed, input kind, rating, controller and content hashes for 13 accepted runs. The SOC setting is the configured target. |
| [Event results](event-results.csv) and [section service](section-service.csv) | Full-event energy by source and feeder, fuel in litres, sampled SOC extrema and peak battery discharge when present, and the AC energy residual. The feeder table preserves each original demand denominator and 8,760-value profile hash. |
| [Diesel parity](diesel-parity.csv) | 25 validated metric pairs from the archived V14 constant-load controls and V15 24-hour D0 case. The constant-load 24-hour repeat is retained. |
| [Telemetry manifest](telemetry-manifest.csv) and [solver intervals](solver-intervals.csv) | Five instrumented reruns and their 309 measured model-clock intervals. These are solver boundaries, with no component-state columns. |
| [SOC bins](soc-bins.csv) and [C2 SOC comparison](soc-comparison.csv) | Native SOC-bin duration weights and the aligned V15 Python comparison. The 72- and 168-hour native results pool corresponding clock hours across days. |
| [Electrical snapshots](electrical-snapshots.csv) | Eleven steady-state OpenDSS results for the modelled AC topology, including explicit PCC states. |
| [Data manifest](data-manifest.csv) | SHA-256 of every published data table and its source artifact in the local research archive. The source artifacts and individual native files have separate digests. |

The D0 C2 windows start at zero-based profile index 24, corresponding to 2 January 2025 00:00 in the source local solar time (LST) calendar. The model-clock export does not establish a time-zone conversion or a field outage timestamp. The native time-of-day SOC buckets were exported in the run process. Reopened MOFs retained aggregate SOC moments and returned empty time-of-day histograms. Chronological SOC, component power and breaker contact records remain open.

The AC readbacks establish energy/service accounting for the tested cases. Field equipment performance, switching and protection acceptance remain open. The [historical engineering evidence index](../historical-engineering-evidence/) provides the earlier model context.
