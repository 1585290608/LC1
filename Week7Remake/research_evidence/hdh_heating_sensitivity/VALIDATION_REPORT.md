# LC1 HDH Validation Report

2026-11-20 · Python 3.12.10 · Matplotlib 3.11.2 · Synthetic timing sensitivity

## 既有冬季窗口的成对结果

均从 **2025-01-01 00:00 LST** 启动，分别运行 24、72、168 h，初始库存每次重置。这三个窗口嵌套，属于一次代表性冬季的确定性对照。只对 **15.5°C** 主情景运行停电。两侧使用同一原有 **50 kW PV / 50 kW Wind / 100 kW DG / 300 kWh BESS / 90 kW PCS**，初始 BESS SOC **70%**、燃油 **2,000 L**、`MDT_DERIVED` 燃油曲线，沿用 **S3-v2** 和原有 Critical 优先级。BESS 物理 SOC 下限 10%、上限 90%、操作储备 30%、DG 停机 SOC 60%，电池两方向效率均为 0.8944。S3-v2 中按已有规则处理储备，不把 30% 当作硬件地板。保留假设的 UPS 和 AC reference。 [原冬季窗口](../../week7/nextstage/outputs/mission_readiness_feedback_matrix.csv) · [对照完整结果](RESILIENCE_COMPARISON.csv)

下表每组数值为 **原 Central → HDH 15.5°C**。

| 停电 | 空间供暖需求 kWhₑ | Critical ENS kWhₑ | Total ENS kWhₑ | Critical EA % | Diesel L | 最小 / 末态 BESS SOC | 错过出车次数 |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| 24 h | 288.00 → 304.38 | 0 → 0 | 3.10 → 7.01 | 100 → 100 | 363.94 → 367.84 | 两侧均 10% / 10% | 0 → 0（5 次机会） |
| 72 h | 864.00 → 1,024.38 | 0 → 0 | 1,073.70 → 1,225.12 | 100 → 100 | 1,414.78 → 1,437.39 | 两侧均 10% / 10% | 0 → 0（17 次机会） |
| 168 h | 2,016.00 → 2,400.33 | 259.58 → 277.52 | 6,555.40 → 7,098.94 | 95.93 → 95.65 | 2,000.00 → 2,000.00 | 两侧均 10% / 10% | 1 → 1（29 次机会） |

24 h 和 72 h 的 Critical 服务保持，燃油分别增加 **3.90 L** 与 **22.61 L**。168 h 两侧均耗尽燃油，Critical ENS 增加 **17.94 kWhₑ**，Critical EA 下降 **0.28 percentage points**，Total ENS 增加 **543.54 kWhₑ**。所有运行均使用 `EV_DYNAMIC_MISSION_CONSTRAINED`，使命机会和同一规则不变。动态充电可在供电短缺后重新请求，累计请求电量可能因实际充电分配不同而改变。完整结果单列 EV Requested AC、EV Served AC 和 EV ENS，避免把 EV ENS 当成永久牵引损失。Critical 分母逐对完全相同。没有把固定年度 EV 排程混入停电 ENS 分母。

`screen.simulate` 无外部负荷参数。试验适配器以 Python 函数的私有命名空间给其原有实现绑定 A/B 辅助负荷，保持原文件、模块全局 `LOADS` 及 dispatcher 独立。三组 A 情景在 **1e-7** 容差内同时复现未适配入口和存档的冬季动态 EV 结果。B 情景逐时核实输入来自 HDH 版本。对照最大 AC 误差 **1.43×10⁻¹⁴ kWhₑ**、BESS DC **2.14×10⁻¹⁴ kWh**、燃油 **1.14×10⁻¹³ L**。Critical/aux/EV 各自 `demand = served + unserved`。BESS、燃油与 UPS 库存逐时连续，无负燃油及同时充放电事件。

## 验收与 Preservation

| 检查 | 结果 |
| --- | --- |
| 原始负荷和 T2M 时间轴 | **PASS**。Low/Central/High 与原始 NASA / 处理 T2M 每组 8,760 小时，顺序、时区标记和数值一致，零缺失、重复或非有限值。 |
| HDH 输出 | **PASS**。主情景 CSV 二次独立读取并逐时对账，三个调整点无负负荷、超上限、禁止时段供暖、供暖和 summer cooling 同时运行。非供暖列逐点等同冻结 Central。 |
| 年度和月度电量 | **PASS**。三个温度点的供暖与年总电量均守恒。72 个月度情景行，按 15 个端用独立核算。主情景供暖与全站年误差均约 **1×10⁻¹² kWhₑ**。 |
| 特殊边界 | **PASS**。非零权重的最大可分配量恰好匹配时保留时段和上限，超过容量的用例明确抛出 `INFEASIBLE`。 |
| Islanded solver 执行 | **PASS**。**6** 个成对运行，另有 **3** 个独立未适配 baseline 复核。原始与存档的 **3/3** 窗口通过 parity，六个结果均完整。 |
| 图表 | **PASS**。6 张 PNG 经渲染目检及 300 dpi 检查，6 张 PDF 验证为可缩放矢量图。 |
| 独立目录复算 | **PASS 16/16**。四个结果 CSV 和十二个图表文件的 SHA-256 均与复算输出一致。 |
| Week7Remake / Initial Draft 回归 | **143/143、53/53 PASS**。已有 EV Regression Fixtures **3/3**。 |
| 文件哈希 | **PASS**。公开 Baseline **142/142**，完整 Baseline **166/166**，原始包 **367/367**，Stage 7 输出 **16/16**（Git 和档案各自核对），Stage 8 已存工件 **324/324**。 |
| Frozen Git paths | **PASS**。从 `2d58409` 分支点开始，本轮 Git 改动只新增 `research_evidence/hdh_heating_sensitivity/`。Initial Draft、原模型、配置和 Stage 0–8 历史文件均无改动。 |

使用 `PYTHONDONTWRITEBYTECODE=1` 及 `-B`。执行 `python -B -m pytest -q -p no:cacheprovider`，分别位于 `Week7Remake` 和 `Initial Draft`，完整 Baseline 验证使用 `week7/audit/check_preservation.py --archive-root` 指向原压缩包解出的 `LC1-main`。输入路径及 SHA-256 见 [SOURCE_MAP.csv](SOURCE_MAP.csv)。

## 可用于 EN3400 的结论及剩余证据

可以报告在相同年能量、相同供暖时间边界与相同发电设备下，更集中于寒冷时段的供暖会提高该组模型的冬季峰值与局部 ENS。三个温度点只用于考察主结果对平衡点的敏感性。单组嵌套冬季停电不能识别概率权重或 reliability improvement。MDT、HOMER Pro 和电气瞬态验证均未执行。

正式称为 temperature-calibrated forecast 前，需要场址匹配的空间供暖 AC 分表、室外传感器来源、运行/占用时段及设备特性。若论文要论证结果超出所选冬季窗口，下一步应预先指定更多冬季起点并保留季节覆盖，不改变硬件和控制。若要主张实物供电连续性，需要独立 UPS transfer 和 grid-forming 证据。
