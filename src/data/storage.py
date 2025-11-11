import os
import os
import pandas as pd
from ..system.log import get_logger

logger = get_logger(__name__)

CACHE_DIR = os.path.join(os.getcwd(), 'data_cache')
os.makedirs(CACHE_DIR, exist_ok=True)


def _cache_path(symbol):
    # 简单按 symbol 存单文件（可扩展为按年月分片）
    safe = symbol.replace('/', '_')
    return os.path.join(CACHE_DIR, f"{safe}.parquet")


def write_cache(symbol, df: pd.DataFrame):
    path = _cache_path(symbol)
    try:
        df.to_parquet(path)
        logger.info("Wrote cache for %s -> %s", symbol, path)
    except Exception as e:
        # 回退到 csv
        try:
            csvp = path + '.csv'
            df.to_csv(csvp)
            logger.warning("Parquet write failed for %s, wrote CSV -> %s; error=%s", symbol, csvp, e)
        except Exception as e2:
            logger.exception("Failed to write cache for %s: %s", symbol, e2)


def read_cached(symbol, start=None, end=None):
    path = _cache_path(symbol)
    df = None
    if os.path.exists(path):
        try:
            df = pd.read_parquet(path)
            logger.info("Cache hit (parquet) for %s -> %s", symbol, path)
        except Exception as e:
            logger.warning("Failed reading parquet cache for %s: %s", symbol, e)
            try:
                df = pd.read_csv(path + '.csv', index_col=0, parse_dates=True)
                logger.info("Read fallback CSV cache for %s", symbol)
            except Exception as e2:
                logger.warning("Failed reading CSV cache for %s: %s", symbol, e2)
                return None
    else:
        # 也尝试 csv 后缀
        csvp = path + '.csv'
        if os.path.exists(csvp):
            try:
                df = pd.read_csv(csvp, index_col=0, parse_dates=True)
                logger.info("Cache hit (csv) for %s -> %s", symbol, csvp)
            except Exception as e:
                logger.warning("Failed reading CSV cache for %s: %s", symbol, e)
                return None
        else:
            logger.debug("No cache found for %s", symbol)
            return None

    if start:
        df = df[df.index >= pd.to_datetime(start)]
    if end:
        df = df[df.index <= pd.to_datetime(end)]
    return df
