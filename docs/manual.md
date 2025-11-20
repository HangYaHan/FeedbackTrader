# FeedbackTrader Manual

Last Updated: 2025-11-20

---
## 1. Introduction
FeedbackTrader is a modular backtesting and (future) live-trading research platform. It emphasizes:
- Clear separation of concerns (data acquisition, storage, portfolio/strategy, execution, reporting)
- Pluggable data adapters (yfinance, akshare, CSV, future broker APIs)
- Deterministic, inspectable backtest flows (daily snapshots + transaction history)
- Progressive roadmap toward an event-driven architecture, risk management, and live execution.

Target audience: quantitative strategy developers and system builders who value maintainability and extensibility.

---
## 2. High-Level Architecture

```
CLI / Backtest Command
	|
	v
+--------------------+         +------------------+
|  Backtest Engine   | ----->  |   task config    |
| (or driver script) |         +------------------+
+--------------------+
	|
	v
+--------------------+      (initialize)
|      Fetcher       |  -- cache-first -> fallback adapter
| - check cache      |
| - select adapter   |
+--------------------+
    |         |
cache hit     | adapter.fetch
    v         v
 +------+   +-----------------------------+
 |Cache |   | Adapter: yfinance/akshare...|
 |(parquet)| | - fetch(symbol,start,end)  |
 +------+   +-----------------------------+
      \         /
	v      v
+--------------------+
| Local Storage      | <-- normalized persistence (parquet)
+--------------------+
	|
	v
+--------------------+
| VirtualManager     | <-- load N strategies, aggregate actions
| - load strategies  |
| - aggregate actions|
+--------------------+
	|
	v
+--------------------+   (for each trading day)
|   Strategies (N)   | -> decide(date, history) -> {sym: qty}
+--------------------+
	|
	v
+--------------------+
| Execute / Update   | <- apply net actions at daily prices
+--------------------+
	|
	v
+--------------------+
| Daily Snapshots    | <- equity curve, positions, cash
+--------------------+
	|
	v
+--------------------+
| Visualize / Report |
+--------------------+
```

Responsibilities (from `blockdesign.md` refined):
- Backtest Driver: orchestrates daily loop, triggers reporting.
- Fetcher: unified API `get_history`, mediates cache + adapter selection, handles retries.
- Adapter: source-specific data acquisition & minimal normalization.
- Storage: efficient local parquet cache.
- VirtualManager: multi-strategy portfolio simulation, transaction + snapshot recording.
- Visualization/Report: post-run analytics (KPIs, charts). (Future)

---
## 3. Data Layer

### 3.1 Fetcher (`get_history`)
Cache-first unified entry point. Parameters: symbol, start, end, source (yfinance / akshare / csv), interval, adjusted, cache flags, retries with exponential backoff. Returns normalized OHLCV `DataFrame` or raises typed exceptions.

### 3.2 Adapters
Each adapter implements `fetch(symbol, start, end, interval, **kwargs) -> DataFrame`. Responsibilities: connect to source, minimal column/time normalization, raise unified exceptions (`RateLimitError`, `DataNotFoundError`, `AdapterError`, `NetworkError`). No global retry logic (delegated to Fetcher).

### 3.3 Storage
Uses parquet (columnar, compressed, fast selective reads). Recommended partitioning: `data/{source}/{symbol}/...` plus metadata (future: per year/month). Core operations: `read_cached`, `write_cache`, `list_cached_symbols`. Benefits: latency reduction, rate-limit avoidance, reproducibility.

### 3.4 Exceptions
Define a small stable taxonomy enabling deterministic control flow:
- `DataNotFoundError`: adapter returned empty/none
- `RateLimitError`: triggers retry/backoff
- `AdapterError`: source-specific failure
- `NetworkError`: low-level connectivity issues

### 3.5 Engineering Practices
- Single Responsibility: adapters do not implement caching / high-level orchestration.
- Lazy Imports: avoid loading heavy dependencies until needed (improves startup time).
- Observability: structured logging (future), surface retry counts & cache hit/miss metrics.
- Testability: mock adapter boundaries in unit tests; avoid hard-coded globals.

