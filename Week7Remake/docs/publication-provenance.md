# Public distribution and archive provenance

## Source of the migration

- Frozen GitHub baseline `228c005aa47bdee720524d152e56c10c5d4a7cd3`. The local reference `archive/initial-draft-20261120` points to this commit.
- Revised Python source and Stage 7 results come from the verified `LC1_Complete_Stage7_Local_Codex_20261119/LC1_working` research package. The original package manifest SHA-256 is `0a6ffd131d4eed03715e38085908bee186a0ec43a8cb3775580f485ad15d7a24`.
- The Stage 8 controller gate was resolved on 20 November 2026. The local D1 gate evidence manifest SHA-256 is `e363a0c51f2a33fd7fbe3cf0d1b8681641ab871bc17971dc1b120bf0b3891eb8`. The frozen integrated Python fixture manifest SHA-256 is `c4d223d3a0a6080bdafcbead1a3086340d9005a40365f3172c7ccf7c8aa478ad`.
- The literature evidence ZIP SHA-256 is `989a9871a982635d92a64908894087b4cb07899c73879cd7eda4c6204673f5c4`. Source definitions and access limitations are summarized in the [research evidence index](../research_evidence/README.md).

[Publication source map](PUBLICATION_SOURCE_SHA256.csv) identifies the original archive-relative path and both original and published digests. Changes for the Git layout are limited in the imported model tree to the baseline audit and the Stage 5 preflight that calls it. The new regression fixture helper regenerates only missing EV CSVs. Original Python tests, numerical constraints and archived evidence are preserved.

## Evidence scope and reproduction

The [public baseline scope](../week7/audit/public_baseline_scope.md) explains which files can be checked from a clone. All 166 historical SHA-256 checks use the original archive. The separate 158-file GitHub baseline is preserved as the `Initial Draft/` tree. File integrity and passing software regressions each apply to their own scope.

The public checkout includes original Python configuration and synthetic data needed for regression, including annual and islanded traces read by tests. It retains the 16 hashed Stage 7 outputs. The three larger per-vehicle traces are regenerated from versioned inputs and checked against the [archived trace digests](../week7/audit/ev_regression_fixture_sha256.csv). The local archive holds original proprietary MDT models and raw outputs, SQL local databases, third-party PDFs, logs with machine paths, development and reproduction scratch copies, and other larger results. Publication did not move or delete those records.

The original chronological reports in the `week7/` subdirectories describe their own stage and its then-current evidence. Run the [current quick start](../README.md) for this checkout. Use a separate copy for commands that regenerate saved output files. Inspect [Stage 8 outcomes](../week8/README.md) before citing native comparison results. Complete archived Draft3A/B/C replay, joint MDT/HOMER validation, site engineering and production stochastic calibration remain unverified.
