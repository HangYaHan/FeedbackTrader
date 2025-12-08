# ploter

Source: `src/ploter/ploter.py`

## Functions
- `plot_kline(df: pandas.DataFrame, symbol: str, frame: str = 'daily', output: str | None = None, ma: list[int] | None = None, ema: list[int] | None = None, boll: tuple[int, float] | None = None, rsi: list[int] | None = None, macd: tuple[int, int, int] | None = None, atr: int | None = None) -> None`: Plot candlesticks with overlays and optional indicator sub-panels; saves to file if `output` is provided else shows interactive window.
- `run_plot_command(args: list[str]) -> None`: Parse CLI-style args (`plot SYMBOL [-start ...] [-end ...] [-frame daily|weekly] [-source ...] [-refresh] [-output file.png] [-ma ...] [-ema ...] [-boll win,k] [-rsi win] [-macd f,s,signal] [-atr win]`) and delegate to `data.fetcher.get_history` then `plot_kline`.

## Behaviors
- Normalizes column names to `Open/High/Low/Close/Volume`; errors if OHLC missing.
- Resamples to weekly when `frame='weekly'` and index is datetime-like.
- Indicators supported: MA, EMA, Bollinger Bands, RSI, MACD, ATR; volume overlay when available.
