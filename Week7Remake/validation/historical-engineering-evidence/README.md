# Historical engineering evidence

[简体中文](README.zh-CN.md)

This index describes earlier engineering studies. The full reports, native
models and run directories remain in their original archives. On the original
computer, the Git-ignored `local-only/historical-evidence-locations.md` links
to those files. See the [scenario index](../../docs/scenario-index.md) for
the model and result files included in this checkout.

## Original MDT engineering studies

| ID | Research purpose | Coverage in this checkout |
| --- | --- | --- |
| D0 | Source provenance and study boundary | Derived input profiles. Original reconciliation report archived locally. |
| D1 | AC/DC interfaces, PCS and UPS | Original report indexed locally |
| D2 | Native MDT energy and reliability | Original report indexed locally |
| D2B | Event-scoped EA and EENS accounting | Original report indexed locally |
| D2C | Multiple random seeds and EENS definitions | Original report indexed locally |

The original MDT study and the later Python Draft studies have separate
version histories. The MDT `case_study_v6` and Python Remake V6 refer to
different versions.

## Remake versions

The V1 and V2 code hashes are recorded in the Draft 2 version map.
Reports for V3–V11 are archived in V11. V12–V16 each have a local workspace.

| Version | Research purpose |
| --- | --- |
| V3 | Physics, metrics and engineering acceptance checks |
| V4 | Representative system design and equipment evidence |
| V5 | Battery state-of-charge acceptance checks |
| V6 | Multi-objective comparisons and cross-tool validation scope |
| V7 | Validation evidence audit |
| V8 | Conditional resilience and model limitations |
| V9 | Running generator failure and continuity of the grid reference |
| V10 | Controlled Python calibration and preparation for native MDT comparison |
| V11 | Engineering evidence and model audit |
| V12 | Independent annual energy reconciliation and portable execution |
| V13 | Native MDT execution of 24-hour cases |
| V14 | Controlled diesel-only comparison under constant load |
| V15 | Hybrid event timing, storage and energy comparison |
| V16 | Final audit of battery state of charge and critical load priority |

V13 documents completed native runs and result readback. V14 established
limited parity for the constant-load diesel-only diagnostic cases. The hybrid
comparison in V15 remains `PARTIALLY_COMPARABLE`.

## Original MDT work packages

These engineering work packages use a separate numbering system from the
economic operating scenarios. Acceptance scope and outstanding work are
recorded in the original MDT implementation plan.

| ID | Research purpose |
| --- | --- |
| P0 | Preserve baselines and trace inputs to results |
| P1 | Diagnose unserved load during startup |
| P2 | Reconcile resilience metrics and denominators |
| P3 | Verify topology and startup support |
| P4 | Model solar and wind generation |
| P5 | Review reliability assumptions and stochastic behaviour |
| P6 | Analyse fuel and dispatch |
| P7 | Define economic metrics and cost scope |
| P8 | Search the design space |
| P9 | Check robustness and document the final recommendation |
