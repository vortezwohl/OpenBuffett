"""text2text 基础服务边界测试。

该文件验证 `Text2Text` 仍作为独立 NLP 接口存在，同时默认 agent 装配不再
依赖它作为会话控制或运行时桥接层。
"""

from __future__ import annotations

import unittest

from src.core import LLM, Text2Text
from src.app.default_agent import build_default_agent


class Text2TextBoundaryTests(unittest.TestCase):
    """验证 text2text 不再承担 agent runtime 主链职责。"""

    def test_text2text_remains_independent_llm_interface(self) -> None:
        """Text2Text 应继续是可独立构造的 LLM 实现。"""

        llm = Text2Text(
            provider="openai",
            model_name="demo-model",
            api_key="test-key",
            api_base="https://example.com/v1",
        )

        self.assertIsInstance(llm, LLM)
        self.assertEqual(llm.endpoint, "openai/demo-model")

    def test_default_agent_factory_does_not_reference_text2text(self) -> None:
        """默认 agent 装配不应把 text2text 拉回主链。"""

        names = build_default_agent.__code__.co_names

        self.assertNotIn("Text2Text", names)
        self.assertNotIn("text2text", names)


if __name__ == "__main__":
    unittest.main()
