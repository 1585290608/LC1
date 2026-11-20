# LC1 HDH Heating Sensitivity

2026-11-20 · Cardiff University EN3400 · Hypothetical 120-person camp · Fixed 2025 LST

**Central 年总用电维持 763,901.095464 kWhₑ，年供暖维持 72,768 kWhₑ。** 在原有供暖时段内按气温重排后，15.5°C 情景将供暖移向较冷月份，年峰值从 **195.09** 升至 **201.09 kW**。这项试验只改变用电发生的时间。结论适用于本研究的假定供暖策略和代表性天气年。 [情景汇总](HDH_SCENARIO_SUMMARY.csv) · [全年逐时序列](HDH_HOURLY_8760.csv)

## 时间、能量与证据边界

- `MODELLED_BASELINE` 为冻结 2025 Low/Central/High。Central 原始日均 **2,092.88 kWhₑ/day**、平均 **87.20 kW**、最小 **50.60 kW**，峰值最早发生在 **1 月 2 日 18:00 LST**。从原 CSV 逐时复算 `E_{category,month} = Σ(P_category(t) × 1 h)`，月日均为月电量除以该月天数，年度为十二个月之和。各情景均有 14 个基础设施端用与独立 EV AC 充电列。峰值是单个 1 h 间隔的平均功率最大值。
- `NASA_POWER_METEOROLOGICAL_INPUT` 为已存档的 NASA POWER / MERRA-2 2 m 气温。源位置 **51.95°N、3.57°W**。按相同 source LST 时间戳读取，2025 年 8,760 小时，无 DST 转换。每个 `data/temp.csv` 气温值均与原 NASA 文件 T2M 一一匹配。 [气象审计](../../docs/WEATHER_DATA_AUDIT.md) · [NASA 小时产品说明](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/)
- `MEASURED_EXTERNAL_REFERENCE` 为此前筛查的住宅热泵资料。其电气计量有用，但目前缺少营地建筑与设备匹配，也缺乏可转用的空间供暖分项、热水分离和温度测点证据。没有从其电表或 COP 拟合 LC1。 [上一轮证据](../temperature_driven_load_calibration/TEMPERATURE_LOAD_CALIBRATION.md) · [输入来源与哈希](SOURCE_MAP.csv)
- `TEMPERATURE_INFORMED_SYNTHETIC` 为能量守恒的数学情景。中心 **15.5°C** 对应 Met Office 度日产品的英国常见报告基准，**14.5°C** 与 **16.5°C** 为上下各 1°C 的窄敏感性。本研究采用逐时阈值计算；Met Office 文件提供的是逐日参考定义。三点均为假设的 balance point。 [Met Office guidance, p. 15](https://www.metoffice.gov.uk/binaries/content/assets/metofficegovuk/pdf/business/sectors/construction-catalogue-v3.pdf)

## Scenario A / B 与安全边界

1. 计算每小时非负权重 `HDH(t) = max(T_base − T_out(t), 0) × 1 h`。仅在冻结排程允许供暖且 summer cooling 为零的小时保留该权重。允许时间为 **10–4 月 17:00–05:00** 与 **5、9 月 18:00–02:00**，共 **3,032 h**，跨午夜按各小时所属月份判定。
2. 先检查容量 `30 kW × 正权重小时数 ≥ 72,768 kWhₑ`。主情景的 **3,004 h** 对应 **90,120 kWhₑ** 可分配容量，裕量 **17,352 kWhₑ**。低/高两点容量分别为 **89,130 / 90,660 kWhₑ**。容量不足将报告 `INFEASIBLE`。
3. 解 `Σ min(30, α × w(t)) × 1 h = 72,768 kWhₑ`，其中 `w(t) = 有效 HDH(t) / 1 h`。迭代固定达到上限的小时，将剩余电量按其余权重归一化。主情景 `α≈3.23328 kW/°C` 由年度配额决定，仅用于将权重映射为功率。主情景有 **1,397 h** 触及 30 kW 上限。原 Central 启用小时是 **24 kW = 30 × 0.80**，故同一额定功率下允许部分小时超过原 Central 的 24 kW。所有温度点使用同一 30 kW 上限。
4. `P_B = P_A − P_heating,A + P_heating,B`。只替换空间供暖。C4ISR、Medical、Security、General Auxiliary、Summer Cooling 与 8,760 小时计划 EV 逐时一致。kWhₑ 指电输入，模型未引入 COP、热输出、建筑热损失或新设备。输出电量和峰值按 1 h 数值比较。

分配器按 **10⁻⁷ kWhₑ** 的年电量容差验收，表内保存至 12 位小数。三温度点绝对年差均 ≤ **4×10⁻¹² kWhₑ**。同一年内把能量移入寒冷时段可增加峰值。跨年温差会如何改变年供暖总量不在本次固定年配额的识别范围内。

## 月度和年度结果

中间两列为 **kWhₑ/月 / kWhₑ/day**。最右列为 **空间供暖 kWhₑ/月**。全量月表还保存温度、HDH、分项电量及日均值、月平均/最小/最大 kW。

| 2025 LST | 原 Central | HDH 15.5°C | Heating A → B |
| --- | ---: | ---: | ---: |
| 2025-01 | 67,474.64 / 2,176.60 | 69,491.51 / 2,241.66 | 8,928.00 → 10,944.87 |
| 2025-02 | 60,741.34 / 2,169.33 | 62,354.18 / 2,226.93 | 8,064.00 → 9,676.84 |
| 2025-03 | 66,990.15 / 2,160.97 | 68,316.39 / 2,203.75 | 8,928.00 → 10,254.24 |
| 2025-04 | 65,144.25 / 2,171.47 | 65,028.69 / 2,167.62 | 8,640.00 → 8,524.44 |
| 2025-05 | 64,286.15 / 2,073.75 | 62,216.29 / 2,006.98 | 5,952.00 → 3,882.14 |
| 2025-06 | 57,802.95 / 1,926.77 | 57,802.95 / 1,926.77 | 0.00 → 0.00 |
| 2025-07 | 59,971.05 / 1,934.55 | 59,971.05 / 1,934.55 | 0.00 → 0.00 |
| 2025-08 | 59,550.15 / 1,920.97 | 59,550.15 / 1,920.97 | 0.00 → 0.00 |
| 2025-09 | 62,331.37 / 2,077.71 | 60,248.27 / 2,008.28 | 5,760.00 → 3,676.91 |
| 2025-10 | 67,474.64 / 2,176.60 | 66,169.29 / 2,134.49 | 8,928.00 → 7,622.65 |
| 2025-11 | 64,723.35 / 2,157.44 | 64,276.07 / 2,142.54 | 8,640.00 → 8,192.72 |
| 2025-12 | 67,411.05 / 2,174.55 | 68,476.24 / 2,208.91 | 8,928.00 → 9,993.19 |

DJF（1、2、12 月）日均电量由 **2,173.63** 增至 **2,225.80 kWhₑ/day**，JJA **1,927.44 kWhₑ/day** 保持一致。1 月增幅最大（**+2,016.87 kWhₑ**），9 月减幅最大（**−2,083.09 kWhₑ**）。主情景最大逐时增加 **6.00 kW**，最大减少 **24.00 kW**。最早年峰出现时间仍为 1 月 2 日 18:00 LST。按功率降序和时点升序打破同值并列，主情景与原 Central 年度前 100 个高需求小时有 **81** 个重合。三个平衡温度的年度峰值均为 **201.09 kW**，DJF 日均在 **2,223.53–2,228.08 kWhₑ/day**。

## Dissertation Figures

| 图 | PNG 300 dpi | Vector PDF |
| --- | --- | --- |
| 1 月度分项堆叠 | [PNG](figures/01_monthly_electricity_by_end_use.png) | [PDF](figures/01_monthly_electricity_by_end_use.pdf) |
| 2 年度端用份额 | [PNG](figures/02_annual_electricity_breakdown.png) | [PDF](figures/02_annual_electricity_breakdown.pdf) |
| 3 月日均与室外温度 | [PNG](figures/03_daily_demand_and_temperature.png) | [PDF](figures/03_daily_demand_and_temperature.pdf) |
| 4 年度守恒下的月供暖与 HDH | [PNG](figures/04_calendar_vs_hdh_heating.png) | [PDF](figures/04_calendar_vs_hdh_heating.pdf) |
| 5 月日均、峰值对照 | [PNG](figures/05_calendar_vs_hdh_total_load.png) | [PDF](figures/05_calendar_vs_hdh_total_load.pdf) |
| 6 代表性冷季周逐时总负荷与供暖 | [PNG](figures/06_representative_winter_week.png) | [PDF](figures/06_representative_winter_week.pdf) |

用既有 Python 3.12 和 Matplotlib 从 `Week7Remake` 运行。输出指向新目录。

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python -B -m research_evidence.hdh_heating_sensitivity.study --output-dir research_evidence/hdh_heating_sensitivity/reproduction
```
