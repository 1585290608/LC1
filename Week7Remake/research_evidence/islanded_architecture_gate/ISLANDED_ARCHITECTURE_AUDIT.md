# LC1 Islanded Electrical Architecture Audit

2026-11-21 · EN3400 · Hypothetical 120-person camp

**审计结论。Week7Remake 足以说明 24/72/168 h 的有功能量调度，C4ISR 的物理连续供电仍为 `POWER_CONTINUITY_UNVERIFIED`。** 代码没有指定孤岛时建立 AC voltage/frequency reference 的设备。DG 有功上线、PCS 90 kW 数值限制和理想 UPS 账本均已找到；三者之间的实体启动和切换关系缺证。 [功能架构 SVG](figures/architecture_overview.svg) · [时间线](POWER_CONTINUITY_TIMELINE.csv)

## 模型边界和运行证据

| 元素 | Week7Remake 冬季电量模型 | 实体或其他原生拓扑证据 |
| --- | --- | --- |
| Utility / PCC | Grid-connected Stage 6 有进口、出口和功率上限。S3-v2 停电窗口由 `islanded=True` 输入，窗口内 grid import/export 为 0 | 孤岛场景通过模型标记进入。PCC 是概念边界。无事件探测、触点状态或重合闸模型 |
| PV / Wind | 50 kW / 50 kW，按 2025 固定 LST 的 v6 p.u. 乘装机，向公共有功平衡分配。PV p.u. 已含其转换边界，Wind 为可用净功率 | PV inverter 与 Wind 接口是有功输入的物理假设。无控制模式、低电压支撑、启动或并联测试 |
| DG | 100 kW 额定，25% 最小出力，2,000 L 初始库存，`MDT_DERIVED` 燃油插值。在低功率 surplus 下可走被允许的 BESS 充电或理想 25 kW dump sink 假设 | 代码有 OFF/STARTING/READY/RUNNING 和燃料耗尽的能量区段。无实际 governor、AVR、励磁、电压建立或同步过程 |
| BESS / PCS | 300 kWh DC，90 kW AC，方向效率各 0.8944。初始 SOC 70%，储备 30%，物理下限 10%，上限 90%。S3-v2 的 committed backup 路径可按规则使用 30% 以下库存至 10% | 数学上可在 DG 未发电时放电。没有确认 PCS 会自立建压、支撑无源母线、承担负荷启动或进行 seamless transfer |
| UPS / Critical tier | 理想 UPS 30 kW、初始 7.5 kWh，补剩余 Critical gap。Critical 含 C4ISR、专用冷却、医疗冷藏和 perimeter security lighting，Central 需求 35–41 kW | 未知哪些实体回路接 UPS。理想路径没有 kVA、负荷峰值、旁路、电池降额、切换中断或独立验收 |
| Auxiliary / EV | W7 三 tier 按 Critical → Auxiliary → EV 分配可用功率。EV 为单向用电，动态反馈由实际分配 AC 电量更新 | 代码分配顺序不提供逐支路实体接线、保护或开关动作。动态 EV 结果适用于其当前假定车辆和 mission guard |

[核心组件](../../models/core/components.py) · [核心参数](../../models/core/simulate.py) · [S3-v2](../../week7/nextstage/dispatcher.py) · [Stage 4 调用](../../week7/stage4/contingency.py) · [Stage 6](../../week7/stage6/annual_grid.py) · [场址假设](../../week7/site_design_basis.md)

**私有研究档案层。** 归档 `LC1_MDT/case_study_v6` 的只读拓扑核查显示，固定 1 DG 基线为一个 Bus、六条 Line、零 Switch、零 Transformer，利用 `PowerUtility/DBT` 表征停电。另有 P3 UPS/馈线小试，以及 `integrated_connection_v1` 的六份独立连接 MBF，已保存原生 Bus、抽象开关与 inverter 接口，PCC 默认 open。P3 的关联 UPS 试验使用 40 kW / 300 kWh 理想目录装置和独立启动条件，不能套用到 Week7Remake 的 30 kW / 7.5 kWh。连接分支也注明实际 Utility 注入、设备额定、同步保护和现场连续供电未验证。可追溯原档案报告为 `OUTAGE_BOUNDARY_AND_TOPOLOGY.md`、`P3_CONTROL_AND_UPS_REPORT.md`、`CONNECTED_MODEL_DELIVERY.md`。此处仅用它们确认拓扑与功能证据范围，没有开展新的原生容量或服务比较。

## Grid-forming 与 islanding 核对

