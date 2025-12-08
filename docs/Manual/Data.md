# data

Sources: `src/data/fetcher.py`, `src/data/storage.py`, `src/data/exceptions.py`, `src/data/adapters/*.py`

## fetcher
- `select_adapter(name: str) -> Callable`: Map adapter name (`akshare`, `yfinance`, `csv`) to fetch function; raises `AdapterError` on unknown.
- `get_history(symbol: str, start: str | None, end: str | None, *, source: str = 'akshare', interval: str = '1d', adjusted: bool = True, cache: bool = True, refresh: bool = False) -> pandas.DataFrame`: Fetch historical OHLCV using adapter, optionally using parquet cache. Respects `refresh` to bypass cache; writes cache on success.
- `valid_test() -> pandas.DataFrame | None`: Quick fetch of sample symbol for smoke-testing adapters.

## storage
- `_cache_path(symbol: str) -> pathlib.Path`: Internal helper computing parquet cache path under `data/`.
- `write_cache(symbol: str, df: pandas.DataFrame) -> None`: Save DataFrame to parquet cache (creates parent dirs).
- `read_cached(symbol: str, start: str | None = None, end: str | None = None) -> pandas.DataFrame | None`: Load cached parquet data, optionally slice by date range; returns `None` if missing.

## exceptions
- `DataFetchError`, `RateLimitError`, `DataNotFoundError`, `AdapterError`, `NetworkError`: Domain-specific exception classes for data layer.

## adapters
- `akshare_adapter.fetch(symbol: str, start: str | None, end: str | None, interval: str = '1d', adjusted: bool = True, **kwargs) -> pandas.DataFrame`: Fetch via `akshare`. Converts dtypes, sets datetime index, returns OHLCV.
- `yfinance_adapter.fetch(symbol: str, start: str | None, end: str | None, interval: str = '1d', adjusted: bool = True, **kwargs) -> pandas.DataFrame`: Fetch via `yfinance.download`, returning OHLCV with datetime index.
- `csv_adapter.fetch(symbol: str, start: str | None, end: str | None, interval: str = '1d', **kwargs) -> pandas.DataFrame`: Read local CSV (path provided in `kwargs['path']`), parse dates, rename to OHLCV columns; raises on missing path.
