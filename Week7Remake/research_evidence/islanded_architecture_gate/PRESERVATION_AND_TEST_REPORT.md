# Preservation and Test Report

2026-11-21 · Windows · Python 3.12.10 · `PYTHONDONTWRITEBYTECODE=1` · All Python commands used `-B`

从干净本地 `27c48e4` 建立审阅分支 `research/islanded-architecture-and-dissertation-figures`。祖先检查确认 `f79f89e`、`2d58409`、`27c48e4` 都在活跃工作树；远端 `main` 为 `fca1878`，三个研究提交均未进入远端主线。架构审阅与图表库独立提交。

| 复验 | 实际结果 |
| --- | --- |
| Week7Remake 全回归 | **143/143 PASS**，`python -B -m pytest -q -p no:cacheprovider` |
| Initial Draft 独立回归 | **53/53 PASS**，同一入口在该版本目录 |
| Baseline 检查 | **142/142 public**，**166/166 full archive**，完整档案用 `check_preservation.py --archive-root` 指向原 `LC1-main` |
| EV regression fixtures | **3/3 PASS**，既有 SHA-256，`python -B -m week7.prepare_regression_fixtures` |
| Original package | **367/367 PASS**，私有 `PACKAGE_CONTENT_SHA256.csv` |
| Stage 7 outputs | **16/16 PASS**（Git），另 **16/16 PASS**（原工作档案），逐项按现存清单重算 |
| Stage 8 原始工件 | **324/324 PASS**，七份清单分别 62、7、46、68、34、78、29。两个 D1 文件目录所含 MOF 是历史组件资料，不是新的 integrated MOF。D1 gate JSON 在 Git 与档案逐字节一致 |
| 冬季记录独立账本 | **168/168 PASS**。从原始功率列复算 AC ≤2.843×10⁻¹⁴ kWh，BESS DC ≤2.132×10⁻¹⁴ kWh。Fuel、UPS 和各 tier 的独立余额至数值精度为 0。库存跨小时连续，grid import/export 全零 |
| 既有结果 | **PASS**。保存的 168 小时账本前缀与 HDH 比较中的 A 24/72/168 h Critical/Total ENS 一致。两侧 EA 由各自 Critical 分母重算一致。核查的是已有 Python 结果 |
| MDT D1 / HOMER / 电气动态 | **NOT RUN**。查阅现存日志、控制字段、原始工件清单和 Sandia 指南。未执行新增原生、容量或电气仿真 |

冬季 plant trace SHA-256 为 `8fe69e140b5a87e5f6639b84279ae59512d33af5ae11f2ce38eba26e49358a2a`。完整余额使用每小时功率×1 h，AC 包含 generated、dumped、charge/discharge、UPS 与三类负荷，DC 使用方向效率和 300 kWh 名义容量。经核对的本地 Sandia MDT Guide v1.4 已存于私有文献目录，SHA-256 `2d5fbdc67cee8c2f69c17d8652947dee7db3ac6c98e1f11090ea7aff5e808cf7`。此版可复用既有文献记录。 [冬季数据](../../week7/nextstage/outputs/winter_168h_original_equipment_plant_trace.csv) · [Sandia 2024 guide](https://www.sandia.gov/research/publications/details/microgrid-design-toolkit-mdt-user-guide-software-v1-4-2024-07-01/)

本审阅新增三份 Markdown、两份 CSV 和一份原创功能流 SVG，均在 `research_evidence/islanded_architecture_gate/`。Initial Draft、原有配置、报告、校验清单、Stage 0–8 输出及所有原始 MOF/MBF 不在变更中。另一个 DeepSeek 研究档案的历史记录曾报告一份用户保存的 legacy diagnostic input 漂移，属于另一套冻结清单。本轮未重置或重算该旁支的旧 545 项证据。

未解决的工程项包括真实 GFM/black-start 来源、UPS transfer、同步与保护、严格 D1 两个配置阻塞和 integrated telemetry。 [架构审阅](ISLANDED_ARCHITECTURE_AUDIT.md) · [D1 决定](VALIDATION_GATE_DECISION.md)
