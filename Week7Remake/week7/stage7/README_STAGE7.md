# LC1 Week 7 Stage 7 — native validation-ready audit, not new native validation

Original model and Stage 0–6 files are unchanged. Stage 7 is an isolated new directory.

## Reproduce

From the root `LC1-main` directory (requires Python 3.11+ / pytest):

```bash
PYTHONDONTWRITEBYTECODE=1 python -B -m week7.stage7.make_outputs
PYTHONDONTWRITEBYTECODE=1 python -B -m pytest -q -p no:cacheprovider tests week7/tests week7/nextstage/tests week7/stage3/tests week7/stage4/tests week7/stage5/tests week7/stage6/tests week7/stage7/tests
PYTHONDONTWRITEBYTECODE=1 python -B week7/audit/check_preservation.py
```

`outputs/`: analytical metrics; independent audit of five archived traces; 27-case 20-year cash PV reconciliation; 567-year line items; SHA-256 manifest.

`external_handoff/`: 4 × 8760 single-column fixed-load kW text files for HOMER primary-load import; CSV manifest with SHA-256, totals and peaks; external native result **blank** template and metadata template.

`docs/`: T17 validation runbook and precise evidence boundaries, Methodology v0.7 addendum, T09 financial ledger report and T20 supervisor decision handoff. All are draft/unapproved.

To compare **real external results supplied in the future** (never fabricate them):

```bash
python -B -m week7.stage7.native_handoff \
  --native path/to/real_native_export.csv \
  --metadata path/to/signed_source_metadata.json \
  --out path/to/new_comparison_results
```

The native comparator will reject missing metadata, nonmatching checksums and unattested controller equivalence. It can never independently authenticate claimed solver origin. **No new native MDT / HOMER Pro software run is included.**
