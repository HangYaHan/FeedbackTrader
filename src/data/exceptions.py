class DataFetchError(Exception):
    """Base exception for data fetching errors."""


class RateLimitError(DataFetchError):
    """Raised when requests are rate-limited (HTTP 429 or provider limits)."""


class DataNotFoundError(DataFetchError):
    """Raised when requested data is not available or empty."""


class AdapterError(DataFetchError):
    """Raised when an adapter encounters an internal error."""


class NetworkError(DataFetchError):
    """Raised for network-related errors (connection, timeout, DNS, etc.)."""
