"""
Backtest 引擎接口：
- run_backtest(strategy, data, portfolio, start, end, config)
- 支持回测结果导出（绩效、逐笔记录）
"""
from typing import Any, Dict


class BacktestEngine:
    def __init__(self, config: Dict[str, Any]):
        """初始化回测引擎（传入配置）。"""
        pass

    def run_backtest(self, strategy: Any, data_source: Any, portfolio: Any, start, end) -> Dict[str, Any]:
        """
        运行回测并返回结果字典（包括历史市值、交易记录、绩效指标等）。
        """
        pass