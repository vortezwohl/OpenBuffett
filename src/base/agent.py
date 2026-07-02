"""Strands 主脑模型装配入口。

该文件负责把项目现有的 provider/model/api 配置装配为 strands 可用的
`LiteLLMModel`。它只服务带 tool-call 语义的主脑运行时，避免把这类职责
继续塞进 `Text2Text`。
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from strands.models.litellm import LiteLLMModel

from src.base.llm import LLM

load_dotenv()


class AgentModel(LLM):
    """封装 strands 主脑模型所需的最小配置。

    Args:
        provider: LiteLLM provider 名称，例如 `openai`。
        model_name: 模型名。
        api_key: 显式传入的 API Key。为空时会读取 `dotenv` 加载后的环境变量。
        api_base: 显式传入的 API Base。为空时会读取 `dotenv` 加载后的环境变量。
    """

    def build_model(
        self,
        *,
        temperature: float = 1.0,
        top_p: float = 1.0,
        seed: int | None = 42,
    ) -> LiteLLMModel:
        """构造一个绑定采样参数的 `LiteLLMModel`。

        Args:
            temperature: 采样温度。
            top_p: nucleus sampling 参数。
            seed: 随机种子；为空时不显式传递。

        Returns:
            strands 可直接使用的 `LiteLLMModel`。
        """

        params: dict[str, float | int] = {
            "temperature": temperature,
            "top_p": top_p,
        }
        if seed is not None:
            params["seed"] = seed
        return LiteLLMModel(
            model_id=self.endpoint,
            client_args={
                "api_key": self._resolve_api_key(),
                "api_base": self._resolve_api_base(),
            },
            params=params,
        )

    def _resolve_api_key(self) -> str:
        """解析主脑模型 API Key。

        默认从 `dotenv` 加载后的环境变量中读取；若显式传入则优先使用显式值。
        """

        return self._api_key.strip() or os.getenv("API_KEY", "").strip() or os.getenv(
            "OPENAI_API_KEY",
            "",
        ).strip()

    def _resolve_api_base(self) -> str:
        """解析主脑模型 API Base。

        默认从 `dotenv` 加载后的环境变量中读取；若显式传入则优先使用显式值。
        """

        return (
            self._api_base.strip()
            or os.getenv("API_BASE", "").strip()
            or os.getenv("OPENAI_API_BASE", "").strip()
        )


def build_litellm_model(
    *,
    provider: str,
    model_name: str,
    api_key: str = "",
    api_base: str = "",
    temperature: float = 1.0,
    top_p: float = 1.0,
    seed: int | None = 42,
) -> LiteLLMModel:
    """以函数形式返回 strands 主脑模型。

    Args:
        provider: LiteLLM provider 名称。
        model_name: 模型名。
        api_key: 显式传入的 API Key。
        api_base: 显式传入的 API Base。
        temperature: 采样温度。
        top_p: nucleus sampling 参数。
        seed: 随机种子。

    Returns:
        strands 可直接使用的 `LiteLLMModel`。
    """

    return AgentModel(
        provider=provider,
        model_name=model_name,
        api_key=api_key,
        api_base=api_base,
    ).build_model(
        temperature=temperature,
        top_p=top_p,
        seed=seed,
    )
