"""序列化辅助工具。

该文件提供把枚举、模型、列表和字典递归转换为字典值的通用方法。
"""

from enum import Enum
from typing import Any
import base64
from pathlib import Path


def to_dict_value(value: Any) -> Any:
    """递归把对象转换为适合序列化的基础值。"""
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return value.to_dict()
    if isinstance(value, list):
        return [to_dict_value(item) for item in value]
    if isinstance(value, dict):
        return {key: to_dict_value(item) for key, item in value.items()}
    return value


def local_file_to_base64(file_path: str) -> str:
    """把本地文件转成纯 Base64 字符串。"""
    path = Path(file_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    if not path.is_file():
        raise ValueError(f"给定路径不是文件: {path}")

    return base64.b64encode(path.read_bytes()).decode("utf-8")
