"""扩展能力包。

该包用于存放独立于基础文本模型之外的扩展能力封装。当前主要提供
Seedream 生图调用入口，供上层按需导入和组合。
"""

from src.ext.seedream import (
    SeedreamClient,
    SeedreamImageResult,
    generate_seedream_image,
)

__all__ = [
    "SeedreamClient",
    "SeedreamImageResult",
    "generate_seedream_image",
]
