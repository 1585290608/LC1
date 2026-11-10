> GitHub working copy. Local home directory redacted. Original SHA-256: 62c6b86c8e7e09c53afb5d6f7448ca26f62c00c2efcf0b8e8da81359f6630109.

# DG Fix Validation Report — Draft 2

日期：2026-11-05。研究：Techno-Economic Optimisation and Resilience Assessment of a Grid-Connected Hybrid Microgrid with Islanding Capability for Defence Applications。

**COMPLETE — SCOPED MODEL-INTEGRITY VALIDATION PASSED**。此结论只针对已声明边界和假设下的数值模型完整性修复，不是设备、UPS、成网、保护或整套混合系统工程认证。未开始IEEE LaTeX论文，经济性和回本结论继续暂停。

## A. Root cause analysis：先区分实际版本

缺陷原件位于 `USERPROFILE/Documents/DeepSeek HARNESS/LC1 Remake/src/`；`USERPROFILE/Documents/LC1 Remake/archive_original/`中的对应两份源代码SHA256完全相同。其原始结果、Draft1审计和图表也在前一路径。公开根目录`LC1 Remake/src`是后来的v2，V16及Thesis_Research又是同一份更新的v2源代码；它们不是本次v1缺陷原件，不能把758L案例直接归为V16当前结果。版本映射在 `evidence/MODEL_VERSION_MAP.json`。

本次修复位于独立工作目录`Validation/Draft2_DG_Fix`，本地Git分支`fix/dg-energy-accounting-draft2`。初始源代码提交8180395，经过物理测试的修复提交e80a567；原件、v2/V11–V16及经济工作区未被覆盖。

1. **Error A**：冻结副本 `before/src/simulate.py:67` 将Diesel.dispatch的真实生成输出覆盖成serve返回的负荷送达量。组件已经按最低25kW燃油计费，但系统日志与旧residual都只用送达量，所以同一错误变量在平衡两侧相消。独立只读插桩不改变返回值，逐项复现8,760行原始数据，最大差为0。
2. **Error B**：`before/src/simulate.py:145` 用第一小时末库存加整段已记负载供能/4拼凑初始燃油。24/72/168h分别报告2017.240198、2396.739071、2674.182820L，超出实际2000L。它既错用了时间边界，也错把送达量当成所有生成量。
3. **Error C**：`before/src/simulate.py:147` 把第一小时末SOC0.7171302035当初始值，实际构造器初始为0.70。

原始油箱下降758.663785557476L；按日志负荷送达供能计算674.182819549682L；真实DG生成3034.655142229904kWh、日志送达2696.731278198728kWh。漏记337.923864031176kWh，对应84.480966007794L。原有residual最大1.42e−14kWh仍“通过”，而独立全AC残差最大24.052662307156kWh、累计337.923864031176kWh。数据与未修改的插桩代码在 `evidence/LEGACY_DEFECT_REPRODUCTION.json`、`scripts/reproduce_legacy.py` 和 `runs/LEGACY_INSTRUMENTED_GENERATION.csv`。

原17项测试实际通过，却没有检测该缺陷。这证明旧测试通过不能替代独立物理账目审计。第一次按整个旧tests目录收集时误将非UTF8历史TEST_REPORT.txt作为文本测试收集，失败日志已保留；随后明确执行原`test_model.py`，17项通过。未改旧测试预期。

## B. Code changes：隔离、明确并保留行为变化

| 修改文件/函数 | 具体变化 | 必要边界 |
|---|---|---|
| `src/components.py:36` Diesel.dispatch | 实际生成与负荷去向分离；dt显式；保存ON功率、实际运行时间、OFF/ON剖面、库存与燃油消耗 | 固定0.25L/kWh为研究假设 |
| Diesel最低出力/缺油 | ON功率≥25kW且≤100kW；缺油可运行不足整步，平均功率可能低于25，但实际ON功率不低于最低值 | 不是低负载连续运行；无怠速/启动额外燃油模型 |
| Diesel零需求/启停 | 无需求时停止，随后新需求重新等待1h启动 | 修复原RUNNING标记在零输出时一直保留的歧义，会改变调度结果；未增加优化控制器 |
| `src/simulate.py:43–73` step | 独立记录DG generated/delivered/toBESS/dumped及fuel；按真实运行片段分配负荷、UPS及余量 | RE→BESS→按需DG→关键UPS的原优先顺序保留 |
| BESS与UPS | 每步清除旧损耗/功率；移除同一步可能重复放电的分支；DG充电须显式允许、连接假设、PCS/SOC/效率可行；UPS依据真正DG输出缺口供电并明确再充电 | 主参考关闭DG充BESS；UPS是理想AC可送达7.5kWh储备，不是厂家DC电池或转态认证 |
| 全系统平衡 | 实际注入PV/Wind=available−curtail；独立记录电池内部能量、燃油、负荷服务和DG去向 | 零线路损耗假设；不要再把curtail重复算成发电 |
| `src/simulate.py:100` event_metrics | 起始状态来自首步dispatch前，末态来自末步后；输出start/end-exclusive、三负荷层ENS/EA及DG各能量去向 | 确定性缺供使用ENS；不再输出EENS字段 |

