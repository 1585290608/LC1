# LC1 本地管理与 GitHub 说明

[English maintenance guide](workspace-guide.md)

- **models/core/** 存放共享设备模型和能量核算。
- **models/islanded/** 存放停电调度、燃油曲线和故障逻辑。
- **models/grid_connected/** 存放并网调度和经济计算。
- **data/** 统一存放输入。各研究报告及结果仍按用途放在 **validation/**，已有图表放在 **Image/**。
- [编号索引](scenario-index.md)连接 S、P、C 的描述性名称和历史编号。历史版本的本机入口放在 `local-only/historical-evidence-locations.md`，由 Git 忽略。

`source-map.csv` 同时记录原始与整理后文件的 SHA-256。多个原始副本可以指向同一
文件。`byte_identical` 是原字节复制，`layout_adapted` 是整理后适配的代码或测试路径。
原始归档的内部路径和版本保留在各报告里。

管理新场景时，沿用一个入口并给案例起描述性名称，记录原编号、输入版本和参数。
运行时储备下限与停电起始 SOC 分别记录。现有场景工厂和条件分支沿用归档研究定义。
图表和报告涉及新假设时，随改动保留对应证据和运行设置。

从仓库根目录运行 `python -m pytest -q`。原始逐时轨迹和财务现金流可按
[归档复放指南](../validation/archive-replay.md)核查。准备上传时先查看 `git status --short`，
核对课程发布要求及代码、数据和图表的共享范围。仓库尚未配置开源许可。
