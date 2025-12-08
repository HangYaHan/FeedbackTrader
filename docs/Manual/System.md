# system

Sources: `src/system/CLI.py`, `src/system/json.py`, `src/system/log.py`, `src/system/main_window.py`

## CLI
- `print_help() -> None`: Print CLI help text.
- `interactive_loop() -> int`: Simple REPL supporting commands `help`, `exit`, `backtest TASK`, `config`, `plot ...`; delegates to backtest/plot modules.
- `main(argv: list[str] | None = None) -> int`: Entry point wrapper for `interactive_loop` with error handling.

## json helpers
- `read_json(path: str | Path, default: Any | None = None) -> Any`: Read JSON file; return `default` on missing/parse error.
- `write_json(path: str | Path, data: Any, *, indent: int = 2, ensure_ascii: bool = False) -> None`: Write JSON, creating parent directories; logs and re-raises on error.
- `safe_loads(s: str, default: Any | None = None) -> Any`: Parse JSON string, returning `default` on error.
- `safe_dumps(obj: Any, *, indent: int = 2, ensure_ascii: bool = False) -> str`: Serialize object to JSON string.

## log
- `configure_root_logger(level=logging.INFO) -> None`: Idempotent root logger setup writing to timestamped file under `logs/`; removes console handlers.
- `get_logger(name: str | None = None) -> logging.Logger`: Configure root once then return logger.

## main_window
- Placeholder file; no content yet.
