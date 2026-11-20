# LC1 混合微电网研究

[English README](README.md)

本项目以 Sennybridge 周边代表性微电网为案例，研究停电期间的供电韧性和正常并网运行的经济性。设备模型与输入曲线集中管理，孤岛和并网调度分别执行。

| 目录 | 用途 |
| --- | --- |
| [models/core](models/core/) | 共享设备模型与能量核算 |
| [models/islanded](models/islanded/) | 柴油与电池调度、燃油曲线、停电及故障场景 |
| [models/grid_connected](models/grid_connected/) | 年度并网运行与经济计算 |
| [data](data/) | 负荷、风光及气象输入 |
| [validation](validation/) | 研究报告、结果表、归档复放及历史工程证据 |
| [Image](Image/) | 按研究用途归类的图表 |

## 研究进度 · 2026 年 11 月 15 日

### 已完成

| 验证项 | 结果 |
| --- | --- |
| 主电网断开与孤岛供电 | MDT 原生算例以上游电网失电触发孤岛运行。OpenDSS 稳态对照核查了 PCC 断开、孤岛供电和显式重合闸。 |
| 柴油机基准对照 | 恒定负荷下，24、72、168 小时的 MDT 与 Python 事件能量和燃油核算一致。 |
| 关键负荷优先与馈线恢复 | 40 kW 柴油机试验中，需求从 78 kW 降至 39 kW 后，EV 和可中断辅助在低负荷窗口恢复供电。另一组混合压力试验中，独立馈线断路器将 C4ISR 缺供从 11.765 kWh 降至零。总缺供由 30.588 kWh 增至 38.551 kWh，剩余缺供集中在 EV。 |
| C2 混合系统与储能功率上限 | PV75/Wind75/BESS300/PCS120 在测试的 24、72、168 小时原生停电窗口中，各级负荷缺供均为零。独立过载试验确认模型的电池最大有功放电功率为 120 kW。 |
| 原生求解时序与 SOC 分布 | 五组重跑记录了 309 个原生求解区间和按时段分组的 SOC 直方图。C2 的 24 小时对照中，MDT 在高于 80% 的 SOC 档位累计约 23.42 小时，同一窗口的 Python 对照为零。直方图在求解后保存，重新打开 MOF 时该字段为空。 |
| Python 调度与经济模型 | 已复算关键调度、备用策略与财务输出，结论适用于研究采用的输入假设。 |

### 待验证

- **混合系统逐时对照。** 还缺同一次原生运行的逐步 SOC、各设备功率及断路器触点记录。
- **Sennybridge 现场验收。** 还缺实测负荷、正式单线图和馈线清单，以及 PCS 并联与成网、UPS 后备时间、保护配合和 PCC 切换试验。10 kW 必要辅助分界是研究模型设定。
- **最终选型与实际回本。** 还需可核验的报价、电价与出口合同、出口许可和现场设备证据。

最新原生运行及其私有规格库保存在本地研究归档。[原生验证证据](validation/native-mdt/)提供公开结果表、输入与输出哈希和复核命令。[EN3400 英文结果与讨论](docs/en3400-results-and-discussion.md)介绍这些结果如何支持论文结论。

在项目根目录使用 Python 3.12 运行测试。

```powershell
python -m pip install -r requirements-test.txt
python -m pytest -q
```

[中文管理说明](docs/workspace-guide-zh.md) · [场景与历史编号索引](docs/scenario-index.md) ·
[历史工程证据中文索引](validation/historical-engineering-evidence/README.zh-CN.md)

研究涵盖模拟能量核算、负荷供电和条件性经济分析。原生 MDT 验证、设备性能和并网外送的适用范围见相应研究报告。
