Python 接口设计（结合本项目实践）

目的：让调用方清楚能用什么、怎么用；内部可自由演进且易排障。

命名与可见性
- 公共 API 无下划线；内部实现单下划线；双下划线只在需避免子类覆盖时使用。

分层与导入
- 跨包用绝对导入；同包用相对导入；入口用 `python -m src.main` / `-m src.system.CLI`。
- 示例：`src/system/CLI.py` 内部 `from .log import get_logger`，跨包 `from src.backtest.engine import run_task`。

契约示例（项目内）
- 策略基类 `src/strategy/base.py` 规定生命周期：`on_start/on_bar/on_tick/on_stop/generate_signals`。
- 具体策略 `MovingAverage`：`on_bar` 接收含 close 的 bar；`generate_signals` 返回 `{ "signal": ..., "size": ... }`。
- 回测入口 `src/backtest/engine.run_task(name)`：读取 `tasks/*.json`，加载策略、取数、回测，返回 `equity_curve`（CLI 打印最终权益）。
- 绘图入口 `run_plot_command(args)`: 解析 CLI 参数，检查 OHLC 列，支持 MA/EMA/BOLL/RSI/MACD/ATR，`-output` 可保存图。

健壮性
- 早做输入校验：缺列/必需参数直接报错。
- 记录关键日志：数据加载、回测开始/结束、指标失败；CLI 捕获异常给用户友好提示。
- 避免 `from module import *`，减少命名冲突。

演进与兼容
- 公共接口保持兼容，新增功能优先加新参数并设默认；内部（单下划线）可重构。

写作模板（最小）
- 模块：开头写用途、暴露的主函数。
- 类：docstring 说明职责/参数/返回；公共方法写明契约；内部方法加 `_`。
- 函数：说明参数、默认、返回、可能的异常，给一个最小调用示例。

