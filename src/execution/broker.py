"""
Broker / Execution 接口定义：
- place_order / cancel_order / get_order_status / simulate_fill 等
- 实盘适配器需实现这些接口
"""
from typing import Dict, Any


class BrokerInterface:
    def place_order(self, order: Dict[str, Any]) -> str:
        """提交订单，返回 order_id（字符串）。"""
        raise NotImplementedError

    def cancel_order(self, order_id: str) -> bool:
        """取消订单，返回是否成功。"""
        raise NotImplementedError

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """查询订单状态，返回字典描述。"""
        raise NotImplementedError