"""基础 NLP 与模型抽象模块。

该包不再承载 agent runtime、工具调度或事件流主链。SmartIPO 的默认
agent 会话运行时由 EasyHarness 提供；此处仅保留独立基础 NLP 能力。
"""

from src.core.llm import LLM
from src.core.text2text import Text2Text

__all__ = [
    "LLM",
    "Text2Text",
]
