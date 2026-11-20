# LC1 Load Evidence Audit

2026-11-20 · EN3400 · Hypothetical Sennybridge-area support camp

**结论。Central 的 2,092.88 kWh/day 可以作为学术情景，但其数值仍缺少场址验证。** 美国陆军 300 人温带营地的 **4,091 kWh/day** 已从原技术报告表格核实。该报告使用模拟电力需求，且冬季部分改用燃油供暖。其人均 **13.64 kWh/person/day** 可作为用电量级参考。现有 LC1 的 25 kW 连续 command/communications、6 kW 专用 cooling 及七辆 EV 的任务参数仍为研究假设。 [参数证据](PARAMETER_EVIDENCE.csv) · [数值对照](SCENARIO_COMPARISON.csv)

## 营地总需求比较

| 数据 | 人数 | 总用电 kWh/day | kWh/person/day | 剔除计划 EV 后 kWh/day |
| --- | ---: | ---: | ---: | ---: |
| LC1 Low | 120 | 1,869.96 | 15.58 | 1,773.61 |
| LC1 Central | 120 | 2,092.88 | 17.44 | 1,972.44 |
| LC1 High | 120 | 2,388.10 | 19.90 | 2,237.56 |
| US Army FY12 ORTB · Temperate Ready State | 300 | 4,091 | 13.64 | EV 未列为电气端用 |
| Fort Devens 现场测量 · 48 小时 | 90 名参训者 | 2,438 | 未归一化 | EV 未报告 |

