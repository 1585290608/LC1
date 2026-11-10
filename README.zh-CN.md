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

在项目根目录使用 Python 3.12 运行测试。

```powershell
python -m pip install -r requirements-test.txt
python -m pytest -q
```

[中文管理说明](docs/workspace-guide-zh.md) · [场景与历史编号索引](docs/scenario-index.md) ·
[历史工程证据中文索引](validation/historical-engineering-evidence/README.zh-CN.md)

研究涵盖模拟能量核算、负荷供电和条件性经济分析。原生 MDT 验证、设备性能和并网外送的适用范围见相应研究报告。
