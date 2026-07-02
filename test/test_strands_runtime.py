"""Strands 最小运行时测试。

该文件只验证本次 strands agent runtime 集成的最小闭环：主脑模型装配、
工具成功调用、工具失败边界和工具暴露子集，不依赖真实外部 LLM 请求。
"""

from __future__ import annotations

import unittest
from unittest.mock import patch

from strands import Agent

from src.base.agent import build_litellm_model
from src.core.agent_loop import AgentLoop
from src.core.strands_runtime import StrandsRunResult
from src.ext.seedream import SeedreamImageResult
from src.tool.contracts import ToolContext, ToolResult, ToolSpec
from src.tool.registry import ToolRegistry, build_default_tool_registry


class _FakeSuccessRuntime:
    """用于模拟工具成功调用的 strands runtime。"""

    requires_model = False

    def __init__(self) -> None:
        self.seen_tool_names: list[str] = []

    def run(self, prompt: str, *, model, tools, system_prompt: str) -> StrandsRunResult:
        self.seen_tool_names = [item.tool_name for item in tools]
        tool_map = {item.tool_name: item for item in tools}
        tool_map["generate_seedream_image"](prompt=prompt)
        return StrandsRunResult(text="image generated")


class _FakeFailureRuntime:
    """用于模拟工具失败调用的 strands runtime。"""

    requires_model = False

    def run(self, prompt: str, *, model, tools, system_prompt: str) -> StrandsRunResult:
        tool_map = {item.tool_name: item for item in tools}
        tool_map["generate_seedream_image"](prompt=prompt)
        return StrandsRunResult(text="should not reach here")


class _FakeCaptureRuntime:
    """用于验证当前回合实际暴露了哪些工具。"""

    requires_model = False

    def __init__(self) -> None:
        self.seen_tool_names: list[str] = []

    def run(self, prompt: str, *, model, tools, system_prompt: str) -> StrandsRunResult:
        self.seen_tool_names = [item.tool_name for item in tools]
        return StrandsRunResult(text="captured")


class StrandsRuntimeTests(unittest.TestCase):
    """验证最小 strands runtime 集成。"""

    def test_litellm_model_and_agent_construct(self) -> None:
        """主脑模型与 Agent 构造应按当前装配方式成功。"""

        model = build_litellm_model(
            provider="openai",
            model_name="gpt-4.1-mini",
            api_key="test-key",
            api_base="https://example.com/v1",
            temperature=0.2,
            top_p=0.8,
            seed=7,
        )

        self.assertEqual(model.config["model_id"], "openai/gpt-4.1-mini")
        self.assertEqual(model.client_args["api_key"], "test-key")
        self.assertEqual(model.client_args["api_base"], "https://example.com/v1")
        self.assertEqual(model.config["params"]["temperature"], 0.2)
        self.assertEqual(model.config["params"]["top_p"], 0.8)
        self.assertEqual(model.config["params"]["seed"], 7)
        agent = Agent(model=model, tools=[], system_prompt="demo")
        self.assertIsInstance(agent, Agent)

    def test_fake_runtime_executes_exposed_tool_and_returns_summary(self) -> None:
        """已暴露工具应能被 fake runtime 调用并返回统一结果。"""

        runtime = _FakeSuccessRuntime()
        loop = AgentLoop(
            model=None,
            tool_registry=build_default_tool_registry(),
            runtime=runtime,
        )
        fake_result = SeedreamImageResult(
            model="demo-model",
            prompt="draw a skyline",
            images=[{"url": "https://example.com/demo.png"}],
            response_payload={"data": [{"url": "https://example.com/demo.png"}]},
        )

        with patch(
            "src.tool.seedream_image.generate_seedream_image",
            return_value=fake_result,
        ) as patched:
            result = loop.run_once(
                "draw a skyline",
                system_prompt="You are a helpful image agent.",
            )

        patched.assert_called_once()
        self.assertEqual(result.text, "image generated")
        self.assertEqual(runtime.seen_tool_names, ["generate_seedream_image"])
        self.assertEqual(len(result.tools), 1)
        self.assertEqual(result.tools[0].name, "generate_seedream_image")
        self.assertIn("Seedream generated 1 image item", result.tools[0].summary)

    def test_fake_runtime_tool_failure_bubbles_up(self) -> None:
        """工具执行失败时异常应继续向上抛出。"""

        loop = AgentLoop(
            model=None,
            tool_registry=build_default_tool_registry(),
            runtime=_FakeFailureRuntime(),
        )

        with patch(
            "src.tool.seedream_image.generate_seedream_image",
            side_effect=RuntimeError("seedream boom"),
        ):
            with self.assertRaisesRegex(RuntimeError, "seedream boom"):
                loop.run_once(
                    "draw a skyline",
                    system_prompt="You are a helpful image agent.",
                )

    def test_only_named_tool_subset_is_exposed(self) -> None:
        """未显式暴露的工具不应进入当前主脑回合。"""

        hidden_called = {"value": False}

        def _hidden_handler(_context: ToolContext) -> ToolResult:
            hidden_called["value"] = True
            return ToolResult(content="hidden", summary="hidden")

        registry = ToolRegistry()
        for tool_spec in build_default_tool_registry().list_tools():
            registry.register(tool_spec)
        registry.register(
            ToolSpec(
                name="hidden_tool",
                description="A hidden tool for boundary verification.",
                display_name="Hidden Tool",
                input_schema={"type": "object", "properties": {}},
                handler=_hidden_handler,
            )
        )
        runtime = _FakeCaptureRuntime()
        loop = AgentLoop(
            model=None,
            tool_registry=registry,
            runtime=runtime,
        )

        result = loop.run_once(
            "draw a skyline",
            system_prompt="You are a helpful image agent.",
            tool_names=["generate_seedream_image"],
        )

        self.assertEqual(result.text, "captured")
        self.assertEqual(runtime.seen_tool_names, ["generate_seedream_image"])
        self.assertFalse(hidden_called["value"])


if __name__ == "__main__":
    unittest.main()