**余量必须有去向**：主参考采用显式假设25kW AC吸收/电阻负载，余量转为热。它不是已安装设备。默认不允许DG给BESS充电；允许时另由布尔控制、共同AC连接假设、PCS和SOC限制验证。若无允许充电或吸收负载，运行会报告InfeasibleOperatingPoint，负对照不被当成有效供电结果。`runs/PHYSICAL_CONTROLS/NO_SINK_INFEASIBLE.json`保存原始异常；没有默默丢弃能量或把余量自动塞入BESS。

缺油示例：只有1L、15kW负荷、DG已启动。25kW运行0.16h，生成4kWh，其中负荷2.4、dump1.6，燃油1L、末库存0，负荷ENS12.6kWh。不能把平均4kW当成发电机低于25kW连续运行。真实机组的燃油枯竭/停机动力学仍未验证。

## C. Before/after：结果发生变化，不是只改列名

以下均为原始起点0、首168h断网随后全年并网的8,760h场景。before“生成量”来自原代码真实dispatch返回的只读插桩，不能把它说成旧CSV原本已完整记录。

| metric | before | after | units |
| --- | --- | --- | --- |
| DG generated | 3034.655142229904 | 2934.655142229904 | kWh |
| DG delivered | 2696.7312781987275 | 2668.491893701794 | kWh |
| DG dumped |  | 266.1632485281098 | kWh |
| Fuel consumed | 758.6637855574763 | 733.663785557476 | L |
| SOC initial | 0.7 | 0.7 | fraction |
| SOC final | 0.3 | 0.3 | fraction |
| Grid import | 162532.97892069284 | 162539.60887727374 | kWh |
| Grid export | 2154.625998961989 | 2154.625998961989 | kWh |
| C4 ENS | 0.0 | 0.0 | kWh |
| Full AC max residual | 24.052662307155927 | 1.4210854715202004e-14 | kWh |


修复后2934.655142kWh=2668.491894kWh负荷送达+266.163249kWh显式dump；DG到BESS为0。实际油耗733.663786L=.25×生成kWh，初始2000L，168h后1266.336214L。新状态切换和UPS供能使发电、弃能、负荷分配与电网再充电发生变化，因此未假设修复前后调度相同，也未调整参数维持旧EA。

## D. Validation：实际执行的物理及负对照

原测试17通过；新增物理测试15通过，覆盖A–K要求。`TEST_RESULTS.csv`由真实JUnit XML提取测试名称；`logs/PHYSICS_TESTS.log`、`evidence/PHYSICS_TESTS.xml`保存实际结果。

| name | status |
| --- | --- |
| test_A_minimum_generated_not_overwritten_by_delivered | PASS |
| test_B_full_load_limit | PASS |
| test_C_partial_final_fuel_preserves_minimum_on_power_and_destinations | PASS |
| test_D_one_hour_startup_and_actual_UPS_energy | PASS |
| test_D_fractional_timestep_startup_and_zero_demand_shutdown | PASS |
| test_E_battery_energy_power_efficiency_bounds | PASS |
| test_E_DG_charges_only_when_explicitly_permitted_and_connected | PASS |
| test_F_connected_import_export_no_diesel_or_simultaneous_flows | PASS |
| test_G_island_has_zero_grid_exchange | PASS |
| test_H_critical_first_under_shortage | PASS |
| test_I_initial_states_are_pre_dispatch_and_event_indices_exact | PASS |
| test_J_full_8760h_balances_each_interval | PASS |
| test_K_zero_RE_empty_fuel_min_SOC_unavailable_source | PASS |
| test_K_minimum_surplus_without_sink_is_infeasible | PASS |
| test_invalid_fuel_and_event_alignment_are_rejected | PASS |


模型和独立已保存CSV回读逐步容差为1e−7kWh（AC、DC、DG去向）、1e−7L（燃油）；库存累计1e−6L、原件复现差1e−9、负荷层每步1e−8kW。每步检查DG实际ON功率额定/最低值、储能90kW和SOC、无同时充放电、无禁止的同时进出口、孤岛进出口恒0。旧residual没有作为唯一验收依据。

