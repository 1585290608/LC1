# LC1 PR #1 Pre-Merge Review

2026-11-20 · **READY FOR HUMAN REVIEW** · Draft PR

审阅对象为 [PR #1](https://github.com/1585290608/LC1/pull/1)。最初核对的 PR head 为 `9e917302e4d0771aa066e2c6bdfef651a367f05d`，base 为 `main@228c005aa47bdee720524d152e56c10c5d4a7cd3`。CI 与审阅修订均在 `restructure/initial-draft-week7remake`。最终 head 和 CI 结果以 [PR Checks](https://github.com/1585290608/LC1/pull/1/checks) 为准。

| 检查 | 判定 | 证据与范围 |
| --- | --- | --- |
| 原 PR 540 个变更文件逐项审计 | **PASS** | 检查 Git blob 内容、路径、文件类型及来源。对 77 个 PNG 校验结构、CRC 和元数据。逐文件 SHA-256、来源分类和扫描标记保存在本地审阅记录。公开版 source map 的 366 个条目均与来源和发布字节匹配。 |
| 凭据、个人路径、私有 MDT/SQL 文件 | **PASS** | 修订后，凭据特征、个人邮箱模式、绝对机器路径和禁入文件类型的扫描均无命中。本次发布范围未发现原生 MBF/MOF、私有 SQL 数据库或专用安装文件。 |
| Stage 4 路径可移植性 | 首轮 **FAIL**，复核 **PASS** | 一个 Unix 绝对临时目录示例已替换为同用途相对路径，发布 source map 同步记录该文件的原始及发布哈希。 |
| 第三方资料和研究输出 | **PASS** | 文件审计未发现第三方论文全文、外部论文原图或供应商分发包。引用、DOI 和研究摘录有来源。审阅确认 76 个活动版本的已存生成结果和日志均有归档来源，没有提交缓存、临时备份或三份大型 EV trace。保留的 NASA POWER 气象数据为原有模拟输入。 [NASA POWER 引用说明](https://power.larc.nasa.gov/docs/referencing/) |
| 第三方权利的独立核验 | **INCONCLUSIVE** | 本轮按文件内容、出处和已公开来源审计。没有独立核实所有历史权利声明和归档中的出版许可。 |
| Initial Draft 冻结内容 | **PASS** | 158/158 个原文件与原 `main` 的 Git blob、模式和归档字节一致。此次审阅修订未改动 `Initial Draft/`。 |
| 原始研究档案 | **PASS** | 原始包 367/367，归档 Baseline 166/166，Stage 7 outputs 16/16，早期 Stage 8 278/278、D1 档案清单 46/46 的 SHA-256 均匹配。 |
| 独立回归与公开数据完整性 | **PASS** | 从干净 Git 导出分别运行，Initial Draft 53/53、Week7Remake 143/143。公开版 Baseline 142/142。3/3 EV traces 从固定输入生成并匹配原 SHA-256，再次执行时验签现有文件。 |
| GitHub Actions | **PASS** | 首次托管运行验证 head `c02c54707dd65ca5626cf4dc4f1d80abfb91eac7`。Initial Draft 53/53、Week7Remake 143/143、公开 Baseline 142/142、EV traces 3/3 均从托管作业日志确认。两项 job 各自在版本目录运行，只安装 Python 测试依赖。 [首轮 Actions 运行](https://github.com/1585290608/LC1/actions/runs/44758265965) |
| EV 说明 | **PASS** | 4 个 light utility、2 个 medium logistics 和 1 个 mobile emergency support archetype 的 **75/160/100 kWh** 分别标注为 **provisional simulation assumptions**。原始 fleet 参数保持原值。 [Week7Remake EV assumptions](Week7Remake/README.md#ev-assumptions) |
| D1 状态与验证声明 | **PASS** | D1 保留 **NO-GO / NOT RUN**，原生运行次数为 0。P2/W2 的 Event and Physical State 保持 **INCONCLUSIVE**。公开报告区分组件结果、重建时序和 Python 结果。完整 hybrid MDT/HOMER、现场故障概率和 probability-weighted EENS 仍缺少验证证据。 [Stage 8 证据](Week7Remake/week8/README.md) |
| Merge 控制 | **PASS** | PR 保持 Draft，`main` 未更新，auto-merge 未启用。 |

逐文件工作记录、机器路径相关本地日志和归档回读保存在 Git 忽略的 `local-only/pre-merge-review/`。人审批准并手动合并后，再将本地工作树同步到最新 `main`，在独立 feature branches 上继续开发。
