# common

Sources: `src/common/config.py`, `src/common/utils.py`

## config
- `load_config(path: str) -> dict | None`: TODO stub; intended to load config from file.
- `save_config(cfg: dict, path: str) -> None`: TODO stub; intended to persist config.
- `get_config_value(cfg: dict, key: str, default: Any = None) -> Any`: TODO stub; intended safe lookup.

## utils
- `ensure_dir(path: str) -> None`: TODO stub; expected to create directory if missing.
- `parse_date(value: str | datetime) -> datetime`: TODO stub; expected to coerce input to `datetime`.
- `chunk_iterable(it: Iterable[T], size: int) -> Iterable[list[T]]`: TODO stub; expected to yield fixed-size chunks.
