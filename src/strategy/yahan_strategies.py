from __future__ import annotations

import pandas as pd
from typing import Dict

from src.strategy.calc_lines import CLOSE, MA, MACD
from src.strategy.support import TriggerSet, crossabove, crossbelow


class SMAStrategy:
    """
    Simple MA crossover strategy using TriggerSet to avoid global state.
    """

    def __init__(self, symbol: str, short_window: int = 5, long_window: int = 20, qty: int = 100) -> None:
        self.symbol = symbol
        self.short_window = short_window
        self.long_window = long_window
        self.qty = qty
        self._orders: Dict[str, int] = {}
        self._triggers = TriggerSet()

        # Register triggers: buy on short crossing above long; sell on short crossing below long.
        self._triggers.always(
            lambda ctx: bool(crossabove(ctx["sma_short"], ctx["sma_long"]).iloc[-1]),
            lambda ctx: self._orders.__setitem__(self.symbol, self.qty),
            name="sma_buy_cross",
        )
        self._triggers.always(
            lambda ctx: bool(crossbelow(ctx["sma_short"], ctx["sma_long"]).iloc[-1]),
            lambda ctx: self._orders.__setitem__(self.symbol, -self.qty),
            name="sma_sell_cross",
        )

    def _select_price(self, history: pd.DataFrame) -> pd.Series | None:
        if self.symbol in history.columns:
            return CLOSE(history[[self.symbol]].rename(columns={self.symbol: "close"}))
        if "Close" in history.columns:
            return history["Close"]
        if "close" in history.columns:
            return history["close"]
        return None

    def decide(self, date: pd.Timestamp, history: pd.DataFrame) -> Dict[str, int]:
        if history.empty:
            return {}

        price = self._select_price(history)
        if price is None:
            return {}

        ctx = {
            "sma_short": MA(price, self.short_window),
            "sma_long": MA(price, self.long_window),
        }

        self._orders.clear()
        self._triggers.run(ctx)
        return dict(self._orders)


class MACDStrategy:
    """MACD crossover strategy (MACD line vs signal line)."""

    def __init__(self, symbol: str, fast: int = 12, slow: int = 26, signal: int = 9, qty: int = 100) -> None:
        self.symbol = symbol
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self.qty = qty
        self._orders: Dict[str, int] = {}
        self._triggers = TriggerSet()

        self._triggers.always(
            lambda ctx: bool(crossabove(ctx["macd"], ctx["signal"]).iloc[-1]),
            lambda ctx: self._orders.__setitem__(self.symbol, self.qty),
            name="macd_buy_cross",
        )
        self._triggers.always(
            lambda ctx: bool(crossbelow(ctx["macd"], ctx["signal"]).iloc[-1]),
            lambda ctx: self._orders.__setitem__(self.symbol, -self.qty),
            name="macd_sell_cross",
        )

    def _select_price(self, history: pd.DataFrame) -> pd.Series | None:
        if self.symbol in history.columns:
            return CLOSE(history[[self.symbol]].rename(columns={self.symbol: "close"}))
        if "Close" in history.columns:
            return history["Close"]
        if "close" in history.columns:
            return history["close"]
        return None

    def decide(self, date: pd.Timestamp, history: pd.DataFrame) -> Dict[str, int]:
        if history.empty:
            return {}

        price = self._select_price(history)
        if price is None:
            return {}

        macd_df = MACD(price, fast=self.fast, slow=self.slow, signal=self.signal)
        ctx = {
            "macd": macd_df["macd"],
            "signal": macd_df["signal"],
        }

        self._orders.clear()
        self._triggers.run(ctx)
        return dict(self._orders)