# LC1 Week 7 Stage 4 — T10/T16/T17 Extension

**Policy:** additive research extension only. Previous `week7/`, `week7/nextstage/`, `week7/stage3/` models, the 166-file source baseline and all prior output records remain unchanged.

### To reproduce

From the extracted `LC1-main/` root with installed dependencies:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python -m week7.stage4.run_study
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python -m week7.stage4.plots
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python -m pytest -q tests week7/tests week7/nextstage/tests week7/stage3/tests week7/stage4/tests
python week7/audit/check_preservation.py
```

`run_study` reproduces 1,508 deterministic static-load scenarios, 52 dynamic EV runs, 780 archived Stage3 numerical metric comparisons and a SHA-256 output manifest. It does not use external native software. For a new clean output folder, use `--out /tmp/my-stage4-results` (therefore existing results are not overwritten).

### Core outputs

- `outputs/stage4_52start_contingency_full.csv`: all 1,508 source-window/capacity/policy combinations.
- `outputs/stage4_52start_contingency_summary.csv`: paired 52-window mean, percentile, worst, and Critical ENS count metrics.
- `outputs/stage4_accepted_refuel_events.csv`: requested, accepted and unaccepted fuel per simulated hour-start arrival.
- `outputs/stage4_13start_EV_mission_feedback.csv`: 52 runs coupling charging ENS to seven assumed vehicle SOC states.
- `outputs/stage4_stage3_baseline_parity.csv`: 780 numerical parity comparisons to archived Stage3 cases.
- `figures/*.png`: reproducible figures for the dissertation draft (not externally validated).

### Claims not supported

These simulations cannot establish real site loading, operational fuel-delivery feasibility, DG failure probability/MTBF, actual V2B/V2G capacity, native MDT/HOMER parity, full NPC optimisation, protection, transient stability or reliability certification. Do not use `0/52` as a failure probability or a safety guarantee.

**Bytecode preservation note:** The historical source freeze includes 21 `.pyc` artefacts. Set `PYTHONDONTWRITEBYTECODE=1` when running tools from the ZIP to prevent them from being regenerated with new paths; new `.pyc` files would change their hashes even though source code remained unchanged.
