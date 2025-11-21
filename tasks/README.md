请注意，尚未实现

任务模板说明（供 `testback` 使用）

目的：

主要字段：

VirtualManager / testback 的预期实现要点：

任务模板与示例（供 `testback` / `VirtualManager` 使用）

概述
- 本 README 说明 `tasks/task_template.json` 的字段含义，并提供一个可直接运行的示例 `tasks/t1.json`。

快速要点
- `id`、`name`、`description`：任务标识与说明。
- `symbols`：回测标的列表（字符串数组，变长）。
- `data_source`：数据源配置，必须包含 `source`（如 `yfinance`、`akshare`、`csv`），可选 `interval`、`adjusted`。
- `date_range`：回测起止日期，`start` 和 `end`，ISO 日期字符串（YYYY-MM-DD）。
- `cash`：初始资金（数字）。
- `strategies`：策略数组，按顺序加载。每个策略为对象，至少包含 `name`、`path`（可 import 的模块路径）与 `params_list`（构造参数）。

示例文件
- 示例任务已保存为：`tasks/t1.json`。
- 内容示例（已写入仓库）：

```json
{
	"id": "t1",
	"name": "demo_ma_cross",
	"description": "简单均线交叉回测示例（演示用）",
	"symbols": ["AAPL", "MSFT"],
	"data_source": { "source": "yfinance", "interval": "1d", "adjusted": true },
	"date_range": { "start": "2020-01-01", "end": "2020-12-31" },
	"cash": 100000,
	"strategies": [ { "name": "ma_cross", "path": "strategy.ma", "params_list": { "short": 20, "long": 50, "order_size": 100 } } ]
}
```

如何被 `VirtualManager` / `testback` 使用（约定）
1. 加载任务：读取任务 JSON，验证基本字段（如 `id`, `symbols`, `data_source`, `date_range`）。
2. 拉取数据：将 `symbols`、`data_source` 和 `date_range` 传给 `Fetcher`（Fetcher 优先缓存，未命中时调用适配器）。
3. 装载策略：对 `strategies` 数组，按顺序 `import` 指定 `path` 模块并从中获得策略类（约定策略模块导出一个可实例化的类或工厂）。使用 `params_list` 构建实例。
4. 回测循环：按交易日（通常用历史日历）迭代：
	 - 构造当日前的历史窗口（history）并传入策略的 `decide(date, history)`。
	 - 聚合所有策略返回的 `next_action`（按 symbol 累加净买卖量）。
	 - 调用执行层（Execution/Broker）以约定的成交规则成交并更新持仓/现金/PNL。
	 - 保存每日快照。
5. 输出：将回测快照与报告保存到 `tasks` 中或 `output` 字段指定的位置（若存在）。

扩展建议
- 若需验证任务结果，建议在任务中添加 `assertions` 字段（例如期望的最低收益率、最大回撤阈值等）。
- 若需要批量执行多个任务，添加 `tasks/index.json` 列表或自动读取 `tasks/` 目录下的所有 `*.json`。

如果你希望我把模板修正为统一字段名（例如将 `path` 改回 `module`、`params_list` 改为 `params`，以及修复 `task_template.json` 中 `required` 的拼写错误 `desription` → `description`），我可以一并处理并更新示例文件以保持一致性。