---
## 4. Portfolio & Strategy Layer

`VirtualManager` consolidates multiple strategies. Each strategy must implement `decide(date: pd.Timestamp, history: pd.DataFrame) -> Dict[str, int]` (positive=buy, negative=sell). Manager aggregates per-symbol quantities, executes at day prices via simplified fills (no fees/slippage yet), records:
- Transaction history (`_record_tx`) with deep-copied position snapshots
- Daily snapshots (equity, cash, unrealized/realized PnL)

Key extensibility points (see `virtualmanager.md`):
- Add fee/slippage models
- Order objects & execution types (market/limit)
- Risk checks (max position concentration, drawdown halts)
- Performance optimization (avoid frequent deep copies; incremental diffs)

Naming conventions (from `t1.md`): underscore prefix for internal methods (`_buy_at`), no underscore for public API (`get_summary`). Avoid overuse of double underscores except for name-mangling cases.

---
## 5. CLI / Backtest Driver (Planned)
Current manual focuses on core libraries. Future CLI will:
- Parse configuration (JSON/YAML) per task
- Instantiate adapters/fetcher/manager/strategies dynamically
- Output standardized run artifact directory (logs, snapshots parquet, report HTML)

Engineering practices:
- Strict command validation
- Clear error messages (unknown adapter, invalid date range)
- Separation of presentation (CLI) vs orchestration logic.

---
## 6. Installation & Quick Start
1. Create and activate virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Fetch data example (akshare): run the provided script under `scripts/` (e.g. `fetch_akshare_save.py`).
4. Use `get_history` directly in exploratory notebook to retrieve cached vs remote data.
5. Write a minimal strategy implementing `decide` and pass a price DataFrame to a `VirtualManager` instance.

Example (conceptual):
```python
vm = VirtualManager("demo", 50000)
vm.add_strategy(MyStrategy())
prices = get_history("AAPL", "2024-01-01", "2024-03-31")[["Close"]].rename(columns={"Close":"AAPL"})
for date in prices.index:
    history = prices.loc[:date].iloc[:-1]
    actions = vm._aggregate_actions(date, history)
    vm._execute_actions(actions, {"AAPL": prices.loc[date, "AAPL"]}, date)
summary = vm.get_summary()
```

---
## 7. Fetching Market Data
Use `get_history` (see `interface/get_history.md`). Key guidelines:
- Prefer cache unless explicitly refreshing (`refresh=True`).
- Control retries to respect remote limits.
- Normalize columns early (consistent OHLCV naming) for downstream indicators.
- Consider partition strategy for large symbols/time ranges.

---
## 8. Backtesting Workflow (Daily Loop)
For each trading day:
1. Slice `history` (past days only) for strategies.
2. Collect strategy decisions -> aggregated net actions.
3. Execute trades at daily closing (or defined) price.
4. Record transaction & snapshot.
5. After final day, compute KPIs & export artifacts.

Extensibility: replace step 3 with event-driven order matching (BAR -> SIGNAL -> ORDER -> FILL) as per roadmap.

---
## 9. Extending the System
### New Adapter
1. Create file `src/data/adapters/my_adapter.py` implementing `fetch`.
2. Map in `ADAPTER_MODULES` (`fetcher.py`).
3. Raise unified exceptions; avoid leaking vendor-specific ones.
4. Provide small unit test with monkeypatch / fixture.

### New Strategy
1. Implement `decide(date, history)`; ensure idempotent given same inputs.
2. Avoid network calls inside strategy; pre-load required data externally.
3. Return integers (shares) not floats.
4. Consider edge cases: empty history, NaN prices.

### Performance Enhancements
- Migrate snapshots/history to on-disk parquet for large runs.
- Lazy compute KPIs only at end.
- Vectorize indicator calculations (use pandas / numba where beneficial).

---
## 10. Logging & Diagnostics (Planned)
Goals:
- Structured logs (JSON) with correlation IDs per backtest
- Metrics: cache hit ratio, adapter latency, retry counts
- Trace slow strategy decisions
Future integration with Prometheus / OpenTelemetry for live mode.

