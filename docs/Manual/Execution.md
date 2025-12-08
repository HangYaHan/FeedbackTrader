# execution

Source: `src/execution/broker.py`

## Interfaces
- `class BrokerInterface`: Abstract broker contract.
  - `place_order(symbol: str, qty: int, price: float | None = None, order_type: str = 'market') -> str`: Place an order and return broker order id.
  - `cancel_order(order_id: str) -> bool`: Cancel by id, return success flag.
  - `get_order_status(order_id: str) -> dict`: Return status payload for the given order.

Implementations are not provided; integrate with a live broker by subclassing `BrokerInterface` and implementing the three methods.