5个新正式运行均在物理测试通过后执行，输入、代码SHA、配置、完整轨迹及独立SUMMARY在 `evidence/REVALIDATED_RUN_INDEX.json` 所列目录。另有11个保存的物理/负对照，一个无可行sink试验明确拒绝。单独Python进程重跑原年度场景，8,760行CSV逐字节一致：`evidence/REPRODUCIBILITY.json`。

| case | DGgenerated_kWh | DGdelivered_kWh | dump_kWh | fuel_L | C4_ENS_kWh |
| --- | --- | --- | --- | --- | --- |
| REFERENCE_ANNUAL168 | 2934.655142 | 2668.491894 | 266.163249 | 733.663786 | 0.000000 |
| GRID_ANNUAL | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| ISLAND_24H | 68.960791 | 68.960791 | 0.000000 | 17.240198 | 0.000000 |
| ISLAND_72H | 1709.984634 | 1586.956283 | 123.028351 | 427.496158 | 0.000000 |
| ISLAND_168H | 2934.655142 | 2668.491894 | 266.163249 | 733.663786 | 0.000000 |


原E24/E72/E168是同一个168h断网的重叠前缀。新24/72/168各自重新初始化运行，仍使用相同起点0和嵌套天气窗口；它们不构成统计独立的气象样本或Monte Carlo实验。独立初始化结果与原168h新轨迹对应前缀逐量核对一致。`REFERENCE_PREFIX_METRICS.csv`与各`EVENT_METRICS.csv`均保留。

全年GRID_ANNUAL是真正8760h全部并网、正常DG燃油0的独立运行，不是旧混合年度中8592h并网子集。初末SOC可能不同，故此处没有重复年NPC或回本结论。

## E. MDT comparison：修复与软件对照分开

使用真实保存的原生A_H24 MBF/MOF和FRESH_MOF_READBACK，重新检查原始SHA及版本化`require_saved_result`收据。没有修改原始MDT结果，也没有把Python输出伪装为MDT。本轮新原生求解次数为0，复用已有真实证据，而非声称软件无法运行。

`MDT_PYTHON_PARAMETER_MATRIX.csv`逐项记录天气起点、0/1基索引、PV/Wind、DG额定/最低/曲线、BESS、SOC、PCS、负荷、优先级、算法、时长、初始燃油和启动。主修复参考是50/50、PCS90、2000L、1h；它不是V16的75/75、PCS120、3000L、不同EMS。混合系统仍PARTIALLY_COMPARABLE。

独立24h DG-only控制采用已确认输入索引24、原生10s启动、DG100、无PV/Wind/BESS/UPS功率流及相同3000L库存。D0小时负荷序列与原生对齐，38–65kW域内25%最低出力约束不活跃；原生绝对UTC未直接导出，仍为UNVERIFIED。精确10s只用于分段能源积分，不能当成瞬态仿真。

- 原研究固定0.25L/kWh不变：生成1103.894444kWh匹配，但燃油275.973611L对原生360.842371L，差84.868760L，这是不同燃油假设，**不是原始84.480966L漏记缺陷**。整体PARTIALLY_COMPARABLE。
- 单独控制采用真实保存的五个USgal/kWh点和预先定义的分段线性比油耗插值，未拟合系数：DG能量、三负荷层服务/ENS、时长及燃油在max(1e−6,1e−9×native)容差内通过。只在该DG-only/full-event/无燃油枯竭/最低约束不活跃的范围标PARITY_VERIFIED。该控制不替换主研究的固定燃油模型，也不认证设备曲线、混合EMS或保护。

完整数值、差值和输入协议在 `MDT_DG_CONTROL_COMPARISON.csv`、`evidence/MDT_CONTROL_PROTOCOL.json`。V16已经记录的SOC端点缺失、早期充电与原生压力负荷比例分配限制保持不变。

## F. Remaining scientific limitations

真实dump负载、90kW PCS/kVA、线损、接地/保护、实际成网及UPS转态未验证。当前AC参考可用、PV/Wind可接入和零线路损耗是概念级假设，不是详细电路解算。SOC/效率固定，未建真实老化/温度/厂商限制。UPS7.5kWh是理想AC可送达库存；不能据此选定DC电池或保证30kW下15min实物续航。启停没有额外燃油、最短运行时间、爬坡或瞬态模型。

全系统能量守恒通过不代表所有控制策略都符合真实设备。明确停机/重启处理修复了零输出RUNNING状态歧义，但需要OEM控制资料才能用于部署。新数据支持数值能量、库存、时间边界与确定性负荷服务，不支持整套系统工程认证。

