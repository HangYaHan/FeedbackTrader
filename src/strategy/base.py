"""
Strategy 基类接口定义
- 生命周期方法（on_start/on_stop）
- 市场数据回调（on_bar/on_tick）
- 信号生成接口
"""
from typing import Any
import pandas as pd


class Strategy:
    def __init__(self, config: dict):
        """初始化策略实例（接收配置字典）。"""
        self.config = config

    def on_start(self) -> None:
        """策略启动回调（初始化内部状态）。"""
        pass

    def on_stop(self) -> None:
        """策略停止回调（清理资源）。"""
        pass

    def on_bar(self, bar: pd.Series) -> None:
        """接收一根 K 线（或一条聚合数据）。"""
        pass

    def on_tick(self, tick: Any) -> None:
        """接收逐笔/行情 tick 数据。"""
        pass

    def generate_signals(self) -> Any:
        """返回信号对象（可由框架统一解析为订单）。"""
        pass