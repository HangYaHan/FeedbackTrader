from __future__ import annotations

import pandas as pd
from typing import Dict

from src.strategy.calc_lines import CLOSE, MA
from src.strategy.support import crossabove, crossbelow


class SMAStrategy:
    """
    Simple MA crossover strategy.

    Parameters
    ----------
    symbol : str
        Target trading symbol.
    short_window : int
        Short moving average window.
    long_window : int
        Long moving average window.
    qty : int
        Trade size (shares) per signal.
    """

    def __init__(self, symbol: str, short_window: int = 5, long_window: int = 20, qty: int = 100) -> None:
        self.symbol = symbol
        self.short_window = short_window
        self.long_window = long_window
        self.qty = qty

    def decide(self, date: pd.Timestamp, history: pd.DataFrame) -> Dict[str, int]:
        """
        Generate actions for the given date using past history (excluding current date).

        Returns
        -------
        Dict[str, int]
            symbol -> quantity (positive buy, negative sell). Empty dict if no signal.
        """
        if history.empty:
            return {}

        # accept either symbol-named column (multi-asset) or single-symbol OHLC with Close
        if self.symbol in history.columns:
            price = CLOSE(history[[self.symbol]].rename(columns={self.symbol: "close"}))
        elif 'Close' in history.columns:
            price = history['Close']
        elif 'close' in history.columns:
            price = history['close']
        else:
            return {}
        sma_short = MA(price, self.short_window)
        sma_long = MA(price, self.long_window)

        buy_cross = crossabove(sma_short, sma_long)
        sell_cross = crossbelow(sma_short, sma_long)

        signals = {}
        if not buy_cross.empty and bool(buy_cross.iloc[-1]):
            signals[self.symbol] = self.qty
        elif not sell_cross.empty and bool(sell_cross.iloc[-1]):
            signals[self.symbol] = -self.qty

        return signals