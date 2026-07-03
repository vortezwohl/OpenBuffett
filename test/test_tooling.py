"""EasyHarness 工具与默认装配测试。

该文件验证 SmartIPO 默认工具集合已经切换为 EasyHarness 公共工具合同：
官方 fileglide toolset 提供文件能力，Seedream 业务工具使用 `@tool` 声明。
"""

from __future__ import annotations

import unittest
from unittest.mock import patch

from easyharness import Agent, ModelConfig, ToolOutput

from src.app.default_agent import (
    DEFAULT_BUSINESS_TOOL_NAMES,
    DEFAULT_FILEGLIDE_TOOL_NAMES,
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_WORKBENCH_TOOL_NAMES,
    build_default_agent,
    build_default_tools,
)
from src.tool.seedream_image import SEEDREAM_IMAGE_TOOL


class EasyHarnessToolingTests(unittest.TestCase):
    """验证 EasyHarness 工具体系与默认 composition 层。"""

    def test_default_tool_names_use_easyharness_public_names(self) -> None:
        """默认工具名应使用官方 fileglide 与业务工具公开名。"""

        self.assertIn("fileglide_read_text", DEFAULT_FILEGLIDE_TOOL_NAMES)
        self.assertIn("fileglide_edit_text", DEFAULT_FILEGLIDE_TOOL_NAMES)
        self.assertIn("generate_seedream_image", DEFAULT_BUSINESS_TOOL_NAMES)
        self.assertEqual(
            DEFAULT_WORKBENCH_TOOL_NAMES,
            (*DEFAULT_FILEGLIDE_TOOL_NAMES, *DEFAULT_BUSINESS_TOOL_NAMES),
        )
        self.assertIn("EasyHarness", DEFAULT_SYSTEM_PROMPT)
        self.assertNotIn("text.read", DEFAULT_SYSTEM_PROMPT)

    def test_build_default_tools_returns_public_tool_objects(self) -> None:
        """默认工具对象集合应可直接交给 EasyHarness Agent 使用。"""

        tools = build_default_tools(".")
        names = {getattr(item, "tool_name", "") for item in tools}

        self.assertIn("fileglide_read_text", names)
        self.assertIn("fileglide_search_text", names)
        self.assertIn("generate_seedream_image", names)

    def test_build_default_agent_returns_easyharness_agent(self) -> None:
        """默认 agent 装配入口应直接返回 EasyHarness Agent。"""

        with patch.dict("os.environ", {"API_KEY": "test-key"}, clear=False):
            agent = build_default_agent(".")

        self.assertIsInstance(agent, Agent)

    def test_seedream_tool_returns_tool_output(self) -> None:
        """Seedream 业务工具应返回 EasyHarness ToolOutput。"""

        fake_result = type(
            "FakeSeedreamResult",
            (),
            {
                "model": "seedream-test",
                "prompt": "画一只猫",
                "images": [{"url": "https://example.com/cat.png"}],
                "response_payload": {"ok": True},
            },
        )()

        with patch(
            "src.tool.seedream_image.generate_seedream_image",
            return_value=fake_result,
        ):
            output = SEEDREAM_IMAGE_TOOL(prompt="画一只猫")

        self.assertIsInstance(output, ToolOutput)
        self.assertEqual(output.data["model"], "seedream-test")
        self.assertEqual(output.data["image_count"], 1)
        self.assertIn("Seedream generated 1 image item", output.preview)


if __name__ == "__main__":
    unittest.main()
