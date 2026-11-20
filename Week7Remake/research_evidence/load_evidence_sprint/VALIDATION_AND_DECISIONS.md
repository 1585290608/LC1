# LC1 Validation and Decisions

2026-11-20 · Minimum evidence sprint · EN3400

## 概念电气边界

**单线概念。** PV inverter、Wind converter、DG（可作为 AC reference 的假设之一）与 BESS 经独立 90 kW PCS 接入假定已建立电压/频率参考的 islanded AC bus。Critical load bus 为假定 UPS 支持的负荷，Auxiliary 与单向 EV charging 分别计量及调度。启动期间 UPS 计量补给，DG 或其他经确认的电源接管后由母线供电。此 one-line 只定义 energy-accounting 边界。 [基础能源模型](../../models/core/simulate.py) · [服务台账](../../models/islanded/service_dispatch.py)

| 边界 | 判定 | 依据 |
| --- | --- | --- |
| Python 能量与分级服务 | **PASS，限数值模型** | Tier order 为 Critical > Auxiliary > EV。已有 S3-v2 控制器限制同小时 BESS 充放电。原有效窗口的 S3-v2 一致性由既有回归和 Stage 4 parity 记录支持。 |
| Grid-forming / black start | **UNVERIFIED · EVIDENCE_GAP** | `ac_reference_assumed=True` 是能量模型预设。DG 不在线时由哪台设备形成并维持参考、BESS PCS 能否 grid-form、可再生是否允许并网到该母线、切换瞬态均无本轮验证证据。 |
| UPS 过渡与连续 Critical 服务 | **UNVERIFIED · EVIDENCE_GAP** | 30 kW、15 min 对应理想 AC 7.5 kWh，算术上小于 35–41 kW Critical 总需求的整段覆盖。单独 UPS 支持还受 kVA、power factor、负荷启动、BESS/DG 启动与转换窗口影响。核心默认 DG 冷启动 1 h 同样只是能量模型参数。小时或分段 ENS 台账不建立无中断证明。 |
| 保护与设备配置 | **UNVERIFIED · EVIDENCE_GAP** | 需要电气工程审查和经过许可的设备资料来确认额定电气能力、切换、保护与现场工作边界。当前输出支持概念比较。 |

本轮未修改 `Settings`、dispatcher、UPS 或 priority 分配。水处理仍保留在现有 Auxiliary，EV readiness 由车辆状态另算。 [Stage 4 baseline parity](../../week7/stage4/outputs/stage4_stage3_baseline_parity.csv) · [既有 S3-v2 和 EV 验证](../../week7/nextstage/validation_update.md)

## MDT D1 与 HOMER

[Stage 8 D1 gate JSON](../../week8/t17_dg_bess_native_v1/D1_GATE_STATUS.json) 的结论保持 **Controller Feasibility NO-GO，strict parameter equivalence FAIL，native 2 h NOT RUN**。Python 固定 100 kW DG 的最低利用率为 **25%**，已检查的 MDT 1.4.2513.0 PRM 为 **40%**。两者在预期 100 kW setpoint 不触发该下限，但定义仍不等价。Python 的 BESS 物理地板 10% 与运行储备 30% 为独立约束。MDT 单一 SOC 下限 30% surrogate 可以表示某个有效 cutoff，无法保留两个独立约束。90 kW AC charge/discharge boundary 及方向效率的组件证据已有记录。D1 的 integrated dispatch order、initial SOC、load priority 和 telemetry 仍需确认。锁定 Python 事件参考 **1.192533333 h** 不包含 native 样本。 [参数映射](../../week8/t17_dg_bess_native_v1/DG_BESS_PARAMETER_MAPPING.csv) · [历史组件判定](../../week8/README.md) · [Stage 7 T17 边界](../../week7/stage7/docs/T17_Validation_Evidence_and_Gaps.md)

- **A · 当前决定。** 保留严格 NO-GO。Integrated aggregate、event timing、native fixed 1 h、direct SOC/fuel telemetry 与 MOF reread 维持 **NOT RUN**。现有 control-semantics 仍 **INCONCLUSIVE**。历史 DG/BESS/PV/Wind 组件结果按各自报告的 aggregate、event 和 native clock 判定使用。
- **B · 条件成立才启动。** 取得实际 MDT controller 文档及原生配置 readback，证明可设置相同 DG 下限并分别表达物理 SOC floor 与 operating reserve。然后在独立新目录锁定两端异常策略、负荷分组、初始状态、90 kW AC、AC/DC 边界及能量/事件公差，使用 2 h fixture 验证。两端如采用新参数，应以新版独立 fixture 命名，保留原 D1 判定。保存原生 clock、MOF、日志和直接遥测。派生小时量应单独标注。B 条件目前 **EVIDENCE_GAP**，未启动。
- **HOMER Pro。** 本轮 **NOT RUN**。若 EN3400 要求经济结果的独立软件比较，可用现有 8,760 h handoff，在价格、年界勾稽、AC 服务、充电、电量和 fuel 输入等价后做最小 service-matched 对照。HOMER 经济或小时平衡不能判断 UPS 瞬态、grid-forming 或 Stage 4 动态 EV 任务等价。 [HOMER handoff](../../week7/stage7/external_handoff/stage7_HOMER_import_manifest.csv)

