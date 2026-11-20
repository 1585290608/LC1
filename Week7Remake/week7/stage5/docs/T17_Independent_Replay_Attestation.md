# Stage 5 — Clean-Extraction Reproduction Check

**Date:** 19 November 2026

The delivered Stage 5 ZIP was extracted into an independent new folder before running any checks, without referencing the author's working directory. The test/replay sequence was:

```bash
python -B -m pytest -q -p no:cacheprovider tests week7/tests week7/nextstage/tests week7/stage3/tests week7/stage4/tests week7/stage5/tests
python -B week7/audit/check_preservation.py
python -B -m week7.stage5.run_study --out <new_empty_output_directory>
```

- **112/112** Python test cases passed from fresh extraction.
- **166/166** original baseline file SHA-256 checks passed.
- Eight deterministic Stage 5 output files (`stage5_T17_preflight.csv`, `stage5_T17_preflight.json`, `stage5_conditional_economic_comparison.csv`, `stage5_cost_sensitivity_full.csv`, `stage5_key_option_pairs.csv`, `stage5_run_metadata.json`, `stage5_sensitivity_winner_counts.csv`, `stage5_year_by_year_cost_ledger.csv`) were reproduced **byte-for-byte with identical SHA-256 digests**.
- The ZIP CRC/integrity self-test returned **no corrupt entries**.

This attests package reproducibility and internal arithmetic/self-consistency, **not** an independently calibrated simulation or actual Microgrid Design Toolkit/HOMER Pro verification. Stage 5 re-scores archived Stage 3/4 physical runs rather than recomputing all 1,508 Stage 4 hours-against-52-start contingency cases. No new native tool execution took place.

**Frozen cache warning:** historical 166-file manifest includes `.pyc` files. Use `python -B` for archive-preserving test runs; otherwise Python may rewrite compiled caches with different binary contents without modifying any source `.py` files.
