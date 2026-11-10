# Replay against frozen results

Run from the repository root. Supply the local `Validation` folder that
contains `Draft3A`, `Draft3B` and `Draft3C`, each with its original manifest and
results. For example, if the projects are siblings:

```powershell
python -m validation.replay_saved_results "../LC1 Remake/Validation"
```

The replay first checks the original file hashes. It compares new dispatch
records and service ledgers byte-for-byte, checks annual metrics, then compares
the financial outputs and cashflows. The winter resilience baseline is
accounted for as a reused strategy trace. This command reads the archives
and prints its findings. It checks Python migration equivalence within the
archived test scope. See the research reports for native solver evidence.

The GitHub checkout contains selected result tables. The full hourly traces
and cashflows used by this command are in the frozen original studies.

## Repository migration check

The consolidated checkout passed 53 distinct existing tests. The four prior
snapshots ran 116 test instances because they shared copies of test modules.
The archive replay matched 24 strategy traces, 17 newly generated historical
contingency traces, the reused winter trace, all 18 service ledgers, 12 annual
grid traces and 16 financial outputs. This covers 110,760 distinct hourly
rows across the 53 independently replayed traces.
