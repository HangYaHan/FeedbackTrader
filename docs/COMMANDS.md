    help, h, ?       Show this help
    config, cfg      Show or set configuration
    backtest, bt     Run a backtest
    plot             Plot cached OHLC data
    exit, quit, q    Exit the CLI

# help 命令使用说明

`help` 命令用于显示所有可用命令的简要说明。

# config 命令使用说明

`config` 命令用于查看或设置系统配置参数。

# backtest 命令使用说明

# plot 命令使用说明

`plot` 命令用于基于已经缓存的数据（parquet / csv 回退）绘制标的的 K 线图。

## 基本语法

```
plot SYMBOL [--start YYYYMMDD] [--end YYYYMMDD]
     [--frame daily|weekly] [--source akshare|yfinance|csv]
     [--refresh] [--output path.png]
```

## 参数说明
- SYMBOL: 标的代码，例如 `sh600000`, `AAPL`
- --start / --end: 起止日期（可用 `YYYYMMDD` 或 `YYYY-MM-DD`），用于筛选缓存/抓取的数据。
- --frame: 时间框架，`daily` 默认，`weekly` 会按周聚合产生周K。
- --source: 数据源名称（决定在刷新或缓存未命中时使用哪个 adapter）。
- --refresh: 强制重新抓取并覆盖缓存。
- --output: 将图像保存为指定文件而不是弹出窗口显示。

## 默认值：
- --frame: daily
- --source: akshare
- --start: 无限制（从最早日期开始）
- --end: 无限制（到最新日期结束）
- --refresh: False
- --output: None

## 示例

1. 绘制浦发银行日K（使用缓存优先，akshare 数据源）
```
plot sh600000 --start 20240101 --end 20241130 --source akshare
```

2. 绘制贵州茅台周K，并保存为图片
```
plot sh600519 --frame weekly --output maotai_weekly.png
```

3. 绘制贵州茅台日K，添加多种技术指标
```
plot sh600519 -start 2024-01-01 -ma 5,20 -ema 12,26 -boll 20,2 -rsi 14 -macd 12,26,9 -atr 14
```