# DG+BESS Validation Gate Decision

2026-11-21 · MDT 1.4.2513.0 · Existing frozen D1 fixture

**严格 D1 · NO-GO / NOT RUN。** 本轮读取已保存的安装版 PRM bridge、组件回读和冻结 Python 对照。严格参数匹配失败。未启动原生求解。 [现存 Gate 状态](../../week8/t17_dg_bess_native_v1/D1_GATE_STATUS.json) · [本轮参数矩阵](DG_BESS_PARAMETER_EQUIVALENCE.csv)

## 证据和精确阻塞

1. Python 锁定机组额定 100 kW、最低输出 **25 kW**。保存的安装版 `PRM::DieselGenerator::DEFAULT_MIN_UTILIZATION=0.40`，由 `PRMEvaluator.MakeNativeDieselGenerator` 传入，作用为 **40 kW**。此前字段检查未找到按机组覆盖。预期 100 kW 时两者均不触发下限，不能由此推定数值偏差。冻结技术条件仍不等价。
2. Python 分别表达 **10%** 物理 floor、**30%** operating reserve 和 **90%** 上限。检查过的 `BatterySpec.MinStateOfCharge` 只能表达一个下限。B3 的 **30%** 是有效 cutoff surrogate，不能同时证明独立 10% 下限。D1 `Standard` 控制器下的 70% 实际 opening SOC 也未取得。B3 的 `DesiredStateOfCharge=0.70` 和左端值仅支持其组件工况。
3. `Standard` 可作为候选，`MinRunningFossilGenerators=1` 仅指定运行台数。无已证的 100 kW 固定 setpoint、先 DG 后 BESS、零 DG-to-BESS、三段逐 tier pickup/shedding，以及实际 90 kW 截止时序。已有组件 MBF 的一个 Load Section 内含多个 tier，不能据此推定三组独立控制成功。
4. Native `OnSimulationAdvanced` 提供时间和 configuration，未提供具名事件原因、源功率、SOC 或油量状态。DG24 原生可见 **10+14 h**，其 10 h fuel-depletion 一致性已被单独核对；B3 reserve cutoff **3.5776 h**，固定 1 h 输出失败。不能把两段当作完整内部积分网格。B1/B2 的终点 SOC 和旧 DG 末油量仅可作守恒推导。D1 原始集成 MOF、event timeline 和 direct endpoints 均为 **NOT RUN**。

D1 本身是 **2 h**、零启动延时、125 L、恒定 **0.25 L/kWh** 正出力系数的独立验证夹具。100 kW Critical、90 kW 优先辅助、10 kW 较低优先辅助。它与调度研究的 1 h cold-start 和 load-dependent `MDT_DERIVED` 生产插值有不同目的。文档依据及本地 archive 文件包括 `NATIVE_BRIDGE_EVIDENCE.json`、`NATIVE_API_EVIDENCE.json`、`NATIVE_COMPONENT_READBACK_DG24.json`、`NATIVE_COMPONENT_READBACK_B3.json`。对应资料受原清单保护。 [冻结事件参考](../../week8/t17_dg_bess_fixture_v1/DG_BESS_PYTHON_EVENT_REFERENCE.csv) · [Stage 8 范围](../../week8/README.md) · [Sandia MDT v1.4 Guide](https://www.sandia.gov/research/publications/details/microgrid-design-toolkit-mdt-user-guide-software-v1-4-2024-07-01/)

## 下一项最小试验

| 路径 | 当前决定 | 运行前条件 |
| --- | --- | --- |
| 冻结 D1 2 h | **NO-GO** | 需要供应商文档或真实受支持的参数入口提供 25% DG 下限和独立 floor/reserve。回读确认初态、优先级和所有必要输出后，才重开原 gate |
| 独立 `D1A_STANDARD_PRIORITY_1H_NATIVE_LIMITS` | **CONDITIONAL GO，仅候选设计。NOT RUN** | 由 supervisor 批准使用 native 40% 下限和单一 30% effective cutoff，另存全新参考及 MBF；使用三个独立 Load Sections。先证明 `Standard` 的可复现输入及逐段服务计量，可获得真实 MOF、日志和 native clock。满足前置条件后才做一次 1 h bench |

D1A 的最小用途是隔离实例化、DG-first 和 priority pickup。开 BESS 70%、300 kWh DC、最大 90 kW AC、初始燃油 125 L、无补给，独立锁定对应 Python 参考。预注册 1 h 的 AC generation **100 kWh**、discharge **90 kWh**、fuel **25 L**、Critical ENS **0 kWh**、priority Auxiliary ENS **0 kWh**、lower Auxiliary ENS **10 kWh** 以及零充电。计量时分别检查 AC gross generation、per-tier served/ENS 与燃油单位和库存闭合；集成 1 h 输出依旧分别判定 native clock。此 1 h 在锁定 D1 的 1.192533333 h 储备事件之前，不能用它验证 reserve cutoff。D1A 的可运行性取决于直接证据，而非事后改公差。

**原 D1 保持的参考与判分。** 总 AC DG **200 kWh**、BESS 放电 **107.328 kWh AC**、**120 kWh DC**移除、燃油 **50 L**、Critical ENS **0**、Total ENS **92.672 kWh**、reserve event **2236/1875 h**。若能重启 D1，数值容差 `max(1e-8,1e-9×|reference|)`，事件绝对时间差 ≤ **1e-8 h**，检查 no-post-cutoff discharge 与不超过 PCS 90 kW。配置、Aggregate、Control Semantics、Event Timing、Fixed 1 h Native Clock 和 Direct Telemetry 各自记录。直接终态缺资料应给 **INCONCLUSIVE**，派生小时量单独标注。保留独立项目、原始 MOF、字节校验、带版本的复现命令，不改旧文件。 [已冻结数学事件](../../week8/t17_dg_bess_fixture_v1/DG_BESS_PYTHON_EVENT_REFERENCE.csv)

## Supervisor 决策

1. 确认论文主张限定于有功能量和条件性 Critical service。若需声明 continuity，先确认候选实体 AC reference 及额定，取得设备和合格工程验证的 ATS/UPS/DG transfer、black start、接地及保护证据。
2. 选择保留 D1 NO-GO，或批准独立有限 D1A 并确认原生可观察信号和判分项。
3. 允许论文图表引用组件证据范围；剔除任何将抽象 UPS、原生目录或 100% EA 写成实体认证的表述。经济与 24/72/168 h 结果保留既有 scope。
