"""主脑运行时相关模块。

该包用于存放最小 strands agent loop 运行时骨架，职责是把主脑模型、
工具注册表和具体业务能力串起来，而不是承载完整应用状态机。
"""

from src.core.agent_loop import AgentLoop
from src.core.strands_runtime import StrandsRunResult, StrandsRuntime

__all__ = [
    "AgentLoop",
    "StrandsRunResult",
    "StrandsRuntime",
]
