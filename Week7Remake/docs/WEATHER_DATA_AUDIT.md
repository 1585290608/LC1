# LC1 Sennybridge Weather Data Audit

审计日期 2026-11-20。范围包括 Git `Week7Remake` 的 `data/`、`research_evidence/`、Python 入口和已有交付文件，以及本地研究档案中的 `case_study_v6`、气象源文件、处理脚本和已保存的模型输入复读记录。下文“档案”指本地 LC1 研究原件，“仓库”指 Git 的 `Week7Remake`。仓库核对基点为 `fca1878d009a202f35852fa75853cbc6de7fe463`。

**结论。现有资料足够继续使用 2025 年单年基准。** 已验证该地点有完整的 NASA POWER 小时级 GHI、10 m / 50 m 风速和 2 m 气温，以及从同一序列生成的 PV/Wind 可用功率曲线。未找到独立的小时 DNI/DHI 实测或产品文件，也未找到第二个完整气象年。年度确定性和年内 outage 研究目前无需下载气象数据。若研究目标扩展到多年气候概率、极端低可再生出力或设备场址验证，再按目标补充数据。

## 1. 现有气象与功率时序

NASA POWER 原始 CSV 的查询坐标为 **51.95°N、3.57°W**。文件注明网格平均地形高程为 **245.39 m**，属于 MERRA‑2 网格地形值。GHI 随档产品为 CERES SYN1deg all-sky 格点估计。风速和气温来自 MERRA‑2 再分析产品。该日期序列对应实际 2025 年，证据类型为卫星与模型融合的辐照资料及气象再分析。仓库与档案中未核到营地站点或测风塔记录，也未核到 TMY 系列。 [NASA POWER 小时数据说明](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/) · [NASA POWER 气象来源](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/)

