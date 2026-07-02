"""主脑可调用工具集合。

该包负责定义项目内业务能力的统一 tool 契约与注册入口。第一版只接入
真实的 Seedream 生图能力，后续其他能力沿同一接入面扩展即可。
"""

from src.tool.seedream_image import TOOL_SPEC as SEEDREAM_IMAGE_TOOL_SPEC

__all__ = [
    "SEEDREAM_IMAGE_TOOL_SPEC",
]
