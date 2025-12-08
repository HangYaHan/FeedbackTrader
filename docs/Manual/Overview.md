# Package Overview

This folder documents the public interfaces of the `src` package by submodule. Each manual lists callable entry points (functions, classes, methods) with brief descriptions to guide reuse and extension.

## Subpackages
- `backtest`: task loader, strategy loader, and orchestrated backtest runner.
- `common`: shared utilities for config, filesystem helpers, and parsing helpers.
- `data`: fetchers, adapters, storage cache helpers, and data-specific exceptions.
- `execution`: broker interface abstraction.
- `ploter`: OHLC plotting and indicator overlays with CLI argument parser.
- `portfolio`: portfolio state and backtest runner that applies strategy orders.
- `risk`: risk manager stub for order checks and exposure.
- `strategy`: indicator helpers, trigger DSL, and sample SMA crossover strategy.
- `system`: logging, JSON helpers, CLI entry point, and (placeholder) GUI main window.

## Entry Points
- CLI: run `python -m src.system.CLI` for the interactive loop; `backtest` command delegates to `src.backtest.engine.run_task`, `plot` to `src.ploter.ploter.run_plot_command`.
- Programmatic backtest: call `src.backtest.engine.run_task(task_name)` to load a task JSON and run.
- Plotting: use `src.ploter.ploter.plot_kline(df, symbol, ...)` for direct plotting or `run_plot_command(args)` for CLI-style parsing.
- Data access: call `src.data.fetcher.get_history(symbol, start, end, source, ...)` for cached historical data.
- JSON helpers: `src.system.json.read_json` / `write_json` / `safe_loads` / `safe_dumps` for config or task IO.
