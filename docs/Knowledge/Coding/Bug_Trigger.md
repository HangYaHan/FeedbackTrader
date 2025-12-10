# Bug: 旧版全局触发器串扰与重复触发

## 背景
- 模块：`src/strategy/support.py` 早期版本。
- 设计：全局列表 `_TRIGGERS` / `_ON_BAR` 存放所有触发器，`always/on_bar` 向全局追加，`run_triggers` 遍历全局。
- 问题：触发器生命周期与策略实例/回测运行不绑定，导致跨策略串扰、重复触发、逻辑/内存泄漏。

## 复现示例
1) 运行回测 A（SMA 策略）→ 全局追加 SMA 买/卖 2 条触发器。
2) 同进程运行回测 B（MACD 策略）→ 全局再追加 MACD 买/卖 2 条触发器。
3) 再运行回测 A → `run_triggers` 遍历 4 条触发器：
	 - MACD 触发器在 SMA 回测里被执行，可能因缺少上下文报错或误下单（跨策略串扰）。
	 - 若多次运行同一回测，SMA 触发器会被重复追加，满足条件时会执行多次，订单量翻倍（重复触发）。
	 - 全局列表持续增长，无法随策略结束而清理（逻辑/内存泄漏）。

## 修复方案（已实施）
- 引入 `TriggerSet`（`support.py`）：每个策略实例持有自己的触发器集合，`always/on_bar/run` 作用域限于实例。
- 保留兼容接口：全局 `always/on_bar/run_triggers` 仍存在，但内部委托给单例 `_GLOBAL_SET`，新策略应使用实例级 `TriggerSet`。
- 策略调整：`SMAStrategy` 改用实例级触发器；新增 `MACDStrategy` 亦采用 `TriggerSet`。

## 调用链（现实现）
- `backtest.engine.run_task` → `load_task`/`load_strategy` → `data.fetcher.get_history` → `portfolio.run_backtest`
- 每个交易日：
	1) 策略 `decide` 计算指标，调用自身的 `TriggerSet.run(ctx)`；
	2) 返回订单字典；
	3) `PortfolioManager.apply_orders` 更新现金/持仓；
	4) 记录净值，推进下一日。

## 结论
- 旧版全局触发器设计导致跨策略串扰与重复触发，属于逻辑缺陷。
- 通过引入实例级 `TriggerSet` 绑定触发器生命周期，避免共享全局状态，修复串扰与重复触发问题。
