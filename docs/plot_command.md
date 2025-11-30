# Plot 命令使用说明

`plot` 命令用于基于已经缓存的数据（parquet / csv 回退）绘制标的的 K 线图。

## 基本语法

```
plot SYMBOL [--start YYYYMMDD] [--end YYYYMMDD]
     [--frame daily|weekly] [--source akshare|yfinance|csv]
     [--refresh] [--output path.png]
```

- SYMBOL: 标的代码，例如 `sh600000`, `AAPL`
- --start / --end: 起止日期（可用 `YYYYMMDD` 或 `YYYY-MM-DD`），用于筛选缓存/抓取的数据。
- --frame: 时间框架，`daily` 默认，`weekly` 会按周聚合产生周K。
- --source: 数据源名称（决定在刷新或缓存未命中时使用哪个 adapter）。
- --refresh: 强制重新抓取并覆盖缓存。
- --output: 将图像保存为指定文件而不是弹出窗口显示。

## 示例

1. 绘制浦发银行日K（使用缓存优先，akshare 数据源）
```
plot sh600000 --start 20240101 --end 20241130 --source akshare
```

2. 绘制苹果周K并保存为图片：
```
plot AAPL --start 2024-01-01 --frame weekly --output aapl_weekly.png
```

3. 强制刷新后再绘制：
```
plot sh600000 --refresh
```

## 工作流程概述
1. CLI 解析参数并调用 `fetcher.get_history(...)`。
2. 若有缓存且未指定 `--refresh`，直接读取本地 parquet/csv；否则从指定数据源抓取并写入缓存。
3. 将得到的 DataFrame 交给 `src/ploter/ploter.py` 中的 `plot_kline()`。
4. `plot_kline()` 标准化列名并根据 `--frame` 做聚合（周K使用 `resample('W')`）。
5. 使用 matplotlib 绘制蜡烛图并可选保存文件。

## 数据列要求
需要至少包含可以映射到以下列的字段：`Open, High, Low, Close` （大小写或中文别名可自动识别：开盘/最高/最低/收盘）。存在 `Volume` 列时会显示半透明成交量柱状图。

## 常见问题
- 提示缺少列：检查 adapter 返回的列名是否为标准或中文；若不是请在 adapter 中做列名转换。
- 没有数据：确认缓存是否存在或日期范围是否正确；必要时加 `--refresh`。
- 生成的图片过少：可能是筛选日期后剩余行数不足。

## 后续扩展建议
- 增加 `--style` 选项（dark / light）。
- 支持多标的对比（副图或叠加）。
- 增加指标叠加（MA5/MA20 等）。
- 输出交互式 HTML（plotly / bokeh）。

---
如果需要加入指标或多图布局，可继续提出需求，我可以帮你扩展。
