# LINES 函数说明与摘要

本文档概述 `src/strategy/calc_lines.py` 中的时间序列/指标函数，说明其常用金融含义、计算方法与典型使用场景。

## 基础列访问

- `CLOSE(df)`: 取收盘价列（候选名：close/adj close/adj_close/price）。
- `OPEN(df)`: 取开盘价列。
- `HIGH(df)`: 取最高价列。
- `LOW(df)`: 取最低价列。
- `VOLUME(df)`: 取成交量列（候选名：volume/vol）。

## 序列变换与滚动统计

- `LAG(series, n=1)`: 序列后移 *n* 期（用于前一日/前一根值）。  
  公式：`lag_t = series_{t-n}`
- `DIFF(series, n=1)`: 与 *n* 期前的差分，常用于动量/涨跌额。  
  公式：`diff_t = series_t - series_{t-n}`
- `ROLLING_MAX(series, window)`: 滚动窗口内最大值（如近 N 日高点）。
- `ROLLING_MIN(series, window)`: 滚动窗口内最小值（如近 N 日低点）。
- `STD(series, window)`: 滚动标准差（波动度衡量）。
- `ZSCORE(series, window)`: 滚动标准分数，衡量当前值相对窗口均值的偏离。  
  公式：`z_t = (x_t - mean_window) / std_window` （std 为 0 时返回 NaN）

## 均线与经典指标

- `MA(series, window)`: 简单移动平均（SMA），等权平均。  
  公式：`MA_t = (x_t + ... + x_{t-window+1}) / window`
- `EMA(series, window)`: 指数移动平均，近期数据权重更高。  
  递推：`EMA_t = α*x_t + (1-α)*EMA_{t-1}`, 其中 `α = 2/(window+1)`.
- `RSI(series, window=14)`: 相对强弱指标，比较窗口内上涨/下跌的平均幅度。  
  简化计算：  
  - `delta = diff(series)`  
  - `gain = EWM(mean of positive delta)`  
  - `loss = EWM(mean of negative delta)`  
  - `RS = gain / loss`  
  - `RSI = 100 - 100/(1+RS)`
- `MACD(series, fast=12, slow=26, signal=9)`: 快慢 EMA 之差的趋势/动量指标。  
  - `MACD_line = EMA_fast - EMA_slow`  
  - `Signal = EMA(MACD_line, signal)`  
  - `Hist = MACD_line - Signal`
- `BOLL(series, window=20, k=2.0)`: 布林带，基于均值与标准差的通道。  
  - `Mid = MA(series, window)`  
  - `Upper = Mid + k*STD`  
  - `Lower = Mid - k*STD`
- `ATR(high, low, close, window=14)`: 平均真实波幅，衡量波动。  
  - `TR_t = max(high-low, |high-prev_close|, |low-prev_close|)`  
  - `ATR = rolling_mean(TR, window)`

## 重采样

- `RESAMPLE_OHLC(df, rule)`: 按时间规则重采样 OHLC(V)。  
  - Open: first, High: max, Low: min, Close: last, Volume: sum（若有）。
  - 适用于将日线转周线/月线，或 1m 转 5m 等。索引需为 `DatetimeIndex`。
- `RESAMPLE(series, rule, how="last")`: 对任意 Series 按时间重采样，聚合方式支持 last/first/mean。

## 函数摘要（速览）

| 函数                         | 作用           | 备注             |
| ---------------------------- | -------------- | ---------------- |
| `CLOSE/OPEN/HIGH/LOW/VOLUME` | 提取常用行情列 | 自动匹配列名     |
| `LAG`                        | 序列后移       | 前值引用         |
| `DIFF`                       | 差分           | 涨跌/动量        |
| `ROLLING_MAX/MIN`            | 窗口高低       | 近 N 日高低      |
| `STD`                        | 滚动标准差     | 波动度           |
| `ZSCORE`                     | 滚动标准分     | 偏离度量         |
| `MA/EMA`                     | 移动平均       | 趋势平滑         |
| `RSI`                        | 强弱指标       | 0-100 振荡       |
| `MACD`                       | 趋势动量       | macd/signal/hist |
| `BOLL`                       | 布林带         | 均值±k*std       |
| `ATR`                        | 平均真实波幅   | 波动指标         |
| `RESAMPLE_OHLC`              | K 线重采样     | OHLC(V) 聚合     |
| `RESAMPLE`                   | 序列重采样     | last/first/mean  |

## 使用提示

- 所有函数基于 pandas；重采样需 `DatetimeIndex`。
- 滚动函数默认 `min_periods=1`，起始段不全 NaN。
- `BOLL` 的 `k` 可调；`MACD`/`RSI` 参数可按品种/周期调整。