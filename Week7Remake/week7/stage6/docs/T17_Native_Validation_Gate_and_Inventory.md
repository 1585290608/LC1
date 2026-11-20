# Stage 6 T17 — Native solver validation gate (open)

**State: `INTERNAL_PYTHON_CHECKS_PASS; NO_NEW_NATIVE_RUN`.**

Archive filename inventory on 19 Nov 2026: `Research documents.zip` (93 entries), `LC1_cloud AB.zip` (96), original `LC1-main Github 10_11_2026 time1515.zip` (170), and Stage 5 package (329). No file with the inspected candidate native-project suffixes `.homer`, `.hmp`, `.hmd`, `.mdt`, `.hmr`, `.hmod`, `.sim` was found. Filename inspection alone is **not** proof no other compatible project type exists; it is no substitute for an installed/licensed MDT/HOMER environment or actual exports.

- Preserve historical DG-only 24-hour MDT comparison **as historical DG-only evidence only**.
- Native MDT: create a genuinely equivalent 24-hour *critical-only, isolated DG* benchmark first, then an independent PV/Wind hourly output comparison and BESS one-hour charging/discharging component comparison. Require clock, fuel model, startup delay, initial SOC and reserve, load tier priority and AC reference to be documented before any 168-hour hybrid case. Version/export checksums must be logged.
- HOMER Pro: require licensed software, the actual project and software-version metadata and actual 8,760h load/resources with a documented converter and fuel-model mapping; do not equate a financial-model NPC with the Stage 5/6 partial cash-flow proxies.
- If the native model does not support the three service tiers, controlled EV mission SOC, mid-event fuel arrival or generator outage: label the comparison `NOT_COMPARABLE_CONTROLLER` / `UNSUPPORTED_FEATURE`, do not silently downgrade the research logic.
- Existing tool `week7/stage3/compare_external.py` accepts user-provided native exports *only after* an equivalence attestation and source checksums. It cannot independently authenticate solver origin. Its 108 historical reference scenarios are not the new 81 normal-year grid-connected results.

**Claim classification:** 126 total Python tests + all Baseline file hashes do **not** equal independent numerical solver validation. New native MDT runs: **0**. New HOMER Pro runs: **0**.
