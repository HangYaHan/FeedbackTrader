# help 命令
显示所有可用命令的简要说明（与 CLI 内置 `help` 一致）。

# config 命令
预留，用于查看或设置系统配置参数（当前未实现）。

# backtest 命令
基于 `tasks/` 目录下的任务 JSON 运行回测。任务文件需包含 strategy/portfolio/data 三段配置（见 `tasks/task_example.json` && `tasks/task_template.json`）。

## 基本语法
```
backtest TASK_NAME
```
说明：`TASK_NAME` 不包含 `.json` 后缀，程序会从 `tasks/TASK_NAME.json` 读取。

## 执行流程（与代码一致）
- 读取任务：`tasks/<name>.json`
- 加载策略类：`strategy.module` + `strategy.class` + `strategy.params`
- 抓取/加载历史数据：`data.symbol`、`data.start/end`、`data.source`、`data.interval`、`data.cache/refresh`
- 运行回测：`portfolio` 中的 `cash`、`commission`、`slippage`
- 输出：打印最终权益，返回 equity_curve

## 示例
```
backtest task_example
```
这会读取 `tasks/task_example.json`，按其中的策略与参数执行回测。

# plot 命令
基于已缓存的数据（parquet / csv 回退）绘制标的 K 线，并可选叠加常见技术指标。

## 基本语法
```
plot SYMBOL [-start YYYYMMDD] [-end YYYYMMDD]
     [-frame daily|weekly] [-source akshare|yfinance|csv]
     [-refresh] [-output path.png]
     [-ma 5,20] [-ema 12,26] [-boll 20,2]
     [-rsi 14] [-macd 12,26,9] [-atr 14]
```

## 参数说明
- SYMBOL: 标的代码，例如 `sh600000`, `AAPL`
- -start / -end: 起止日期（`YYYYMMDD` 或 `YYYY-MM-DD`）
- -frame: `daily` (默认) 或 `weekly`（内部按周重采样聚合）
- -source: 数据源 `akshare` (默认) | `yfinance` | `csv`
- -refresh: 强制重新抓取并覆盖缓存
- -output: 保存为文件而非弹窗（例：`chart.png`）
- -ma: 逗号分隔的均线周期列表（例：`5,20`）
- -ema: 逗号分隔的指数均线周期列表
- -boll: 形如 `window,k`（例：`20,2`）
- -rsi: 逗号分隔的 RSI 周期列表
- -macd: 形如 `fast,slow,signal`（例：`12,26,9`）
- -atr: ATR 周期（整数）

## 默认值
- frame: daily
- source: akshare
- start/end: 不限制（用全量缓存）
- refresh: False
- output: None（弹窗显示）
- 指标：不叠加（需显式传入）

## 示例
1) 日线，使用缓存优先
```
plot sh600000 -start 20240101 -end 20241130 -source akshare
```

2) 周线并保存图片
```
plot sh600519 -frame weekly -output maotai_weekly.png
```

3) 日线叠加多指标
```
plot sh600519 -start 2024-01-01 -ma 5,20 -ema 12,26 -boll 20,2 -rsi 14 -macd 12,26,9 -atr 14
```

# exit 命令
退出交互式命令行界面。