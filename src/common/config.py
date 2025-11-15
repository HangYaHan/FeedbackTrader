"""
配置管理接口：读取/保存配置、环境覆盖、配置校验
"""
from typing import Mapping, Any


def load_config(path: str) -> Mapping[str, Any]:
    """
    从文件加载配置并返回配置字典。
    - path: 配置文件路径（yaml/json）
    """
    pass


def save_config(cfg: Mapping[str, Any], path: str) -> None:
    """
    将配置写回文件。
    """
    pass


def get_config_value(cfg: Mapping[str, Any], key: str, default: Any = None) -> Any:
    """
    从配置中安全读取值（含类型/范围校验）。
    """
    pass