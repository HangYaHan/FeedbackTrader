import yfinance as yf
import pandas as pd
from ..exceptions import RateLimitError, AdapterError
from ..system.log import get_logger

logger = get_logger(__name__)


def fetch(symbol, start, end, interval='1d', adjusted=True, **kwargs):
    """使用 yfinance 拉取历史数据，返回 DataFrame（DatetimeIndex）。

    将 yfinance 的速率限制或网络错误映射为 RateLimitError/AdapterError。
    """
    try:
        # 明确 auto_adjust 参数以避免未来警告
        logger.debug("yfinance adapter: fetching %s %s-%s interval=%s", symbol, start, end, interval)
        df = yf.download(symbol, start=start, end=end, interval=interval, auto_adjust=adjusted, progress=False)
        if df is None or df.empty:
            logger.info("yfinance adapter: no data for %s", symbol)
            return pd.DataFrame()
        # yfinance 返回列通常为 Open/High/Low/Close/Adj Close/Volume
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        logger.info("yfinance adapter: fetched %s rows for %s", len(df), symbol)
        return df
    except Exception as e:
        # 简单映射：如果是速率限制（yfinance 在内部可能抛出特定错误），映射为 RateLimitError
        msg = str(e).lower()
        logger.exception("yfinance adapter error for %s: %s", symbol, e)
        if 'rate' in msg or 'limit' in msg or 'too many requests' in msg:
            raise RateLimitError(str(e))
        raise AdapterError(str(e))
