# portfolio

Source: `src/portfolio/manager.py`

## Classes
- `class PortfolioState`: Lightweight structure storing `cash: float`, `positions: dict[str, int]`, `history: list[dict]`.
  - `equity(prices: dict[str, float]) -> float`: Compute total equity from cash plus mark-to-market positions.

- `class PortfolioManager`:
  - `__init__(self, initial_cash: float = 1_000_000, commission: float = 0.0, slippage: float = 0.0)`: Initialize with cash and trading costs.
  - `snapshot(self, prices: dict[str, float]) -> dict`: Capture current account snapshot including equity and positions.
  - `apply_orders(self, orders: dict[str, int], prices: dict[str, float]) -> None`: Apply market orders, updating cash/positions with commission and slippage costs.
  - `value(self, prices: dict[str, float]) -> float`: Convenience to compute current equity.

## Functions
- `run_backtest(strategy, data: pandas.DataFrame, commission: float = 0.0, slippage: float = 0.0, initial_cash: float = 1_000_000) -> pandas.DataFrame`: Iterate over historical prices, call `strategy.decide(date, history)` each bar, apply resulting orders via `PortfolioManager`, and return equity curve DataFrame indexed by date.