## 本轮实测的软件与保存检查

采用既有虚拟环境 Python **3.12.10**，`PYTHONDONTWRITEBYTECODE=1`。Git 根目录为 `LC1_Github`，起点 `db3256e4f572bcd04b9d04d99ad5d25a9c872547` 的工作树干净，来自 `main` 的原分支含已完成气象审计。当前独立分支为 `research/load-evidence-minimum-sprint`。远程 main 核对为 `fca1878d009a202f35852fa75853cbc6de7fe463`。

| 检查 | 结果 | 可复查方法 |
| --- | --- | --- |
| Week7Remake Python 回归 | **PASS 143/143** | `python -B -m pytest -q -p no:cacheprovider`，Week7Remake 根目录。 |
| Initial Draft Python 回归 | **PASS 53/53** | 同一命令，从 Initial Draft 独立执行。 |
| Public / full frozen Baseline | **PASS 142/142 与 166/166** | `python -B week7/audit/check_preservation.py`，完整归档另加 `--archive-root <原 LC1-main>`。 |
| 原始 Initial Draft | **PASS 158/158** | 对照迁移前 `228c005aa47bdee720524d152e56c10c5d4a7cd3` 的路径、mode、Git blob 及检出文件原始字节。另有迁移时已加入的 `REPRODUCTION.md`。 |
| Original Package | **PASS 367/367** | 逐项对照私有归档 `PACKAGE_CONTENT_SHA256.csv`。 |
| Stage 7 Outputs | **PASS 16/16（Git）与 16/16（archive）** | 按各自 `week7/stage7/outputs/stage7_output_SHA256.csv` 对已有文件重新计算，保留历史运行。 |
| Historical Stage 8 | **PASS 324/324** | 按档案连同 fixture 的七份 `SHA256SUMS.csv` 检查。DG 68、Temporal 29、BESS 62、PV/Wind 78、PV observability 34、DG+BESS fixture 7、D1 gate 46。 |
| EV deterministic traces | **PASS 3/3** | `python -B -m week7.prepare_regression_fixtures` 核对现有三份 EV traces SHA-256。 |
| 冻结小时数据和单位 | **PASS** | 三份基准各 8,760 个 ordered 2025 fixed LST 小时，时标连续、无重复、无缺值或非有限功率。每小时 14 个分项归并对应 tier，加入 EV AC 后与总 kW 的最大差为 0。EV trace 与总负荷最多相差 4.78×10⁻⁷ kW（输出小数位），DC 充电与牵引能及 SOC 范围相符。All-cases 的 heating 与 summer cooling 互斥。 |
| 新小时曲线 | **N/A** | 本轮仅使用冻结数据和明确标注的日均算术对照。 |
| 新 MDT / HOMER 执行 | **NOT RUN** | 已存原生文件和基准核查，D1 当前 gate NO-GO。 |

三份基准用电 SHA-256 可由各自 `week7/outputs/{low,central,high}_load_8760.csv` 复查。按 Low、Central、High 顺序为 `3fe4d13077e621f674af997ea9392626a97c4daba7b997e3f3d0f0b633481e89`、`5bd278b48e9ec0607273255fe7763c7364d896c6a31ce68eb9806d90c3084660`、`e61c49bf8ac1037a090ec2b4f32fd1c9c64b1d1ca1cc01e3168f2d050f9d063f`。Stage 4 的连续窗口及 mission feedback 结果为确定性 ENS，现无概率权重、失效率或恢复分布可支撑 EENS。

## EN3400 待决定事项

1. **确认设计对象和服务口径。** 请 supervisor 批准 120 人 hypothetical envelope、Critical 服务范围和 25+6 kW ICT 假设的论文用途。优先寻找可许可的分项电表或可公开比较的设施数据，独立确认用电、供热燃料、占用与 duty。优先检验占全年用电比重最高的 Critical 假设。
2. **确定 islanded service 的主张及验证方式。** 若论证拟超出条件性 energy service，请确认 grid-forming 来源与 UPS 转移证据计划，明确需由设备或专业电气验证的边界。若只做 T17 数值交叉验证，维持 D1 NO-GO，待原生控制映射证据后再决定新的匹配试验。
3. **批准 EV 实证与经济验证范围。** 只有获得可许可的 OEM/EVSE 和任务数据后才重新评估车队假设。Python 可复核 AC/DC ledger 与任务反馈。HOMER 独立经济对照需先约定相同服务、资源和费用边界。研究仍限定七辆车单向充电。
