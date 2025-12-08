# risk

Source: `src/risk/risk_manager.py`

## Classes
- `class RiskManager`:
  - `__init__(self, max_position: float | None = None, max_drawdown: float | None = None)`: Initialize thresholds (currently unused).
  - `check_order(self, portfolio: Any, order: dict) -> bool`: TODO stub; intended to vet orders against risk rules.
  - `calculate_exposure(self, portfolio: Any) -> float`: TODO stub; intended to compute current exposure metric.

Risk controls are placeholders; extend `check_order` and `calculate_exposure` to enforce position sizing and drawdown rules.