---
## 11. Roadmap (Condensed from `plan.md`)
Phases:
- Phase 1: Core framework (fetcher, adapters, storage, basic backtest engine, tests, CI, formatting) — IN PROGRESS
- Phase 2: Strategy dev ergonomics (rich lifecycle, indicator library)
- Phase 3: Execution & risk (order objects, risk manager, simulated broker)
- Phase 4: Live trading integration (broker adapters, monitoring, alerting)
- Phase 5: Optimization & ML integration (performance tuning, feature pipeline)

Principles: incremental delivery; keep interfaces stable; prefer composition over inheritance; maintain test coverage per module.

---
## 12. Domain Knowledge (Brief)
Parquet advantages (from `Parquet.md`): columnar compression, predicate pushdown, schema evolution, ecosystem support — ideal for historical market data & feature sets. Avoid for high-frequency single-row transactional writes.

---
## 13. Python Package & Import Practices
Key guidelines (`Use__init__.md`):
- Every package directory includes `__init__.py` for explicit packages.
- Public API exposed via selective imports in `__init__.py`.
- Use absolute imports across packages; relative only within the same package.
- Mitigate circular imports via lazy imports or refactoring into shared modules.

---
## 14. Testing Strategy
Unit tests isolate modules (mock adapters). Example coverage:
- Fetcher: cache hit/miss, adapter selection, retry/backoff, exception propagation.
- VirtualManager: buy/sell flows, partial fills due to insufficient cash, summary correctness.
Planned: integration tests for multi-strategy scenarios; performance tests (profiling); regression suite for KPI stability.

Practices:
- Keep tests deterministic (fixed seeds, stub time).
- Fail fast on data anomalies (raise structured exceptions).
- Measure test runtime; optimize large DataFrame fixtures via minimal samples.

---
## 15. Recent Changes & Audit Trail
See `recent_changes.md` and `manager_record_tx_change.md` for transactional history of modifications (e.g., `_record_tx` addition). Maintain human-readable & machine-parsable change logs for traceability.

---
## 16. Known Gaps / TODO
From `TODO.md` & review:
- No market microstructure rules (lot size, trading halts)
- No periodic cash flows (e.g., monthly deposits)
- Incomplete test coverage for internally generated modules
- Deep copy overhead in transaction history (optimize later)

---
## 17. Style & Conventions
- Underscore prefix for internal methods; avoid unnecessary dunder names.
- Consistent DataFrame column naming (e.g., `Open`, `High`, `Low`, `Close`, `Volume`).
- Use ISO date strings or `pd.Timestamp` in persisted metadata.
- Prefer explicitness: avoid silent coercions; validate inputs early.

---
## 18. Future Enhancements (Ideas)
- Event Bus: unify data ticks, signals, orders, fills (loosely coupled handlers).
- Risk Manager: pre-trade & intra-day checks (exposure, drawdown).
- Performance Module: KPIs (annualized return, Sharpe, max drawdown) + HTML report.
- ML Pipeline: feature store (parquet), model inference integrated as a strategy.
- Live Broker Adapters: simulated vs real; common `Broker` interface.
- Monitoring/Alerting: anomalies in latency, PnL swings, connection status.

---
## 19. Contribution Guidelines (Draft)
- Branch naming: `feature/<topic>`, `fix/<issue>`, `docs/<section>`.
- PR checklist: tests added/passed, doc updates, no unrelated refactors.
- Code review focus: interface stability, error handling completeness, performance implications.
- Semantic versioning for releases once API stabilizes.

---
## 20. Appendix / Resources
- Clean Architecture (Robert C. Martin)
- Adapter / Facade / Strategy design patterns (GoF)
- PyArrow + Parquet docs
- pandas & pytest official documentation
- Quant performance libraries: `quantstats`, `pyfolio` (future integration)

---
## 21. Glossary (Selected)
- Adapter: thin layer translating external data source into unified DataFrame.
- Cache Hit: data served from local parquet store.
- Snapshot: daily portfolio state after applying actions.
- Equity Curve: time series of portfolio value.
- Net Action: aggregated sum of all strategies' share intents for a symbol.

---
End of Manual.