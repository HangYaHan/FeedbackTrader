"""
通用工具函数接口（日期解析、路径保证、序列化等）
"""
from datetime import datetime
from typing import Iterable, Any


def ensure_dir(path: str) -> None:
    """确保目录存在（如果不存在则创建）。"""
    pass


def parse_date(value: str) -> datetime:
    """把字符串解析为 datetime（支持多种格式）。"""
    pass


def chunk_iterable(it: Iterable[Any], size: int):
    """将可迭代对象分块，返回生成器。"""
    pass