"""基础校验工具。

该文件提供简单的 JSON 键存在性与类型判断辅助函数。
"""

from collections.abc import Iterable
from typing import Any, Type


def json_key_validator(json_data: dict, keys_required: Iterable[str]) -> bool:
    """校验字典是否包含所有必需键。"""
    if not isinstance(json_data, dict):
        return False
    for _k in keys_required:
        if _k not in json_data.keys():
            return False
    return True


def type_validator(data: Any, _type: Type) -> bool:
    """判断数据是否属于指定类型。"""
    return isinstance(data, _type)