- **Gildea 等，U.S. Army Natick NSRDEC，2017 年 4 月，NATICK/TR-17/011。** 原报告 *SLB-STO-D: 50, 300, 1000-Person Base Camp, Analysis of FY12 Operationally Relevant Technical Baseline*，印刷页 14 表 4 为集总值，页 17 表 7 按设施功能，页 18 表 8 按设备端用。300 人 Ready State 的 DCAM 电力需求为温带 **4,091**、荒漠 **5,108**、热带 **4,806 kWh/day**。两套分项表描述同一份电能，不能相加。包括住宿、餐饮、C2、照明、冷藏、卫生、洗衣、供水和 shelter HVAC。温带部分直接燃油供暖。车辆燃油另计，表中无 EV 充电端用。发电机容量和用于发电的燃油见单独表项。比对了原报告公开表格文本与两位作者的 Army presentation（slide 11）。报告 PDF 本地下载返回 HTTP 403，归档保存公开演示 PDF，报告 PDF 本身未归档。 [Army 原报告公开镜像](https://www.academia.edu/108894857/Sustainability_Logistics_Basing_Science_and_Technology_Objective_Demonstration_50_300_1000_Person_Base_Camp_Analysis_of_FY12_Operationally_Relevant_Technical_Baseline) · [Quigley 与 Langley，2018 年 1 月 31 日](https://eco-cdn.iqpc.com/eco/files/event_content/y1lhjZiMOBSalABYIuMGLDHFdm9cFKierhYxW8h3.pdf)
- **Gillman 等，Defense AT&L，2014 年 9–10 月，页 45 图 1。** 150 人额定规模的 Force Provider 训练设施在 2013 年 11 月冷季周末有 90 名参训者，受测 48 h 电量 **4,876 kWh**。包括住宿、ECU、电热、洗浴/卫生设施和辅助用电。报告提到洗衣和厨房设施，未给出可独立比对的全部 end-use 计量。全营 C4ISR 和 EV 覆盖未知。交流用电测量与基于波形的分项估计应分开解读。电热主导，人数随时段变化，适合说明冷季量级与热负荷敏感性，无法推导全年电量。 [原刊 PDF](https://www.waru.edu/sites/default/files/Migrate/DATLFiles/Sep-Oct2014/Gilman.pdf) · [作者团队 PDF](https://emsg.mit.edu/wp-content/uploads/2016/08/GillmanNEW.pdf)
- **UK MOD DIO，2017 年，FOI2017/00248 页 1。** 英国 barracks 的建筑类别用电基准按面积和用途建立，回复没有给出统一人均限额。NATO ENSEC COE、MILENG COE、NRCan 和 UK MOD 联编的 *Energy Management Handbook for Military Deployed Force Infrastructure*（2022，§1.2.1–1.2.2）给出分项计量与 EnPI 方法。本轮在这些 UK/NATO 原件中未取得可直接移植的温带 120 人整营电力或 C4ISR 功率。 [UK MOD 原始回复](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/615051/20170125-FOI00248.pdf) · [NATO ENSEC COE 手册](https://www.enseccoe.org/publications/energy-management-handbook/)

用全线性缩放比较，`4,091 × 120/300 = 1,636.4 kWh/day`，比 Central 剔除 EV 的 1,972.44 kWh/day 低 336.04 kWh/day。另一个可复核的算术情景把 ORTB 表 7 的 **510 kWh/day C2 功能** 作为固定组，其余用电按人数缩放，得到 **1,942.4 kWh/day**。先从原总量扣除同一 C2 再缩放残余，因此 C2 只计一次。它包含部分 ICT 相关 HVAC，不能再叠加表 8 的 communications、冷却或 LC1 的 C4ISR。若在该算术情景另加 LC1 Central 已排程 EV **120.43 kWh/day**，结果为 **2,062.83 kWh/day**。Central 比该值高约 **1.46%**。这表明结论对固定负荷和供热边界敏感，接近程度不能验证模型。算术对照没有生成小时曲线。

## 14 类基础设施和四项 Critical 负荷

[参数证据表](PARAMETER_EVIDENCE.csv) 按 `equipment.csv` 和当前 `scheduled_hours` 记录每项额定功率、固定 LST 时段、实际计入小时数、日均和全年 kWh、潜在回路重叠、驱动尺度及证据缺口。Critical 启用时用 100% 假定负荷，Auxiliary 的 Low/Central/High 乘数为 65%/80%/100%。已对三份逐时序列复算。数值能源归类为 `PYTHON_DERIVED_RESULT`，额定值和排程归类为 `EXPLICIT_RESEARCH_ASSUMPTION`。文献包含外部现场实测代理或外部模拟代理，**没有 Sennybridge 营地电表值**。 [冻结配置](../../week7/config/equipment.csv) · [排程代码](../../week7/load_model.py) · [Assumption Matrix](../../week7/audit/assumption_matrix.csv)

| Critical 分类 | 假定 kW | 排程 fixed LST | kWh/day | kWh/year |
| --- | ---: | --- | ---: | ---: |
| Command/communications | 25 | 连续 | 600 | 219,000 |
| Dedicated C4ISR cooling | 6 | 连续 | 144 | 52,560 |
| Medical/emergency refrigeration | 4 | 连续 | 96 | 35,040 |
| Perimeter lighting | 6 | 18:00–06:00 | 72 | 26,280 |
| 总计 | 35–41 按时段 | 全年 | 912 | 332,880 |

Critical 占 Central 全年 **43.58%**，是 camp demand 比较中最突出的结构差异。ORTB 表 8 的 communications/computers 为 **344 kWh/day**（平均约 14.33 kW），表 7 的 C2 功能为 **510 kWh/day**（平均 21.25 kW），均属于有特定场景边界的模拟。LC1 的 25+6 kW 对应 744 kWh/day，C2 功能和 LC1 ICT 设备口径仅部分重合。未找到匹配任务负荷、时序和 cooling 分表的公开数据，25 kW 连续与 6 kW 连续仍为敏感性假设。故本轮没有创建 C4ISR 小时灵敏度场景。后续若有可用负荷形状，应先测试全年 kWh 固定的形状变化，再将年电量变化作为另一独立变量。 [ORTB 表 7–8](https://www.academia.edu/108894857/Sustainability_Logistics_Basing_Science_and_Technology_Objective_Demonstration_50_300_1000_Person_Base_Camp_Analysis_of_FY12_Operationally_Relevant_Technical_Baseline)

现有 Heating/HVAC 有住宿纯风机、季节电热、夏季非关键制冷和 C4ISR 专用冷却四个独立口径。电热与夏季制冷启用时段无重叠。水处理目前归 Auxiliary，生活热水没有独立建模行，属于待界定端用。计算证明现有账本边界内未重复汇总。实际混合回路与边界仍需通过可许可的设备清单或分项计量验证。2025 T2M 已有数据，当前电热使用日程和固定 duty。建筑面积、热损失、设定点和热源或 COP 缺乏独立依据，温度驱动热模型保留为 `EVIDENCE_GAP`。 [供暖排程](../../week7/load_model.py) · [气象审计](../../docs/WEATHER_DATA_AUDIT.md)

## 七辆 EV 证据与用电口径

| Archetype | 数量 | 额定电池 kWh DC | kWh DC/km | 每车 AC kW | 典型任务与保护 reserve SOC |
| --- | ---: | ---: | ---: | ---: | --- |
| Light Utility | 4 | 75 | 0.25 | 11 | 50–65 km 工作日，20% |
| Medium Logistics | 2 | 160 | 0.65 | 22 | 90–95 km，每车每周四个计划日，25% |
| Mobile Emergency Support | 1 | 100 | 0.35 | 11 | 周日 20 km 演练，45% |

FUSO *The Next Generation eCanter* pp. 4–5 确认其商业 S pack 41.3 kWh 对应 up to 11 kW AC，M/L 82.6/123.9 kWh 对应 up to 22 kW AC。该资料支持 **11/22 kW AC 技术上存在**，具体车型、EVSE、相数和可用容量仍需匹配。Ragatz、Duran 和 Walkowicz（NREL，2014，NREL/BR-5400-61190 pp. 1、4）报告商业 eStar 80 kWh，63 辆样本、2,665 个驾驶车辆日。其 **747.2 Wh/mi in-motion DC** 约为 **0.464 kWh DC/km**。汇总 **888.9 Wh/mi AC charged** 和 DC charge 的采样覆盖不同，不能校准 LC1 的 92% AC-to-DC 效率。该商业样本约 36.85 km/day driven，不能作为本车队任务排程或任务储备。原全文指标已在线核对。NREL 原 PDF 本地下载失败，已保存 NLR 官方目录 HTML，未把目录快照当作全文存档。所有 LC1 电池、任务、最低 SOC、初始/目标 SOC 90%、92% 和站端 70 kW cap 均保留为明示假设。 [FUSO 原厂资料](https://www.fuso-trucks.com/wp-content/uploads/sites/2/2022/08/221013_THE-NEW-eCANTER_Broschure_EN_RZ.pdf) · [NREL 原报告](https://docs.nrel.gov/docs/fy15osti/61190.pdf) · [NLR 出版目录](https://research-hub.nlr.gov/en/publications/navistar-estar-vehicle-performance-evaluation-4th-quarter-2013/)

| Normal-year | Low | Central | High |
| --- | ---: | ---: | ---: |
| 营地计入 AC EV charging，kWh/year | 35,166.96 | 43,958.70 | 54,948.37 |
| 电池端 DC charging / traction，kWh/year | 32,353.60 | 40,442.00 | 50,552.50 |
| 模型已执行计划出车次数 | 1,513 | 1,513 | 1,513 |

现行 `EVFleetFeedback` 已在供电不足时把实际 served AC 计入车辆 SOC，先检查每次出车能否完成行程并留有 reserve，短供不计入 SOC。Stage 4 支持计划静态和动态 mission-feedback 两类比较。已保存的 Central 168 h BASE W01 有 **614.04 kWh AC charging ENS**，29 次机会中 **0** 次 missed。BASE W09 有 **3,029.00 kWh** charging ENS，29 次机会中 **1** 次 missed。ENS 是未交付的充电电量，missed mission 是调度和车辆状态的结果。两组指标均为确定性条件性输出，不能估计任务失败概率。此次测试未发现需要新建回归用例的可复现问题，故仅保留证据审计。 [EV feedback 实现](../../week7/nextstage/fleet_feedback.py) · [Stage 4 冻结结果](../../week7/stage4/outputs/stage4_13start_EV_mission_feedback.csv)

## 证据与私有存档

源文件、SHA-256、获取日、页码用途和 BibTeX 保存在私有研究档案 `Reference/Research documents/LC1_load_evidence_sprint_20261120/`。Git 只纳入可公开核对的证据映射、数值摘要与门槛判定。
