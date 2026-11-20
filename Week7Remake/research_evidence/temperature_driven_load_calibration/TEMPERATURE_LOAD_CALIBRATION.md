# LC1 Temperature-Driven Load Calibration

2026-11-20 · EN3400 · Hypothetical 120-person Sennybridge-area camp

**基准复算 PASS，温度校准 EVIDENCE_GAP。** LC1 Central 冬季比夏季平均每天多用 **246.20 kWhₑ（12.77%）**。现有差异主要来自日历型 HVAC 排程。威尔士住宅热泵有多个配对全年电表序列，但空间供暖、生活热水和机组辅机尚未可靠拆分，室外温度的测量来源也未逐系统证实。营地供暖技术、热损失和室内运行条件仍缺证据。依照数据门槛，`temperature_sensitivity` 已登记为 **NOT RUN**，尚无调整小时数据、年电量或峰值变化。 [情景状态](temperature_sensitivity.json)

## MODELLED_BASELINE · 2025 月度账本

每个负荷情景与现有 `data/temp.csv`、原始 NASA POWER `T2M` 的 **8,760/8,760** 小时一一匹配，从 2025-01-01 00:00 到 2025-12-31 23:00。全年零缺失、重复、移位、非有限值或 `-999` 哨兵，分拆温度与原始字段最大绝对差为 0°C。LC1 使用 **2025 固定 LST**，Sennybridge 原始点 **51.95°N、3.57°W** 落在 NASA POWER UTC+0 分带。没有英国夏令时跳时或回拨。T2M 为 MERRA-2 2 m 格点气温。 [气象审计](../../docs/WEATHER_DATA_AUDIT.md) · [NASA POWER 小时 API](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/)

单元格为 **kWhₑ/月 / kWhₑ/day**。月平均气温为该月全部小时 T2M 的算术平均。全精度月表另含 14 类基础设施、EV AC、供暖与非关键制冷月电量、温度范围和每月峰值。 [月度 CSV](monthly_baseline.csv) · [年度核对与输入 SHA-256](baseline_reconciliation.json)

| 月份 | T2M °C | Low | Central | High |
| --- | ---: | ---: | ---: | ---: |
| 2025-01 | 2.98 | 60,075.59 / 1,937.92 | 67,474.64 / 2,176.60 | 77,275.30 / 2,492.75 |
| 2025-02 | 3.93 | 54,098.19 / 1,932.08 | 60,741.34 / 2,169.33 | 69,542.67 / 2,483.67 |
| 2025-03 | 5.90 | 59,685.84 / 1,925.35 | 66,990.15 / 2,160.97 | 76,669.69 / 2,473.22 |
| 2025-04 | 9.04 | 58,014.36 / 1,933.81 | 65,144.25 / 2,171.47 | 74,590.31 / 2,486.34 |
| 2025-05 | 12.14 | 57,486.52 / 1,854.40 | 64,286.15 / 2,073.75 | 73,289.69 / 2,364.18 |
| 2025-06 | 14.81 | 52,050.24 / 1,735.01 | 57,802.95 / 1,926.77 | 65,413.69 / 2,180.46 |
| 2025-07 | 16.22 | 53,979.72 / 1,741.28 | 59,971.05 / 1,934.55 | 67,895.82 / 2,190.19 |
| 2025-08 | 15.67 | 53,640.84 / 1,730.35 | 59,550.15 / 1,920.97 | 67,369.69 / 2,173.22 |
| 2025-09 | 12.14 | 55,728.05 / 1,857.60 | 62,331.37 / 2,077.71 | 71,074.21 / 2,369.14 |
| 2025-10 | 10.00 | 60,075.59 / 1,937.92 | 67,474.64 / 2,176.60 | 77,275.30 / 2,492.75 |
| 2025-11 | 7.56 | 57,675.48 / 1,922.52 | 64,723.35 / 2,157.44 | 74,064.18 / 2,468.81 |
| 2025-12 | 5.70 | 60,024.72 / 1,936.28 | 67,411.05 / 2,174.55 | 77,195.82 / 2,490.19 |

