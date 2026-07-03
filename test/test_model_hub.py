"""EasyHarness 模型装配测试。

该文件验证项目集中模型配置会被解析为 `easyharness.ModelConfig`，并继续
保留环境变量解析与采样参数覆写保护。
"""

from __future__ import annotations

import unittest
from unittest.mock import patch

from easyharness import ModelConfig

from src.model_config import AGENT_SESSION_ROUND, BRAIN_MODEL_CONFIGS, CHANNEL_CONFIGS
from src.service.model_hub import create_default_brain_model, validate_model_config


class ModelHubTests(unittest.TestCase):
    """验证 EasyHarness ModelConfig 装配规则。"""

    def test_default_brain_model_comes_from_model_config(self) -> None:
        """默认主脑模型必须来自集中配置。"""

        config = BRAIN_MODEL_CONFIGS[AGENT_SESSION_ROUND]
        channel = CHANNEL_CONFIGS[config.channel]

        with patch.dict(
            "os.environ",
            {
                "API_KEY": "test-key",
                "API_BASE": "https://example.com/v1",
            },
            clear=False,
        ):
            validate_model_config()
            model = create_default_brain_model()

        self.assertIsInstance(model, ModelConfig)
        self.assertEqual(model.model, f"{channel.provider}/{config.model}")
        self.assertEqual(model.api_key, "test-key")
        self.assertEqual(model.base_url, "https://example.com/v1")
        self.assertEqual(model.temperature, config.temperature)
        self.assertEqual(model.top_p, config.top_p)
        self.assertEqual(model.seed, config.seed)

    def test_sampling_overrides_are_rejected(self) -> None:
        """调用点不得直接覆写集中采样参数。"""

        with patch.dict("os.environ", {"API_KEY": "test-key"}, clear=False):
            with self.assertRaisesRegex(RuntimeError, "主脑采样参数必须来自"):
                create_default_brain_model(temperature=0.01)

    def test_missing_api_key_fails_fast(self) -> None:
        """缺少 API key 时必须显式失败。"""

        with patch.dict("os.environ", {"API_KEY": ""}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "API_KEY 未配置"):
                create_default_brain_model()


if __name__ == "__main__":
    unittest.main()
