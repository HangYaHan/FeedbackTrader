"""
VirtualManager: supports loading any number of strategies. For each trading day,
each strategy produces actions (buy/sell X shares). Actions from all strategies
are summed into `next_action` and executed at that day's prices. The manager
records positions, cash, realized/unrealized P&L and historical transactions.

Strategy interface contract (required):
- decide(date: pd.Timestamp, history: pd.DataFrame) -> Dict[str, int]
    Return a dict mapping symbol -> integer quantity (positive for buy, negative for sell).
    `history` is a price DataFrame containing past dates (excluding the current date),
    indexed by date with columns for each symbol.

Note: This is a simplified model without fees, slippage, partial fills, margin, etc.
It is intended as a basic backtest foundation.
"""
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import copy
import pandas as pd


class VirtualManager:
    def __init__(self, name: str, initial_cash: float = 100000.0) -> None:
        if initial_cash < 0:
            raise ValueError("initial_cash must be non-negative")
        self.name: str = name
        self.initial_cash: float = float(initial_cash)
        self.cash: float = float(initial_cash)
        # positions: symbol -> {'quantity': int, 'avg_cost': float}
        self.positions: Dict[str, Dict[str, float]] = {}
        # market prices: symbol -> last known price
        self._market_prices: Dict[str, float] = {}
        self.realized_pnl: float = 0.0
        # trade history (per-trade)
        self.history: List[Dict[str, Any]] = []
        # daily snapshot history (for backtest output)
        self.daily_snapshots: List[Dict[str, Any]] = []
        # list of strategy instances
        self.strategies: List[Any] = []

    # --- strategy management ---
    def add_strategy(self, strategy: Any) -> None:
        """
        Add a strategy instance. The strategy must implement decide(date, history).
        """
        if not hasattr(strategy, "decide") or not callable(strategy.decide):
            raise ValueError("strategy must implement decide(date, history) -> Dict[str,int]")
        self.strategies.append(strategy)

    # --- market prices & valuation ---
    def update_market_price(self, symbol: str, price: float) -> None:
        if price is None or price < 0:
            return
        self._market_prices[symbol] = float(price)

    def get_portfolio_value(self) -> float:
        market_value = 0.0
        for sym, pos in self.positions.items():
            qty = pos.get("quantity", 0)
            price = self._market_prices.get(sym, pos.get("avg_cost", 0.0))
            market_value += qty * price
        return float(self.cash + market_value)

    def get_unrealized_pnl(self) -> float:
        unreal = 0.0
        for sym, pos in self.positions.items():
            qty = pos.get("quantity", 0)
            avg = pos.get("avg_cost", 0.0)
            price = self._market_prices.get(sym, avg)
            unreal += (price - avg) * qty
        return float(unreal)

    # --- order execution (simplified: executes at provided price) ---
    def _buy_at(self, symbol: str, quantity: int, price: float, timestamp: Optional[datetime] = None) -> bool:
        if quantity <= 0 or price <= 0:
            return False
        total = quantity * price
        if self.cash < total:
            # Insufficient funds: scale down quantity to what is affordable
            max_affordable = int(self.cash // price)
            if max_affordable <= 0:
                return False
            quantity = max_affordable
            total = quantity * price
        self.cash -= total
        if symbol in self.positions:
            pos = self.positions[symbol]
            old_qty = pos["quantity"]
            old_avg = pos["avg_cost"]
            new_qty = old_qty + quantity
            new_avg = ((old_avg * old_qty) + total) / new_qty
            pos["quantity"] = new_qty
            pos["avg_cost"] = new_avg
        else:
            self.positions[symbol] = {"quantity": quantity, "avg_cost": float(price)}
        self.update_market_price(symbol, price)
        self._record_tx("BUY", symbol, quantity, price, timestamp)
        return True

    def _sell_at(self, symbol: str, quantity: int, price: float, timestamp: Optional[datetime] = None) -> bool:
        if quantity <= 0 or price <= 0:
            return False
        pos = self.positions.get(symbol)
        if not pos or pos.get("quantity", 0) <= 0:
            return False
        available = pos["quantity"]
        if quantity > available:
            # If selling more than held, sell all available
            quantity = available
        proceeds = quantity * price
        avg = pos["avg_cost"]
        self.cash += proceeds
        # realized pnl for the sold portion
        self.realized_pnl += (price - avg) * quantity
        pos["quantity"] -= quantity
        if pos["quantity"] == 0:
            del self.positions[symbol]
            self._market_prices.pop(symbol, None)
        else:
            self.positions[symbol] = pos
        self.update_market_price(symbol, price)
        self._record_tx("SELL", symbol, quantity, price, timestamp)
        return True

    def _record_tx(self, side: str, symbol: str, quantity: int, price: float, timestamp: Optional[datetime] = None) -> None:
        """
        Record a single transaction into `self.history`. Stores type, symbol,
        quantity, price, time, resulting cash and a snapshot of positions.
        """
        tx = {
            "type": side,
            "symbol": symbol,
            "quantity": int(quantity),
            "price": float(price),
            "timestamp": timestamp.isoformat() if hasattr(timestamp, "isoformat") else str(timestamp),
            "cash": float(self.cash),
            "positions": copy.deepcopy(self.positions),
        }
        self.history.append(tx)

    # --- aggregate strategy decisions and execute ---
    def _aggregate_actions(self, date: pd.Timestamp, history: pd.DataFrame) -> Dict[str, int]:
        """
        Call each strategy's decide method and aggregate net buy/sell quantities per symbol.
        Returns a dict symbol -> net_quantity (positive buy, negative sell).
        """
        agg: Dict[str, int] = {}
        for strat in self.strategies:
            try:
                actions = strat.decide(date, history) or {}
                if not isinstance(actions, dict):
                    continue
                for sym, qty in actions.items():
                    if qty is None:
                        continue
                    agg[sym] = agg.get(sym, 0) + int(qty)
            except Exception:
                # Ignore errors from strategies for this decision cycle
                continue
        return agg

    def _execute_actions(self, actions: Dict[str, int], price_map: Dict[str, float], timestamp: Optional[datetime] = None) -> None:
        """
        Execute aggregated actions:
        - For each symbol: call _buy_at for positive quantities, _sell_at for negative.
        - price_map is a dict symbol -> price used for execution.
        """
        for sym, net_qty in actions.items():
            if net_qty == 0:
                continue
            price = price_map.get(sym)
            if price is None or price <= 0:
                # Cannot execute without a valid price
                continue
            if net_qty > 0:
                self._buy_at(sym, net_qty, price, timestamp)
            else:
                self._sell_at(sym, -net_qty, price, timestamp)

    def get_summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "initial_cash": self.initial_cash,
            "cash": self.cash,
            "positions": copy.deepcopy(self.positions),
            "market_prices": copy.deepcopy(self._market_prices),
            "portfolio_value": float(self.get_portfolio_value()),
            "unrealized_pnl": float(self.get_unrealized_pnl()),
            "realized_pnl": float(self.realized_pnl),
            "total_pnl": float(self.realized_pnl + self.get_unrealized_pnl()),
            "return_pct": (self.get_portfolio_value() - self.initial_cash) / self.initial_cash if self.initial_cash else 0.0,
            "n_positions": len(self.positions),
            "last_tx": self.history[-1] if self.history else None,
        }

    def get_history(self) -> List[Dict[str, Any]]:
        return copy.deepcopy(self.history)

    def get_daily_snapshots(self) -> List[Dict[str, Any]]:
        return copy.deepcopy(self.daily_snapshots)
