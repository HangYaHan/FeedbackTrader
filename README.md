# Beruto — 贝如塔

## 项目描述

这是一个“自己玩”的量化交易模型系统，目前仍处于非常早期的阶段，现在破破烂烂连地基都没有。我会随着开发进展，逐步将已实现的部分更新到项目描述中。当前正在搭建基础的回测系统。

## 名字来源

这个项目的灵感与命名，很大程度上来源于2025年11月初爆火的《人____南》。名称中的“贝如塔”取自阿尔法（Alpha）之后的贝塔（Beta）。我那位博学的同学（dendrobium，现已成为项目贡献者之一）联想到了中文互联网中的“贝如塔”梗，于是这个名字便应运而生。这个梗原本有两种含义：一是“贝塔”的衍生创作，二是“A如B”的表达方式。而 dendrobium 的巧妙构思，为它赋予了第三层意义：阿尔法之后的贝塔，可谓一语三关。

这便是项目名称的由来。

## 快速开始

- 详见 [docs/Quickstart.md](docs/Quickstart.md)。

## 目录速览
- `README.md`：项目说明与起步指南。
- `CONTRIBUTING.md`：协作规范。
- `requirements.txt`：依赖列表。
- `tasks/`：任务模板与示例（驱动回测）。
- `data/`：行情缓存与样例数据（parquet/csv）。
- `docs/`：设计/接口/知识文档，含 `Manual/` 子模块手册。
- `src/`：核心代码：
  - `backtest/engine.py`：任务加载、策略动态加载、回测调度。
  - `data/`：`fetcher` 统一入口，`storage` 缓存，`adapters/` (akshare/yfinance/csv)，`exceptions` 分类错误。
  - `portfolio/manager.py`：组合状态、下单应用、资金曲线生成。
  - `strategy/`：`calc_lines` 指标、`support` 触发器 DSL、`yahan_strategies` 示例策略。
  - `ploter/ploter.py`：K 线与指标绘图，CLI 参数解析。
  - `system/`：`CLI` 交互入口、`json` 读写、`log` 配置（`main_window` 为占位）。
  - `execution/broker.py`、`risk/risk_manager.py`、`common/config.py`、`common/utils.py`：接口/占位，等待完善。
- `tests/`：单元/集成测试脚本（待补充覆盖）。

## 贡献与规则

欢迎任何形式的贡献！请参阅 `CONTRIBUTING.md` 了解协作规范。主要规则包括：

- 文档命名：全小写为草稿，首字母大写为正式文档，需持续更新。
- 分支：保持 `main` 干净，开发/调试请新建分支。
- 源码：`src` 目录保持无中文。
- PR：附主要函数摘要（参数、返回值、功能）的 Markdown 描述。
- 问题与想法：请提交 GitHub Issues。

## 加入我们

估计没什么人会注意到这个还在起步阶段的小项目，但如果你碰巧感兴趣，非常欢迎提交 PR，也欢迎加入群聊一起交流（吹水）。
QQ 群号是：陆 陆 陆 壹 叁 壹 捌 陆 零
