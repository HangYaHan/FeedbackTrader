# strategy

Sources: `src/strategy/calc_lines.py`, `src/strategy/support.py`, `src/strategy/yahan_strategies.py`

## calc_lines (indicator helpers)
- `CLOSE/OPEN/HIGH/LOW/VOLUME(df: pandas.DataFrame) -> pandas.Series`: Pick column by common names (case-insensitive), else `KeyError`.
- `LAG(series: SeriesLike, n: int = 1) -> SeriesLike`: Shift by `n`.
- `DIFF(series: SeriesLike, n: int = 1) -> SeriesLike`: Difference over `n`.
- `ROLLING_MAX/MIN(series: SeriesLike, window: int) -> SeriesLike`: Rolling extrema with `min_periods=1`.
- `STD(series, window)`, `ZSCORE(series, window)`: Rolling std and z-score.
- `MA(series, window)`, `EMA(series, window)`: Moving averages.
- `RSI(series, window: int = 14) -> SeriesLike`: RSI using EMA of gains/losses.
- `MACD(series, fast: int = 12, slow: int = 26, signal: int = 9) -> pandas.DataFrame`: Columns `macd`, `signal`, `hist`.
- `BOLL(series, window: int = 20, k: float = 2.0) -> pandas.DataFrame`: Columns `mid`, `upper`, `lower`.
- `ATR(high, low, close, window: int = 14) -> SeriesLike`: Average true range.
- `RESAMPLE_OHLC(df, rule: str) -> pandas.DataFrame`: Resample OHLC(+Volume) DataFrame by rule, requires DatetimeIndex.
- `RESAMPLE(series, rule: str, how: str = 'last'|'first'|'mean') -> SeriesLike`: Resample Series by rule.

## support (trigger DSL helpers)
- `class Trigger(condition, action, name: str | None = None)`: Evaluates condition, fires action on rising edge.
  - `evaluate(context) -> None`: Execute condition/action with error wrapping.
- `always(condition, action, name=None) -> Trigger`: Register trigger in global list.
- `on_bar(action) -> action`: Register per-bar callback.
- `run_triggers(context) -> None`: Run all on-bar actions then triggers.
- `assign(value) -> Any`: Identity helper.
- `assert_stmt(condition: bool, message: str = 'assertion failed') -> None`: Raise `AssertionError` if false.
- `crossabove(a: pandas.Series, b: pandas.Series) -> pandas.Series`: True when `a` crosses above `b` at current bar.
- `crossbelow(a: pandas.Series, b: pandas.Series) -> pandas.Series`: True when `a` crosses below `b` at current bar.

## yahan_strategies (examples)
- `class SMAStrategy`:
  - `__init__(self, symbol: str, short_window: int = 5, long_window: int = 20, qty: int = 100)`: Configure target symbol and windows.
  - `decide(self, date: pandas.Timestamp, history: pandas.DataFrame) -> dict[str, int]`: Compute MA crossover signals using `MA` and `crossabove/crossbelow`; returns order dict of symbol -> qty (positive buy, negative sell) or empty when no signal.
