"""默认模型配置最小回归测试。

该文件验证 SmartIPO 不再通过旧模型装配层或多调用点配置表装配模型，
而是由 `src.agent` 直接构造 EasyHarness `ModelConfig`。
"""

from __future__ import annotations

import unittest
from unittest.mock import patch

from easyharness import Agent, ModelConfig

from src.agent import build_default_agent, build_default_model_config


class DefaultModelConfigTests(unittest.TestCase):
    """验证默认模型配置的最小行为。"""

    def test_default_model_config_uses_environment_values(self) -> None:
        """默认模型配置应读取环境变量并返回 ModelConfig。"""

        with patch.dict(
            "os.environ",
            {
                "API_KEY": "test-key",
                "API_BASE": "https://example.com/v1",
            },
            clear=False,
        ):
            model = build_default_model_config()

        self.assertIsInstance(model, ModelConfig)
        self.assertEqual(model.model, "openai/deepseek-v4-flash")
        self.assertEqual(model.api_key, "test-key")
        self.assertEqual(model.base_url, "https://example.com/v1")

    def test_missing_api_key_fails_fast(self) -> None:
        """缺少 API key 时必须在默认模型配置阶段失败。"""

        with patch.dict("os.environ", {"API_KEY": ""}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "API_KEY 未配置"):
                build_default_model_config()

    def test_default_agent_does_not_expose_sampling_overrides(self) -> None:
        """默认 agent 装配入口不接受临时采样参数覆写。"""

        names = build_default_agent.__code__.co_varnames

        self.assertNotIn("temperature", names)
        self.assertNotIn("top_p", names)
        self.assertNotIn("seed", names)

    def test_default_agent_factory_returns_easyharness_agent(self) -> None:
        """默认 agent 工厂应直接返回 EasyHarness Agent。"""

        with patch.dict("os.environ", {"API_KEY": "test-key"}, clear=False):
            agent = build_default_agent(".")

        self.assertIsInstance(agent, Agent)


if __name__ == "__main__":
    unittest.main()
