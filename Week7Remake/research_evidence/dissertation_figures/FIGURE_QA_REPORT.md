# Dissertation figure quality and evidence checks

Review date 21 November 2026. The active data baseline is local Git commit `27c48e4` plus the versioned architecture audit. The library contains 12 figure designs. Eleven are original renderings from saved tables and one is a byte-identical SVG copy of the architecture audit drawing.

## Inventory scope

| Location | Image and figure files |
| --- | ---: |
| Initial Draft in Git | 32 |
| Week7Remake in Git before this audit | 61 |
| Archived Stage 7 working copy | 45 |
| Archived Stage 7 frozen package | 45 |
| Private research Image and MDT trees | 69 |
| Published-format local research outputs | 15 |
| Local research build source artwork | 79 |
| Located legacy source-map originals in Downloads | 6 |
| **Total inventoried file paths** | **352** |

The inventory has **144 distinct SHA-256 values** and **208 redundant paths** in 73 exact-duplicate groups. The count includes historical figures, plot exports in different formats, diagrams and screenshots in the research scope. Whole reports, slide and page previews, dependency assets and unopened backup ZIPs are out of scope. Absolute private-machine paths are represented by root aliases. `ResearchArchive` is the separate DeepSeek engineering research tree. `ResearchOutputs` and `ArchivedResearchBuild` are the ChatGPT research archive's outputs and local build source folders. `Stage7Archive` refers to the archived complete Stage 7 package. `Downloads` identifies legacy figure files in the migration source map. `LIBRARY_SELECTION` index rows are additional to the original count.

No stand-alone graphics were found in the Minimum Evidence Sprint or in the inspected native Stage 8 directories. Figure 10 summarises saved component benchmark decisions directly from JSON. It does not create or select native measurement traces. The inventory flags 199 original paths with unconfirmed exact plotting inputs or missing provenance, including duplicate legacy copies. A linked companion report does not by itself identify the chart's exact input series. The 31 rights-sensitive or untraced assets marked `DO_NOT_REPUBLISH` were not copied.

## Checks

| Check | Result |
| --- | --- |
| Output formats | **PASS**. 11 embedded-font vector PDFs and 11 PNGs at 2,760 × 1,740 px and 300 dpi. The audit SVG is XML-valid and byte-identical to the versioned original. |
| Reproduction | **PASS**. Two fresh renders produced the same SHA-256 for all 23 selected files in the same Windows environment. Each copied file agrees with the replay hash listed in the index. |
| Layout | **PASS**. Checked the figure set with reduced-size proofs and moved the dispatch and cost legends away from the plotted values. The PDF artwork is scalable and small panels should use full A4 text width. |
| Load figures 02–04 | **PASS**. 12 monthly rows and 8,760 hours per case. Modelled Low, Central and High sum to 682,535.156465, 763,901.095464 and 871,656.369552 kWh respectively. The 15 end uses sum to the Central monthly and annual totals. Month lengths are accounted for in kWh/day. |
| Resource figure 05 | **PASS**. Both frozen series have contiguous indices 1–8,760 and finite values in [0, 1] p.u. Hourly means are 0.126102779 for PV and 0.429182015 for wind. Both profiles express modelled availability before dispatch. |
| Dispatch and outage figures 06–07 | **PASS**. The saved Original winter active-energy ledger reconciles over 168 rows. Critical and total ENS are in kWh, fuel is in L and Critical EA is the fraction of Critical energy served expressed in percent. Tier ENS and EA were recalculated for all six case/window combinations within 10⁻⁷ in the displayed units. |
| Cost and grid figures 08 and A02 | **PASS**. Nine Central points meet the saved annual service screen at 250 kW import and ≤10⁻⁶ kWh annual requested-service shortfall. The grid sensitivity plots seven saved limits per case. The cash proxy and deterministic mean islanded ENS retain their separate definitions. |
| Heating figures 09 and A01 | **PASS**. At the plotted 15.5°C balance point, total annual electricity and heating are conserved within 10⁻⁷ kWh against Original Central. Heating is 72,768 kWh/year and its timing is synthetic. The week plot uses the first 168 saved demand hours. |
| Validation figure 10 | **PASS for faithful transcription**. The DG-only tank state and P2/W2 event/state remain inconclusive. B1/B2 end SOC is derived. B3 had an accepted reserve event while its fixed hourly requirement failed. The D1 saved status records NO-GO, zero native runs and no integrated MOF. |
| Historical preservation | **PASS**. Research graphics were read without changes. Stage 7 rerun was 143/143 and Initial Draft 53/53. Public/full baseline hashes passed 142/142 and 166/166, the private package 367/367, Stage 7 outputs 16/16 in both copies, and Stage 8 historical evidence 324/324. See the independent preservation report for scope. |

All regenerated plots share a British English style, fixed 2025 LST where applicable, explicit electrical/energy units, and a consistent palette for technology, load categories and cases. The architecture shows a functional model and energy flow. Figure 10 describes the scope of reported validation, including unresolved physical states. Neither graphic implies commissioning, uninterrupted service or grid-forming proof.

## Reproduction

Run from the Week7Remake directory using the existing Python 3.12 environment with Matplotlib. Use a fresh temporary directory. The script opens destination files exclusively.

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$figureReplay = Join-Path ([IO.Path]::GetTempPath()) ("LC1-figure-replay-" + [guid]::NewGuid().ToString("N"))
python -B -m research_evidence.dissertation_figures.build_figure_library --output-dir $figureReplay
```

The script reads frozen CSV/JSON and the new architecture SVG. It does not run a simulation. Use the index to compare the SHA-256 for the PNG, PDF and SVG results. Rendering by a different Matplotlib or font build may change file bytes while preserving the numerical input.

[Inventory](FIGURE_INDEX.csv) · [Captions](FIGURE_CAPTIONS.md) · [Figure choices](FIGURE_SELECTION.md) · [Architecture preservation and tests](../islanded_architecture_gate/PRESERVATION_AND_TEST_REPORT.md)