| 2025 全年 | 总用电 kWhₑ | Space heating kWhₑ | 非关键制冷 kWhₑ | Peak kW |
| --- | ---: | ---: | ---: | ---: |
| Low | 682,535.156465 | 59,124 | 3,588 | 172.143478 |
| Central | 763,901.095464 | 72,768 | 4,416 | 195.091304 |
| High | 871,656.369552 | 90,960 | 5,520 | 225.000000 |

三个情景的月电量加总与直接逐时累计差均为 **0.000000 kWhₑ**。每小时的分项、tier 和总功率差均为 **0 kW**。三个年度峰值的最早出现时间都是 **2025-01-02 18:00 LST**。

| 2025 分组 | T2M 均值 | Low kWhₑ/day | Central kWhₑ/day | High kWhₑ/day |
| --- | ---: | ---: | ---: | ---: |
| DJF · 1、2、12 月（90 天） | 4.21°C | 1,935.54 | 2,173.63 | 2,489.04 |
| JJA · 6–8 月（92 天） | 15.58°C | 1,735.55 | 1,927.44 | 2,181.30 |
| DJF − JJA | −11.37°C | +199.99 | +246.20 | +307.75 |

Central 的排程供暖在 10–4 月每天 **288 kWhₑ**，5、9 月 **192 kWhₑ**，6–8 月 **0 kWhₑ**。非关键制冷只在 6–8 月运行，每天 **48 kWhₑ**。仅这两项就解释了冬夏差额中的 **240.00 kWhₑ/day**，其余约 **6.20** 主要由工作日排程和 EV 充电日历产生。1 月（2.98°C）和 10 月（10.00°C）有相同的基准日均总负荷，说明月度散点反映了日历联动，斜率不能作为温度系数。

### 每个端用的原始方程

设 `Iᵢ(t)` 为下表时段指示函数，`Pᵢ(t) = 额定 kW × uᵢ × Iᵢ(t)`。Critical 的 `uᵢ=1`，Auxiliary 的 `uᵢ=0.65 / 0.80 / 1.00`（Low / Central / High）。所有区间左闭右开，跨午夜拆成两段并在同月判定。每月 `Eᵢ = ΣPᵢ(t) × 1 h`，`dailyᵢ = Eᵢ / 该月天数`，`peak = maxₜΣPᵢ(t)`。Tier 小计供对账，整站总量只加各端用一次。 [原始设备表](../../week7/config/equipment.csv) · [冻结排程](../../week7/load_model.py)

| 类别 | 额定 kW | Tier | `Iᵢ(t)=1` 条件，固定 LST |
| --- | ---: | --- | --- |
| Command / communications | 25 | Critical | 每天全天 |
| Medical / emergency refrigeration | 4 | Critical | 每天全天 |
| Dedicated C4ISR cooling | 6 | Critical | 每天全天 |
| Perimeter security lighting | 6 | Critical | 每天 18–06 |
| Accommodation ventilation | 12 | Auxiliary | 每天全天 |
| Accommodation sockets | 18 | Auxiliary | 每天 00–02、06–09、17–24 |
| Accommodation lighting | 12 | Auxiliary | 每天 06–09、18–23 |
| Electric catering | 26 | Auxiliary | 每天 06–09、11–14、17–19 |
| Workshop / maintenance | 18 | Auxiliary | Mon–Fri 09–15 |
| Laundry | 12 | Auxiliary | 每天 13–17 |
| Water pumping / treatment | 8 | Auxiliary | 每天 07–10、18–21 |
| Common-area lighting | 8 | Auxiliary | 每天 07–12、16–21 |
| Space heating | 30 | Auxiliary | 10–4 月每天 17–05，5、9 月 18–02 |
| Non-critical summer cooling | 6 | Auxiliary | 6–8 月每天 10–20 |

EV 为独立 AC 端用。按最早下一次出车排序，当车辆已接入时，`E_AC,v = min(车载限制 × 1 h, 共享 AC 剩余, max(0,(0.90 − SOC) × C_DC / 0.92))`。共享上限为 70 kW。任务消耗为 `距离 × 情景行程乘数 × kWh_DC/km`，行程乘数为 0.80 / 1.00 / 1.25。出车前检查任务电量及 reserve，返程记入牵引消耗。整站仅累加 AC 充电。气温未进入冻结等式。 [EV 配置](../../week7/config/fleet.csv)

