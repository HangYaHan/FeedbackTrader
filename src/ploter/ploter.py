"""Unified plotting interface for candlestick charts.

Functions:
	- plot_kline(df, symbol, frame, output, ma)
	- run_plot_command(args): parse CLI args and dispatch plotting

The module normalizes column names to Open/High/Low/Close/Volume when possible.
"""

from __future__ import annotations

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.dates import DateFormatter
from src.system.log import get_logger

logger = get_logger(__name__)

_COL_MAP = {
	'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume',
	# Common alternative names
	'adj close': 'Close', 'close_adj': 'Close', 'price': 'Close'
}

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
	rename_map = {}
	for c in df.columns:
		key = c.lower()
		if key in _COL_MAP:
			rename_map[c] = _COL_MAP[key]
		elif c in _COL_MAP:
			rename_map[c] = _COL_MAP[c]
	if rename_map:
		df = df.rename(columns=rename_map)
	return df

def _resample(df: pd.DataFrame, frame: str) -> pd.DataFrame:
	if frame == 'weekly':
		if not isinstance(df.index, pd.DatetimeIndex):
			try:
				df.index = pd.to_datetime(df.index)
			except Exception:
				return df  # give up resampling if cannot parse
		agg = {
			'Open': 'first',
			'High': 'max',
			'Low': 'min',
			'Close': 'last',
		}
		if 'Volume' in df.columns:
			agg['Volume'] = 'sum'
		dfw = df.resample('W').agg(agg).dropna(how='any')
		return dfw
	return df

def plot_kline(df: pd.DataFrame, symbol: str, frame: str = 'daily', output: str | None = None, ma: list[int] | None = None) -> None:
	if df is None or df.empty:
		raise ValueError('Empty DataFrame provided to plot_kline')
	df = _normalize_columns(df)
	needed = {'Open','High','Low','Close'}
	missing = needed - set(df.columns)
	if missing:
		raise ValueError(f'Missing columns for candlestick plotting: {missing}')

	df = df.sort_index()
	df = _resample(df, frame)

	# Prepare figure
	fig, ax = plt.subplots(figsize=(10,6))
	ax.set_title(f'{symbol} {frame} Candlesticks ({len(df)} bars)')
	ax.set_xlabel('Date')
	ax.set_ylabel('Price')

	if not isinstance(df.index, pd.DatetimeIndex):
		try:
			df.index = pd.to_datetime(df.index)
		except Exception as e:
			logger.warning('Failed to convert index to datetime: %s', e)

	dates = df.index.to_pydatetime()

	# width of each candle (days). For weekly change, widen a bit.
	width = 0.6 if frame != 'weekly' else 3.2

	for i, (ts, row) in enumerate(df.iterrows()):
		o = float(row['Open']); h = float(row['High']); l = float(row['Low']); c = float(row['Close'])
		color = 'red' if c >= o else 'green'
		# wick
		ax.vlines(ts, l, h, color=color, linewidth=1)
		# body
		body_low = min(o, c)
		body_height = abs(c - o)
		if body_height == 0:
			# draw a very thin line to represent no change
			ax.hlines(o, ts, ts, color=color, linewidth=2)
		else:
			rect = Rectangle((ts, body_low), pd.Timedelta(days=width), body_height, facecolor=color, edgecolor=color, linewidth=0.5)
			ax.add_patch(rect)

	ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
	fig.autofmt_xdate()

	if 'Volume' in df.columns:
		ax2 = ax.twinx()
		ax2.set_ylabel('Volume')
		try:
			ax2.bar(dates, df['Volume'].values, alpha=0.15, color='gray')
		except Exception:
			pass

	# Moving averages
	if ma:
		for w in ma:
			try:
				series = df['Close'].rolling(window=w).mean()
				ax.plot(dates, series.values, linewidth=1.2, label=f'MA{w}')
			except Exception:
				logger.warning('Failed to compute MA%s', w)
		ax.legend(loc='upper left')

	if output:
		try:
			fig.savefig(output, dpi=120, bbox_inches='tight')
			logger.info('Saved plot to %s', output)
		except Exception as e:
			logger.exception('Failed saving plot: %s', e)
			raise
	else:
		plt.show()

	plt.close(fig)

def run_plot_command(args: list[str]) -> None:
	"""Parse CLI args and execute plotting.

	Supported:
	  plot SYMBOL [-start YYYYMMDD] [-end YYYYMMDD]
		   [-frame daily|weekly] [-source akshare|yfinance|csv]
		   [-refresh] [-output file.png] [-ma 5,20]
	"""
	from src.data import fetcher as data_fetcher

	if not args:
		print("Usage: plot SYMBOL [-start YYYYMMDD] [-end YYYYMMDD] [-frame daily|weekly] [-source akshare|yfinance|csv] [-refresh] [-output file.png] [-ma 5,20]")
		return

	symbol = args[0]
	start = None
	end = None
	frame = 'daily'
	source = 'akshare'
	refresh = False
	output = None
	ma_list: list[int] | None = None

	i = 1
	while i < len(args):
		tok = args[i]
		if tok == '-start' and i + 1 < len(args):
			start = args[i+1]; i += 2; continue
		if tok == '-end' and i + 1 < len(args):
			end = args[i+1]; i += 2; continue
		if tok == '-frame' and i + 1 < len(args):
			frame = args[i+1].lower(); i += 2; continue
		if tok == '-source' and i + 1 < len(args):
			source = args[i+1].lower(); i += 2; continue
		if tok == '-output' and i + 1 < len(args):
			output = args[i+1]; i += 2; continue
		if tok == '-refresh':
			refresh = True; i += 1; continue
		if tok == '-ma' and i + 1 < len(args):
			raw = args[i+1]
			try:
				ma_list = [int(x.strip()) for x in raw.split(',') if x.strip()]
			except Exception:
				print(f"Invalid -ma value: {raw}")
			i += 2; continue
		print(f"Unknown arg: {tok}")
		i += 1

	try:
		df = data_fetcher.get_history(symbol, start, end, source=source, interval='1d', cache=True, refresh=refresh)
	except Exception as e:
		logger.exception("Failed to fetch data for plot: %s", e)
		print(f"Failed to fetch data: {e}")
		return

	if df is None or df.empty:
		print(f"No data to plot for {symbol}.")
		return

	try:
		plot_kline(df, symbol=symbol, frame=frame, output=output, ma=ma_list)
		print(f"Plotted {symbol} ({frame}) rows={len(df)}" + (f" -> {output}" if output else ""))
	except Exception as e:
		logger.exception("Plotting failed for %s: %s", symbol, e)
		print(f"Plot failed: {e}")


__all__ = ['plot_kline', 'run_plot_command']