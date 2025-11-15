"""
风控模块接口定义：
- check_order 在下单前评估是否合规
- calculate_exposure 计算组合/账户风险指标
"""
from typing import Dict, Any


class RiskManager:
    def __init__(self, config: Dict[str, Any]):
        pass

    def check_order(self, order: Dict[str, Any], portfolio: Any) -> bool:
        """
        在下单前校验订单（资金、限仓、单笔风控等）。
        返回 True 表示通过，False 表示拒绝。
        """
        pass

    def calculate_exposure(self, portfolio: Any) -> Dict[str, Any]:
        """计算并返回当前风险敞口（如杠杆、集中度等）。"""
        pass