## MEASURED_EXTERNAL · 证据筛查

- **HeatpumpMonitor.org。** 在六个威尔士公开系统上读取明确的 2025 UTC 窗，核对原始时间戳和返回值。Swansea 31（Mitsubishi，11.2 kW 标称热输出）有 8,555 个温度与非负相邻计数器差值的配对小时。Newport 64、Pembrokeshire 283、Abermule 431、Monmouthshire 442（Vaillant ASHP，标称热输出分别 7、3.5、5、5 kW）各有 **8,760** 个配对小时，均有年末端点及零回退。Cardiff 752（Vaillant 10 kW）只有 3,658 个配对小时。电功率原采样为 5 或 10 秒，样本中的 outsideT 原采样为 10 秒或 1 小时。核对口径为 `interval=3600&average=0` 的整点返回值，电量为相邻累计电表差 **kWhₑ**。整点计数器连贯不证明 5/10 秒测量全程连续。瞬时 W 的整点缺失也不代表该小时全程缺测。各组明确标注 SDM120 电表及住宅与机型。数据许可 **CC BY 4.0**。 [平台技术说明与许可](https://heatpumpmonitor.org/about) · [API](https://heatpumpmonitor.org/api-helper) · [采样计数、精确 URL 与原始响应哈希](external_data_screen.csv)
- **电气边界。** Newport 64 的联合热泵电量在 DJF 为 **1,469.72 kWhₑ**（4.59°C，90 天），JJA 为 **98.09 kWhₑ**（16.31°C，92 天）。这是独立于住宅其他用电的热泵计量，支持该系统合并用电的强季节性。它含生活热水。64、283、442 无显式 DHW-mode feed，431 的模式在整点仅有 **64/8,760** 个有限值，无法从该导出可靠地把小时能量分配给空间供暖或 DHW。温度 feed 的名称和单位已核对，室外传感器类型或上游气象来源未逐系统证实。此组数据适合作为外部对照，当前不能用于拟合营地 `kW/°C`。 [Newport 系统 64](https://heatpumpmonitor.org/system/view?id=64) · [Abermule 系统 431](https://heatpumpmonitor.org/system/view?id=431) · [电表字段定义](https://github.com/openenergymonitor/HeatpumpMonitor/blob/master/HeatpumpMonitorTH/installation.md)
- **Cardiff University / Wales。** Ionas 2025，Ch. 3 Table 3-7，部分发展群组观测窗口为 2022-10 至 2024-04，包含可区分的热泵电、热量与室外温度。另一个群组的逐时记录只覆盖 2024-02 至 04，论文记录了部分通道缺测与插补。未取得可再利用的完整逐时配对数据和原始数据许可。ORCA PDF 在本地返回 HTTP 403，章节证据来自公开索引。 [Cardiff ORCA](https://orca.cardiff.ac.uk/id/eprint/190464/)
- **Energy Systems Catapult EoH。** UKDS SN 9050 第 2 版的 742 个住宅清洗文件约 2 min，记录电输入、输出热和温度，监测范围 2020-11 至 2023-09。另有 30 min 版本。DESNZ 附录载明 450 个达质量门槛、英格兰与苏格兰样本和 **OGL v3.0**。具备跨季校准方法的价值，但本轮未核到单户无缺口年或同等营地设备，且数据期不含 2025。 [UK Data Service DOI](https://doi.org/10.5255/UKDA-SN-9050-2) · [DESNZ technical annex §A2](https://assets.publishing.service.gov.uk/media/6a450b75e50f952c9b89e285/cfp-technical-annex-heat-pump-transition.pdf)
- **NGED South Wales LV。** 官方目录可见**全部 12 个 2025 月份**的数据分片。NGED 隐私计划规定每 **30 min** 聚合，公开最少 5 个电表。目录无可访问的资源地址（返回 `redacted`），无法验证同一南威尔士 feeder 整年、原始时钟、Wh/kWh 单位或缺失情况。包级 licence 字段为空。NGED Open Data Licence（基于 OGL v3.0）适用于资源明确标 Open 的情形。聚合序列本身缺少端用和气温测点，无法从总 feeder 需求识别空间供暖系数。 [NGED 目录 API](https://connecteddata.nationalgrid.co.uk/api/3/action/package_show?id=aggregated-smart-meter-data-lv-feeder) · [数据与聚合规则](https://customer.nationalgrid.co.uk/downloads-view-reciteme/657539) · [NGED 许可](https://www.nationalgrid.co.uk/open-data-licence)

## TEMPERATURE_ADJUSTED_SCENARIO · 待校准

用可辨识的 **空间供暖 AC 电输入** 测点和同步室外气温拟合，先以按周分块的训练和留出期测试温度变点模型。若数据来自热计量，需根据设备类型把 `kWhₜₕ` 映射到 `kWhₑ`。热泵使用与供回水、室外温度和辅机边界匹配的 COP，直接电表校准的分支无需再除一次 COP。若分项表暂不可得，可先建立有独立建筑面积、热损失、室温设定和设备电气资料的工程模型。本轮既无端用电气曲线也无独立参数，未赋值下表任何调整项。

| 待估项 | 数据或方程 | 主要未知 |
| --- | --- | --- |
| 供暖平衡点及有效电功率斜率 | 分项电表拟合 `P_heat(t) = b_heat × max(0, T_balance − T_out(t))`，有证据再加入设定点、延迟与 duty 状态 | 供暖技术、围护结构、占用、舒适设定及相似建筑样本 |
| COP / 直接电热效率与 AC 辅助负荷 | 对匹配设备使用已验证性能曲线或热量、电量双表，型号和安装边界必须明确 | 水温、化霜、备份电热、循环泵和温度对应关系 |
| 非关键制冷 | 有独立 cooling AC 数据时另拟 `b_cool × max(0, T_out(t) − T_cool)` | 制冷设备、时段、传感器、风机和制冷回路计量 |
| 峰时容量与置信区间 | 由匹配设备电气边界和连续寒热窗留出验证确定 | 峰值误差、外推稳定性、不同物业类型的系数迁移 |

达门槛后逐时替换原有、已计入的同名 HVAC 项。`P_adjusted = P_frozen − P_HVAC_old + P_HVAC_calibrated`，非 HVAC 和未校准的制冷保持原口径，Dedicated C4ISR cooling 也保留排程。年度净变化允许由证据决定。随后对账月总量、日均、冬夏供暖/制冷、年度电量差、峰值及其时点。只有新序列通过 8,760 小时时间完整性和分项电量对账，才准备隔离的 24/72/168 h outage 比较。现为 **NOT RUN**。

## 图表与复现

四张图均为 300 dpi。供暖图展示冻结 HVAC 与气温，温度校准曲线在证据缺口关闭后才可绘制。

1. [Central 月度端用堆叠](../../Image/temperature-driven-load-calibration/20261120/01_monthly_stacked_end_uses.png)
2. [Central 月日均用电对 T2M](../../Image/temperature-driven-load-calibration/20261120/02_daily_electricity_vs_t2m.png)
3. [基准供暖、制冷与 T2M](../../Image/temperature-driven-load-calibration/20261120/03_scheduled_hvac_and_t2m.png)
4. [Low / Central / High](../../Image/temperature-driven-load-calibration/20261120/04_low_central_high_monthly.png)

从 `Week7Remake` 执行。使用已验证的 Python 3.12.10 和 Matplotlib 3.11.2，两个输出参数指向新目录。

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python -B -m research_evidence.temperature_driven_load_calibration.reproduce --output-dir lc1-temperature-review --figure-dir lc1-temperature-review/figures
```

独立回归 Week7Remake **143/143 PASS**、Initial Draft **53/53 PASS**，公开和完整 Baseline **142/142、166/166 PASS**。Original Package **367/367**，Stage 7 output **16/16**（公开与私有各自核对），Stage 8 七份清单 **324/324**，EV fixture **3/3**。同环境独立复算月度 CSV 和 JSON 的 SHA-256 一致。原始资料及 provider snapshots 保存在私有研究档案 `Reference/Research documents/LC1_temperature_driven_load_20261120/`。