经济工作区`Thesis_Research`已按最新要求保留并暂停。本次未继续生成经济/回本图、优化结论或论文。其年度DGoff结果与原v1缺陷不是同一代码版本；是否重新发布经济结论须在独立经济验收中明确版本/边界，不能因本次软件修复自动视为通过。

## G. Publication readiness：逐图限定范围

以下VERIFIED表示来源哈希、已通过的新数值轨迹、单位/图例/数值和预览通过；不是实物认证。涉及原件的曲线明确是复现的失败诊断。假设设备存在/连接的工程含义仍CONCEPTUAL。未支持的经济、回本和全混合PARITY图没有生成。

| figure | publication_classification | scope |
| --- | --- | --- |
| DG_Generated_vs_Delivered_Energy | VERIFIED | Validated reference168h numerical DG destination accounting |
| DG_Fuel_Consumption_Validated | VERIFIED | Fuel inventory verified independently against actual ON-power/time integral |
| DG_Surplus_Energy_Accounting | VERIFIED | Before is a reproduced defect diagnostic; after uses independently validated new results |
| BESS_SOC_Revalidated | VERIFIED | Initial state before first dispatch; final state after each interval |
| Critical_Load_EA_ENS_Revalidated | VERIFIED | Prefix energy-service metrics with corrected pre-event SOC/fuel; deterministic ENS |
| Grid_Import_Export_Revalidated | VERIFIED | Pure grid-connected full2025; DGoff; not original8592h connected subset |
| Full_System_Energy_Balance | VERIFIED | Actual AC injection boundary excludes renewable curtailment; storage and fuel checked separately |
| MDT_vs_Python_DG_Validation | VERIFIED | PARITY_VERIFIED only for matched DG-only numerical energy/service/catalogue fuel; native outputs are inherited genuine evidence |


最终新图位于 `USERPROFILE/Documents/LC1 Remake/Latex_Images/Images/Draft 2/`，每图SVG、矢量PDF及PNG预览。raw CSV和每图metadata在本目录`figure_data/`，SHA及图表映射在`DRAFT2_FIGURE_REGISTER.csv`，8张/24个资产已逐张检查。Draft1没有被覆盖。

## H. Reproducibility and preservation

先读`README.md`，使用独立`.venv`和本地wheel包。代码/数据均从本目录相对路径加载，不需要对V16或旧项目写入。复制原件只读复现与新修复运行分别在`before/`和`src/`。

```powershell
.\.venv\Scripts\python.exe -X utf8 -m pytest -q -p no:cacheprovider tests --junitxml=evidence\PHYSICS_TESTS.xml
.\.venv\Scripts\python.exe -X utf8 scripts\reproduce_legacy.py
.\.venv\Scripts\python.exe -X utf8 scripts\run_revalidated.py
.\.venv\Scripts\python.exe -X utf8 scripts\save_controls.py
.\.venv\Scripts\python.exe -X utf8 scripts\compare_native.py
.\.venv\Scripts\python.exe -X utf8 scripts\reproduce_repaired.py
```

`run_revalidated.py`要求真实JUnit通过才允许生成正式结果，失败会保留QUARANTINED.json且停止。不要在未经重新核查时覆写已发布的Draft2图，生成器会先写新的时间戳草稿；重新发布前保留上一版。

| version | checked | changed | status |
| --- | --- | --- | --- |
| Legacy_Draft1 | 2918 | 0 | PASS |
| Root_archive_original | 26 | 0 | PASS |
| V16 | 1182 | 0 | PASS |
| Thesis_Research | 1207 | 0 | PASS |
| RootV2_model_files | 2 | 0 | PASS |
| V15 | 1160 | 0 | PASS |
| V14 | 887 | 0 | PASS |
| V13 | 158 | 0 | PASS |
| V12 | 6493 | 0 | PASS |
| V11 | 495 | 0 | PASS |


另有校验过的时间戳备份。由于旧Draft1原始资料层级过深，普通复制遭遇Windows路径上限；失败的部分副本保留但未声称完整。随后将所有2836个Latex_Images成员保存为ZIP，逐成员SHA验证，原始文件不改名/不移动。详见`evidence/DRAFT1_ARCHIVE_BACKUP.json`及`VERIFIED_BACKUP.json`。本轮只在修复目录及指定新Draft2图目录写入，未在原MDT/冻结目录运行更新脚本。

**Stop condition reached**：原缺陷已复现、隔离修复已实现、独立数值验证及受影响场景已重跑、限定MDT控制已对照、未解决工程假设已标注、Draft2素材完成。未开始论文、V17、经济重构或新优化。
