import pandas as pd
import pytest
import types

from src.data import fetcher, storage, exceptions


class DummyAdapter:
    def __init__(self, responses):
        # responses: list of either DataFrame or exception to raise
        self._responses = responses
        self.calls = 0

    def fetch(self, symbol, start, end, **kwargs):
        resp = self._responses[self.calls]
        self.calls += 1
        if isinstance(resp, Exception):
            raise resp
        return resp


def make_df():
    idx = pd.date_range('2022-01-01', periods=3, freq='D')
    return pd.DataFrame({'Close': [1, 2, 3]}, index=idx)


def test_cache_hit(monkeypatch, tmp_path):
    # mock read_cached 返回 dataframe
    df = make_df()
    monkeypatch.setattr(storage, 'read_cached', lambda symbol, start, end: df)
    res = fetcher.get_history('SYM', '2022-01-01', '2022-01-03', source='csv', cache=True)
    assert isinstance(res, pd.DataFrame)
    assert not res.empty


def test_adapter_fetch_and_write(monkeypatch, tmp_path):
    # 模拟缓存未命中，适配器返回数据，并确保 write_cache 被调用
    df = make_df()
    monkey = {'written': False}

    monkeypatch.setattr(storage, 'read_cached', lambda symbol, start, end: None)
    monkeypatch.setattr(storage, 'write_cache', lambda symbol, df: monkey.update({'written': True}))

    dummy = DummyAdapter([df])
    monkeypatch.setitem(fetcher.ADAPTERS, 'dummy', dummy)

    res = fetcher.get_history('SYM', '2022-01-01', '2022-01-03', source='dummy', cache=True)
    assert isinstance(res, pd.DataFrame)
    assert monkey['written'] is True


def test_rate_limit_retry(monkeypatch):
    # 模拟前两次抛出 RateLimitError, 第三次返回数据
    from src.data.exceptions import RateLimitError
    df = make_df()
    dummy = DummyAdapter([RateLimitError('rate'), RateLimitError('rate'), df])
    monkeypatch.setitem(fetcher.ADAPTERS, 'dummy2', dummy)

    # mock read_cached
    monkeypatch.setattr(storage, 'read_cached', lambda symbol, start, end: None)
    # speed up sleeps
    monkeypatch.setattr('time.sleep', lambda s: None)

    res = fetcher.get_history('SYM', '2022-01-01', '2022-01-03', source='dummy2', cache=False, max_retries=5, backoff_factor=0)
    assert isinstance(res, pd.DataFrame)
    assert not res.empty


def test_data_not_found(monkeypatch):
    # 适配器返回空 DataFrame -> DataNotFoundError
    df_empty = pd.DataFrame()
    dummy = DummyAdapter([df_empty])
    monkeypatch.setitem(fetcher.ADAPTERS, 'dummy3', dummy)
    monkeypatch.setattr(storage, 'read_cached', lambda symbol, start, end: None)

    with pytest.raises(exceptions.DataNotFoundError):
        fetcher.get_history('SYM', '2022-01-01', '2022-01-03', source='dummy3', cache=False)
