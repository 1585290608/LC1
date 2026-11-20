# Stage 5 — LC1 Conditional Cost–Resilience–Fuel Logistics and T17 Preflight

This add-on does **not** modify frozen base models, Stage 3/4 outputs, physical source data or the original historical parameter file.

To reproduce:

```bash
cd LC1-main
python -B -m week7.stage5.run_study
python -B -m week7.stage5.plots
python -B -m pytest -q -p no:cacheprovider tests week7/tests week7/nextstage/tests week7/stage3/tests week7/stage4/tests week7/stage5/tests
python -B week7/audit/check_preservation.py
```

Core files: `economics.py` (actual financial mechanics), `run_study.py` (15 alternatives, 486 parameter combinations, validation preflight), `preflight.py` (source integrity, T17 status), `plots.py`, `config/cost_scenarios.json`, `tests/test_stage5.py`.

**Financial language:** `selected_20y_cashflow_PV_gbp_NOT_NPC` is not full net present cost. `generalised_score_PV_gbp_NOT_NPC` additionally includes explicitly *non-cash illustrative* energy shortfall valuation. Neither implies a verified economic optimum, power quality, or 100% reliability.

All study outcomes refer to equal-spaced 52 starts from the **single provisional 2025 fixed-LST year**, each independently reset with initial fuel/SOC. Counts are descriptive, not probabilities; outputs do not compute EENS.

Native MDT/HOMER Pro reruns: **none**. External cross-validation remains gated; a result comparison needs genuine native exports and signed-off equivalent assumptions. Stage5 does not attempt to operate proprietary tools via generic CSVs.

**Important preservation note:** the historic frozen source manifest includes 21 compiled `__pycache__/*.pyc` files. Run Python with `-B` (do not create new bytecode) when executing this archived research bundle, so routine Python/pytest imports do not rewrite these preserved binary artifacts. If non-`-B` imports mutate them, restore original archived `.pyc` files from the parent Stage4 ZIP before verifying all 166 frozen hashes. Source `.py` files and 2025 data remain protected by their own hashes.
