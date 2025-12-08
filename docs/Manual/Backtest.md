# backtest

Source: `src/backtest/engine.py`

## Functions
- `load_task(task_name: str) -> dict`: Load task JSON (`tasks/{task_name}.json`) and return parsed dict.
- `load_strategy(module_path: str, class_name: str, params: dict) -> Any`: Dynamically import module and instantiate strategy class with params.
- `run_task(task_name: str) -> pandas.DataFrame`: High-level runner that loads a task, fetches data via `data.fetcher.get_history`, loads strategy via `load_strategy`, and passes to `portfolio.manager.run_backtest`. Returns equity curve DataFrame.

## Notes
- Expects task JSON fields like `symbol`, `start`, `end`, `strategy` block, optional `source`, `commission`, `slippage`, `initial_cash`.
- Errors propagate to caller; CLI catches and prints them.