下表所有 Sennybridge 年序列均为 1 h，覆盖 **2025-01-01 00:00 至 2025-12-31 23:00**，第一条对应 `[00:00, 01:00)`。采用 NASA POWER **Local Solar Time（LST）** 分带和 LC1 固定小时索引。档案对本点按 UTC+0 作几何计算，转换时取每小时中点。没有加入英国夏令时 BST 的跳时或回拨。仅有整数序号的文件用档案 `data/mdt_import_v6/time_index_reference_NOT_FOR_GUI_IMPORT.csv` 对应日期。 [NASA POWER 时间和数据常见问题](https://power.larc.nasa.gov/docs/faqs/data/)

| 路径 / 文件 | 字段、单位与来源 | 完整性与证据类型 |
| --- | --- | --- |
| 仓库 [data/nasa-power-sennybridge-2025.csv](../data/nasa-power-sennybridge-2025.csv) | `ALLSKY_SFC_SW_DWN` 为水平面 GHI，每小时 Wh/m²。WS10M / WS50M 为网格地面上 10 / 50 m，单位 m/s。T2M 为 2 m 气温，单位 °C。坐标和来源见上文 | 8,760 条，零缺小时、零重复时间、零空值、零哨兵值或非有限值。与档案原始下载件及档案规范副本逐字节一致 |
| 仓库 [data/solar.csv](../data/solar.csv) · [data/wind.csv](../data/wind.csv) · [data/temp.csv](../data/temp.csv) | `ghi_wh_m2`、`ws10_ms / ws50_ms`、`temp_c`，分别重排上述原始字段，保留单位和测量高度定义 | 每份各 8,760 条，零缺失、零重复、零异常编码，逐时等于原始字段。与同名档案文件逐字节一致 |
| 仓库 [data/v6_solar_pu_index_value.csv](../data/v6_solar_pu_index_value.csv) · [data/v6_wind_pu_index_value.csv](../data/v6_wind_pu_index_value.csv) | 2025 同点气象的 v6 转换。PV 为 AC 可用功率 / DC STC 名牌功率，Wind 为净可用功率 / 风机额定功率。均为 p.u. | 各 8,760 条，编号 1 至 8,760 连续且唯一，无缺值或非有限值。和档案 MDT 导入文件逐字节一致 |
| 档案 `LC1_MDT/case_study_v6/renewable_hourly.csv` | 除两条 v6 p.u. 曲线外，包含 POA W/m²、PV cell temperature °C、40 m hub wind m/s | 8,760 条，零缺失、零重复。两条曲线与仓库输入逐点最大绝对差均为 **0 p.u.**。属于模型派生天气和可用功率 |
| 仓库 [week7/stage3/external_inputs/LC1_reference_profiles_8760.csv](../week7/stage3/external_inputs/LC1_reference_profiles_8760.csv) | 2025 LST 气象派生 PV/Wind p.u. 与负荷对照，包含从零开始的小时索引 | 8,760 条，零缺失、零重复。两条曲线与仓库功率输入逐点最大绝对差均为 **0 p.u.**，文件 SHA-256 与已有 [provenance manifest](../week7/stage3/external_inputs/LC1_external_input_provenance.json) 一致。用途为 handoff |
| 档案 `LC1_MDT/{screening_v2,verified_screening_v3}/{solar,wind}_power_pu.csv` | 同一 NASA POWER 年份的历史模型曲线。PV 用 GHI × 0.85 的归一化近似，Wind 用 50 m 风速和通用 3/12/25 m/s 曲线 | 四份文件各 8,760 条，无缺时或重复。同类 v2 与 v3 文件逐字节一致。与现行 v6 转换方法有别，仅供历史追溯 |

档案 `config/lc1_weather_source_receipt.json` 记录了原始下载、坐标、时段、原始单位及文件哈希。原始接收件为 `data/Sennybridge 2025 年气象数据/POWER_Point_Hourly_20250101_20251231_051d95N_003d57W_LST.csv`，规范副本为 `data/nasa_power_sennybridge_2025.csv`。仓库原始文件重新计算的 SHA-256 为 `2a59fbfd46bdb9b2cb24b67436dacd43ec8e42108ce4269e8506f8158b52e120`。审计核查现存副本、官方产品说明和已保存回执。

在本次核查目录内，未发现 PVGIS、ERA5/ERA5-Land 或 Met Office 的独立可用小时数据，也未发现 8,784 h 闰年文件、多年气象序列或原始小时 DNI/DHI。研究证据中的外部数据名和方法引用不能证明文件已下载或已接入。档案 `MDT_DATA_SOURCES_AND_IMPORT.md` 还区分了只有 8,759 条的 PyMDT 官方 solar 示例 `official_solar_raw_8759_NOT_FOR_LC1.csv`，该示例未用于威尔士模型。现有原始气象 CSV 没有湿度、降水、风向或阵风字段。未逐个展开历史备份 ZIP，因此以上结论限定于核查范围。

## 2. 质量与地区代表性

全年 GHI 合计 **1,170.11 kWh/m²**，小时范围 0–899.17 Wh/m²。10 m 平均风速 **4.98 m/s**，范围 0.01–17.35 m/s。50 m 平均风速 **7.12 m/s**，范围 0.03–23.04 m/s。2 m 平均气温 **9.71°C**，范围 −3.36 至 27.13°C。核查未见负 GHI、负风速或时序断点。记录为零的 GHI 是有效数据。所有 GHI 为零的小时，v6 PV 可用功率也为零。

| 2025 季节 | 小时 | GHI 累计 kWh/m² | 10 m / 50 m 平均风速 m/s | 2 m 平均气温 °C | PV / Wind 平均可用功率 p.u. |
| --- | ---: | ---: | ---: | ---: | ---: |
| DJF | 2,160 | 85.16 | 5.72 / 8.15 | 4.21 | 0.0495 / 0.5249 |
| MAM | 2,208 | 422.86 | 4.33 / 6.14 | 9.03 | 0.1831 / 0.3346 |
| JJA | 2,208 | 484.69 | 4.49 / 6.35 | 15.58 | 0.1847 / 0.3626 |
| SON | 2,184 | 177.40 | 5.39 / 7.87 | 9.90 | 0.0850 / 0.4974 |

DJF 按 2025 年 1、2、12 月分组。全年 v6 PV 为 **1,104.66 kWh/kW DC**，Wind 为 **3,759.63 kWh/kW rated**，均是在限发、故障和 dispatch 前对可用功率积分的结果。夏季辐照较强、冬季较冷且平均风速较高，方向上与威尔士海洋性气候相容。单年粗网格序列无法验证营地局地遮挡、山脊与谷地差异、湍流、结冰、年际变动和极端值。尤其不能把约 0.429 的年均 Wind p.u. 当作安装点的实测容量因子或 50 m 风速。 [Met Office 英国区域气候概述](https://www.metoffice.gov.uk/research/climate/maps-and-data/regional-climates)

## 3. 实际模型依赖

| 用途 | 证据与结论 |
| --- | --- |
| Python annual / islanded | 主模型 `build_model`、grid-connected dispatch、Stage 6 annual 和 Stage 3–4 screening 读取 v6 p.u. 文件。可用功率由归一化时序乘装机容量得到。原始 GHI、风和温度拆分 CSV 留作预处理输入与溯源，以上 dispatch 入口不直接进行气象转功率。 [核心模型](../models/core/simulate.py) · [Grid dispatch](../models/grid_connected/dispatch.py) · [Stage 6 annual](../week7/stage6/annual_grid.py) · [Islanded screen](../week7/nextstage/screen.py) |
| PV 离线转换 | 档案 `scripts/lc1_renewable_profiles.py` 与 `config/lc1_renewable_assumptions.json` 记录 GHI → Erbs 估算 DNI/DHI → POA → PVWatts DC / inverter AC。使用固定南向 35°、albedo 0.2、10% DC 合计损失、1.1 DC/AC 和 96% 标称 inverter efficiency。T2M 与 WS10M 用于 SAPM cell temperature。档案 `renewable_profile_verification.json` 记录太阳落在地平线下的少量 GHI 在转换阶段归零，原始值仍在 CSV 中。DNI/DHI 是计算中间量，无独立小时数据证据 |
| Wind 离线转换 | 档案脚本用 10 m 和 50 m 风速做对数高度插值至 40 m hub，采用 NREL DW100 100 kW / 27.6 m rotor 参考功率曲线并扣 7% 损失，输出归一化功率。可按 LC1 容量假设缩放，场址风机型号及其功率曲线仍待确认。归档配置未对地形、风向、现场空气密度或结冰单独校准。 [NREL DW100 参考曲线](https://natlabrockies.github.io/turbine-models/2019COE_DW100_100kW_27.6.html) |
| Heating/HVAC | Low/Central/High 的供暖、通风、制冷和 C4ISR cooling 由设备容量、月份、小时及 duty/schedule 假设决定。举例，住宿供暖在 Oct–Apr 使用 17:00–05:00 LST 时段。当前负荷生成器未读取 T2M，未实施 heating degree-hours、建筑热响应或温度相关 COP。T2M 的已确认用途是离线 PV 预处理。 [负荷生成器](../week7/load_model.py) · [设备假设](../week7/config/equipment.csv) |
| MDT case_study_v6 | 档案 `scripts/build_lc1_case_models.py` 将 v6 资源时序载入模型。对照 `LC1_MDT/case_study_v6/manifest.json`，重新核对存档的 **9/9** MBF 文件 SHA-256。按小端 IEEE 754 double 重算仓库曲线的数组 SHA-256，两条曲线都匹配 `fresh_process_verification.json` 中 **9/9** 个 24/72/168 h 配置的既有资源复读记录。证明相同资源输入已存入模型，未新增 solver 证据 |
| MDT Stage 8 和 legacy 标签 | Stage 8 P1/P2/W1/W2 和 PV observability 探针使用受控可用功率边界，属于 synthetic component fixtures。归档 `t17_native_mdt_v1/v6_native_readback.json` 中 `wind_profile.mean_ms` 为 **0.42918201548**，实际匹配 v6 年平均 **p.u.**。应按数组定义解释，不能用作 m/s 指标。 [Stage 8 索引](../week8/README.md) |
| HOMER Pro | Stage 7 handoff manifest 有 4 个 8,760 小时 kW 负荷文件，分别是 Low、Central、High planned EV 总负荷与 Central C4ISR。Stage 3 综合 handoff 包含资源列。核查范围内未找到 HOMER Pro 项目从现有气象文件导入的记录、可核验的 native 配置或气象运行结果。 [HOMER import manifest](../week7/stage7/external_handoff/stage7_HOMER_import_manifest.csv) |
| 24 / 72 / 168 / 336 h outage | Stage 3 从 2025 v6 序列每隔 168 h 选一个起点，共 52 个起点，分别取其后的连续 24/72/168 h。最后 24 小时未进入这组最长窗口。Stage 4 contingency 沿用它。历史 C4 336 h 从年初的连续切片开始，stress 变体把可再生输入缩至 60%，并配置第 48–72 小时的 DG 停运。缩放与停运是情景设定，不提供实际气象或故障发生频率。 [Stage 3 窗口](../week7/stage3/weekly_scan.py) · [Stage 4 contingency](../week7/stage4/contingency.py) · [C4 定义](../models/islanded/contingencies.py) |

v6 MDT 资源输入可复核的 SHA-256 如下。数组哈希基于按 CSV 顺序串接的 8 字节 little-endian IEEE 754 double，不含 CSV 文本或时标。

| 资源 | CSV SHA-256 | 数组 SHA-256 |
| --- | --- | --- |
| PV | `75c740785c5257bbd2805634f2754915c3576db93eecac619f1a2dfa9646cd34` | `9ea89e862cca3a10c6c717e62bd20e1e616a55a6b244529931560060567efc88` |
| Wind | `7acce0b08c4c5e9846010228fdd105f67f1438d555b79d5a1cbf9aeae089c853` | `8a41b7fc1a88f2df400a84cd101251969feb764fc2981e40185533cc3fd87924` |

## 4. 适用性与缺口

| 研究用途 | 判定 | 何时才需要补充数据 |
| --- | --- | --- |
| Annual techno-economic simulation | **足够用于 2025 确定性基准。** 同步 PV/Wind 时序覆盖全年 | 如需多年经济风险、气候代表年或 P50/P90，需要同期的多年小时辐照和风，并保留原时间基准 |
| Seasonal PV/Wind generation | **足够描述 2025 年季节差异。** PV/Wind 发电量均基于参考转换 | 如需验证 PV 分解或 POA，可补独立 DNI/DHI、POA 或实际 PV 曲线。如需设备级场址 Wind 产能，优先补近场或 hub-height 测风及匹配的风机曲线 |
| Temperature-dependent heating | **有气象输入，模型与验证资料待补。** 2025 T2M 可供拟合或做 heating sensitivity，当前 Heating/HVAC 输出仍来自固定日程 | 先确认热损失、设定点、建筑/设备 COP、占用和实测负荷。若后续验证冬季设计工况，再补具有代表性的近场冷季、多年或极端温度记录 |
| Consecutive outage studies | **足够用于落在 2025 年内的连续 24/72/168 h 与已有 336 h 情景。** 可保留风、太阳和温度的同期关系 | 跨年窗口需要相邻年份的真实连续小时数据。估计长时低风低光和寒冷共现的重现期还需要多年序列，不能把 2025 年尾与年初拼接成实际事件 |
| Reliability / Monte Carlo | **固定 2025 气象条件下可做情景敏感性。** 档案 config 的 `repeat_weather_in_monte_carlo` 为 `true`。重复同一气象年没有增加气候样本 | 校准天气相关 outage 概率或尾部风险时，需要多年同步小时气象。电网故障、恢复时长、设备故障及其天气关联需要独立证据，单靠增加气象年无法推定 |

**目前无需新增 Sennybridge 气象下载。** 年度基准和既有停电情景继续使用已核验的 2025 输入。若下一阶段做 Heating/HVAC，先复用 T2M，记录温标与 LST 小时对齐，另行取得热负荷校准证据。若下一阶段提出多年可靠性或气候代表性要求，再确定所需的时间跨度、站点或网格以及原始变量。

## 5. Preservation

审计仅静态读取文件、核对引用、检查序列并计算哈希。Low/Central/High 三份仓库基准负荷 CSV 分别与原工作档案对应文件逐字节一致。未下载新气象数据、运行 Python/MDT/HOMER 模拟、修改既有参数或覆盖历史结果。
