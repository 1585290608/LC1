
# LC1 dissertation workspace

Cardiff University EN3400 · Hybrid Microgrids for Defence Applications · Writing and evidence synthesis

## Working documents

| File | Use |
| --- | --- |
| [Methodology](Methodology.md) | Fifteen source-linked methods sections with equations, worked examples, units, verification and evidence boundaries. |
| [Results](Results.md) | Draft numerical findings from the saved simulations and component benchmarks. |
| [Supervisor review](Supervisor_Review.md) | Review agenda, key findings, four existing figures and five open decisions. |
| [Figure plan](Figure_Plan.md) | Ten main-text and two appendix figures with English captions and source links. |
| [Evidence register](Evidence_Register.csv) | Parameter and result locators, source commit and SHA-256, evidence class and status. |
| [Writing roadmap](Writing_Roadmap.md) | Chapter order, available evidence and dependencies for drafting. |

Use the fixed 2025 source local solar time (LST) for chronological comparisons. Retain evidence labels when reusing tables and figures. Use **Critical** for the model's whole `c4isr` tier, including medical and security. Keep historical static EV runs distinct from later dynamic charging and mission feedback. Preserve the original MDT records and the dissertation figure masters in their existing locations. [Figure QA](../research_evidence/dissertation_figures/FIGURE_QA_REPORT.md)

The Sennybridge No 2 1991–2020 climate reference is available for the study-area chapter. The 2025 NASA POWER weather year remains the dissertation model input. [Climate reference and verification](../research_evidence/README.md#sennybridge-climate-reference)

## Version and provenance

The writing branch was cut from clean local `research/islanded-architecture-and-dissertation-figures` at `3a585167f49f226d88bac82e529c5ccdcc98f1b3`. All five commits below are ancestors of that point. Local `main` and the existing `origin/main` reference were both `fca1878d009a202f35852fa75853cbc6de7fe463` at inspection, with six local research commits beyond this base. No push, rebase or merge was required. The Git worktree inventory contained one active worktree.

| Commit | Research evidence used |
| --- | --- |
| `f79f89eb12433ce25aae199dd4db079fc3cdfbcb` | Minimum Evidence Sprint and the fixed-C2 literature comparator |
| `2d584094f8a314f6f8537bff034e69c80b594271` | Temperature calibration and frozen monthly reconciliation |
| `27c48e420a6516a8cb08009738f82ff1171d4e84` | Energy-neutral HDH and paired outage study |
| `34dc927f89b53ca72133e8c9be2364112aa2f1e5` | Islanded architecture review and D1 decision |
| `3a585167f49f226d88bac82e529c5ccdcc98f1b3` | Dissertation figure library |

Earlier methodology is preserved in the [Stage 3](../week7/stage3/docs/EN3400_methodology_draft_v0.3.md), [Stage 4](../week7/stage4/docs/EN3400_methodology_draft_v0.4.md), [Stage 5](../week7/stage5/docs/EN3400_methodology_draft_v0.5.md), [Stage 6](../week7/stage6/docs/EN3400_Methodology_Update_v0.6.md) and [Stage 7](../week7/stage7/docs/EN3400_Methodology_Addendum_v0.7.md) records. The [Stage 8 index](../week8/README.md) identifies genuinely native component evidence and the unresolved integrated gate. The archived original package, raw MOF/MBF and private catalogue remain in the research archive. [Publication and archive provenance](../docs/publication-provenance.md)

Register paths are relative to the Git repository root unless prefixed `ResearchArchive/`. That prefix identifies paths in the separate LC1 research tree without exposing a local machine address. `Source_Commit` is the latest commit affecting the referenced Git file at the evidence base. For local archive files it is labelled `ARCHIVED_FILE`, because their identity is established by hash. The Army comparator row points to the versioned audit and report table locator. The report PDF is not locally archived. Rows marked `PENDING_SOURCE_VERIFICATION` identify gaps rather than substituting unverified numbers.

## Verification of this consolidation

- PASS. Recalculated the 26,280 frozen load rows, their monthly and annual reconciliation, and the 8,760 timestamp/T2M pairs against the archived NASA data and saved HDH table. Recomputed the paired ENS and Critical EA denominators and the sums of 27 saved discounted cash ledgers. The 0.000188 kWh Central EV difference between the annual scheduler summary and serialised hourly total is explained by reporting precision.
- PASS. Existing Python 3.12 tests were rerun with `-B` and `PYTHONDONTWRITEBYTECODE=1`: Week7Remake 143/143 and Initial Draft 53/53. The three EV fixtures, all 142 public Baseline hashes, and all 166 full Baseline hashes passed. All 158 historical Initial Draft Git blobs match the original commit. The previously added migration note remains outside the original set.
- PASS. The Original Package inventory passed 367/367. Stage 7 output manifests passed 16/16 in Git and 16/16 in the archived working package. All 324 saved Stage 8 file hashes across seven manifests passed.
- PASS. The twelve chosen figure designs map to all 23 existing artwork files. Index digests, source links and the intended dissertation-only Git diff were reviewed.
- NOT RUN. Native and scenario simulations were not newly executed for this documentation task. D1 remains NO-GO / NOT RUN. The archived benchmark outcomes retain their original evidence classes.

The official Cardiff EN3400 submission brief was not found among the inspected Git files. The project supervisor or course material should confirm submission, formatting and assessment requirements. This workspace proposes no deadline, rubric or word limit.
