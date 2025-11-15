"""
常用指标接口（仅提供函数签名）
实现可用 pandas/numpy 完成
"""
import pandas as pd


def sma(series: pd.Series, window: int) -> pd.Series:
    """简单移动平均线接口。"""
    pass


def ema(series: pd.Series, window: int) -> pd.Series:
    """指数移动平均线接口。"""
    pass