| 问题 | 分类 | 具体发现 |
| --- | --- | --- |
| Grid-following / Grid-forming 模式 | NOT_MODELLED | Python 没有转换器模式变量。原生目录抽象 Inverter 不证明 GFM |
| Inverter voltage/frequency reference | DOCUMENTED_ASSUMPTION；NOT_VERIFIED | `Settings.ac_reference_assumed=True`。没有指派设备 |
| Island detection / grid disconnection | PARTIALLY_VERIFIED 数值边界 | Python 明确视为孤岛，原生 v6 有 DBT；PCC 物理检测及隔离未验证 |
| Automatic Transfer Switch | NOT_MODELLED | 启动区段与 UPS 剩余能量逻辑没有 ATS 动作状态或真实切换时间 |
| Black start | NOT_VERIFIED | 无已验证的无源母线建压证据 |
| BESS 在 DG 未发电时工作 | IMPLEMENTED_AND_TESTED 有功；NOT_VERIFIED 实体 | SOC/PCS 唯一约束，模型能给负荷注入功率 |
| Renewables 在 grid unavailable 时 | DOCUMENTED_ASSUMPTION | 通过 `ac_reference_assumed` 打开可用有功，物理并网控制未知 |
| Voltage / frequency control | NOT_MODELLED | 无电压、频率、相位、kVA 功率流或瞬态 |
| DG synchronisation / reconnection | NOT_MODELLED | DG 状态量控制正有功与燃油。无同步判据。另有档案 PCC 外部逻辑参考，未证明物理重连 |
| Protection / earthing | NOT_VERIFIED | 归档无经证的保护配合、接地方案、设备分断能力或故障测试 |

`ac_reference_assumed` 直接门控 `usable` renewable kW。受影响的计算包括 renewable-to-load、按 tier 分配后的剩余缺口、BESS 放电与启停决策、DG commitment、可再生充电和 curtailment，以及最终各 tier ENS。BESS 自己的有功支路没有等价的母线建压判据，即使关闭可再生假定也可能在数值上供电。对应逻辑位于 `core/simulate.py`、`islanded/commitment.py`、`islanded/service_dispatch.py` 与 `week7/nextstage/dispatcher.py`，Stage 4 和 HDH 使用后者。 [Stage 4 调用](../../week7/stage4/contingency.py) · [HDH 验证](../hdh_heating_sensitivity/VALIDATION_REPORT.md)

## UPS 与 DG 的时段解释

**零时刻。** 场景直接给出停电。DG 从 cold/off 有状态地进入启动，但仅在 dispatch 请求时开始计时。代码的 **1 h** 是从该请求起的假设延时。若 t=0 开始，并且 UPS 从 t=0 满载 **30 kW**，7.5 kWh 理想库存可维持 **15 min**。全 Critical tier 的 **35–41 kW** 已大于 UPS 单独峰值。该 15 分钟属于有功额定计算，低负荷或延迟承担时持续时间不同。

| 时段 | 模型中的能源支撑 | 现实需确认 |
| --- | --- | --- |
| 0–15 min | 满电 UPS 可补 ≤30 kW 的缺口，BESS 可按 SOC/PCS 放电，PV/Wind 在假定母线下可用 | UPS 能否承担实际关键回路、PCS 或其他设备能否建立 AC 参考、切换时间 |
| 15–60 min | 若 UPS 起始满载则能量用尽。若初始仅补较小缺口，可能还有存量；BESS/可再生可能继续提供有功 | 没有已验证的另一条实体电源路径覆盖该时段。记录 **POWER_CONTINUITY_UNVERIFIED** |
| DG 可用之后 | 经过一次 cold-start 延时且有请求、有燃料才输出。可接管有功，按策略补负荷或在准许时充 BESS | 机组是否具备接管电压频率的模式、开关转移、同步与源间交接均待证 |

**存档冬季实证核查（模型内）。** 起点小时索引 0 的 Wind 实际 **43.74582 kW**、BESS 放电 **45.25418 kW**、DG 和 UPS **0 kW**、Critical 需求与服务 **41 kW**；第一次正 DG generation 在索引 **3**。该例说明不能把计时假设读成固定 45 分钟失供。一个小时或内部能量区段的 Critical ENS 是未供电量积分，零值说明模型在该时间分辨率内给足了有功。电压跌落、相位跳变、开关死区和 UPS transfer interruptions 在状态空间之外，零 ENS 不能证明真实的不间断服务。 [保存的冬季逐时账本](../../week7/nextstage/outputs/winter_168h_original_equipment_plant_trace.csv)

## 现有结果可用于何种主张

| 窗口 | Critical ENS 原 / HDH kWh | Total ENS 原 / HDH kWh | Critical EA 原 / HDH % |
| ---: | ---: | ---: | ---: |
| 24 h | 0 / 0 | 3.10 / 7.01 | 100 / 100 |
| 72 h | 0 / 0 | 1,073.70 / 1,225.12 | 100 / 100 |
| 168 h | 259.58 / 277.52 | 6,555.40 / 7,098.94 | 95.93 / 95.65 |

上述结果支持“在假定 AC reference 下的有功能量充足性、供暖时序相对敏感性、有限燃油调度”这些限定结论。HDH 年电量 **763,901.10 kWh**、供暖 **72,768 kWh**、峰值 **195.09→201.09 kW** 均与存档吻合。168 h 两侧均用尽模型的 2,000 L；确定性嵌套窗口无概率权重。没有重跑窗口。 [既有 HDH 结果](../hdh_heating_sensitivity/RESILIENCE_COMPARISON.csv) · [HDH 年度账本](../hdh_heating_sensitivity/HDH_SCENARIO_SUMMARY.csv) · [Stage 7 证据边界](../../week7/stage7/docs/T17_Validation_Evidence_and_Gaps.md)
