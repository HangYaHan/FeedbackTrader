"""
Portfolio 管理器接口：
- 管理持仓、现金、估值
- 提供下单建议与成交回调
"""
from typing import Dict, Any


class Portfolio:
    def __init__(self, initial_cash: float, config: Dict[str, Any]):
        """初始化投资组合。"""
        pass

    def allocate(self, symbol: str, quantity: float) -> None:
        """调整持仓分配（仅修改内部目标仓位）。"""
        pass

    def update_on_fill(self, order: Dict[str, Any], fill: Dict[str, Any]) -> None:
        """交易被成交后的回调，用于更新持仓和现金。"""
        pass

    def get_positions(self) -> Dict[str, Any]:
        """返回当前持仓快照。"""
        pass

    def get_value(self) -> float:
        """返回组合当前估值（含现金）。"""
        pass