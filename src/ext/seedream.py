"""Seedream 生图能力封装。

该文件用于对接火山方舟兼容 OpenAI 风格的图片生成接口，提供一个最小
可用的 Seedream 生图实现。当前职责聚焦于：
1. 解析调用所需的 API Key、Base URL 与模型名；
2. 向图片生成接口发起请求；
3. 直接返回豆包接口返回的 `url` 或 `b64_json` 数据，交由上层自行消费。

调用方应优先通过显式参数传入鉴权信息；若未传入，则会从常见环境变量中
按顺序兜底读取。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests


DEFAULT_ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
DEFAULT_SEEDREAM_MODEL = "doubao-seedream-5-0-260128"
DEFAULT_IMAGE_SIZE = "1920x1920"
DEFAULT_TIMEOUT_SECONDS = 120


@dataclass(slots=True)
class SeedreamImageResult:
    """描述一次生图调用的主要输出。

    Args:
        model: 本次请求使用的模型名。
        prompt: 本次请求的提示词。
        images: 接口返回的图片结果项列表，每项至少包含 `url` 或 `b64_json`。
        response_payload: 图片生成接口返回的原始 JSON 数据。
    """

    model: str
    prompt: str
    images: list[dict[str, Any]]
    response_payload: dict[str, Any]


class SeedreamClient:
    """提供最小可用的 Seedream 生图能力。

    该客户端默认对接火山方舟 `images/generations` 接口，并直接返回接口
    响应中的图片地址或 Base64 内容。

    Args:
        api_key: 火山方舟 API Key。为空时会从环境变量中兜底读取。
        api_base: 图片生成接口基础地址。默认使用火山方舟北京区域地址。
        model: 默认使用的 Seedream 模型名。
        timeout: HTTP 请求超时时间，单位为秒。
    """

    def __init__(
        self,
        api_key: str = "",
        api_base: str = "",
        model: str = DEFAULT_SEEDREAM_MODEL,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        """初始化 Seedream 客户端。"""
        self._api_key = api_key.strip() or self._resolve_api_key()
        self._api_base = (api_base.strip() or self._resolve_api_base()).rstrip("/")
        self._model = model
        self._timeout = timeout
        self._session = requests.Session()

    @property
    def image_generation_url(self) -> str:
        """返回图片生成接口地址。"""
        return f"{self._api_base}/images/generations"

    def generate(
        self,
        prompt: str,
        *,
        image: str = "",
        model: str = "",
        size: str = DEFAULT_IMAGE_SIZE,
        n: int = 1,
        seed: int | None = None,
        guidance_scale: float | None = None,
        watermark: bool | None = None,
        response_format: str = "url",
        user: str = "",
    ) -> SeedreamImageResult:
        """执行一次 Seedream 生图并直接返回接口结果。

        Args:
            prompt: 生图提示词，不能为空。
            image: 可选参考图，支持图片 URL、Data URL 或纯 Base64 图片内容。
            model: 可选的模型覆盖值；为空时使用客户端默认模型。
            size: 输出尺寸，例如 `1024x1024`。
            n: 生成图片数量。
            seed: 可选随机种子。
            guidance_scale: 可选提示词遵循强度。
            watermark: 是否添加水印。传 `None` 时不向接口显式传该字段。
            response_format: 首选返回格式，通常使用 `url`。
            user: 可选的业务侧用户标识。

        Returns:
            包含图片结果项和原始响应的结果对象。

        Raises:
            ValueError: 当输入参数非法或接口响应缺少图片内容时抛出。
            RuntimeError: 当未配置 API Key 时抛出。
            requests.HTTPError: 当接口调用失败时抛出。
        """
        normalized_prompt = prompt.strip()
        if not normalized_prompt:
            raise ValueError("prompt 不能为空。")
        if n < 1:
            raise ValueError("n 必须大于等于 1。")
        if response_format not in {"url", "b64_json"}:
            raise ValueError("response_format 仅支持 'url' 或 'b64_json'。")
        if not self._api_key:
            raise RuntimeError("未找到 Seedream API Key，请显式传入或配置环境变量。")

        payload = self._build_payload(
            prompt=normalized_prompt,
            image=image,
            model=model or self._model,
            size=size,
            n=n,
            seed=seed,
            guidance_scale=guidance_scale,
            watermark=watermark,
            response_format=response_format,
            user=user,
        )
        response = self._session.post(
            self.image_generation_url,
            headers=self._build_headers(),
            json=payload,
            timeout=self._timeout,
        )
        response.raise_for_status()
        response_payload = response.json()
        images = self._extract_images(response_payload=response_payload)
        return SeedreamImageResult(
            model=payload["model"],
            prompt=normalized_prompt,
            images=images,
            response_payload=response_payload,
        )

    def _build_headers(self) -> dict[str, str]:
        """构造调用火山方舟接口所需的请求头。"""
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _build_payload(
        self,
        *,
        prompt: str,
        image: str,
        model: str,
        size: str,
        n: int,
        seed: int | None,
        guidance_scale: float | None,
        watermark: bool | None,
        response_format: str,
        user: str,
    ) -> dict[str, Any]:
        """仅组装本次生图请求体，便于单独校验。"""
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "n": n,
            "response_format": response_format,
        }
        normalized_image = self._normalize_image(image)
        if normalized_image:
            payload["image"] = normalized_image
        if seed is not None:
            payload["seed"] = seed
        if guidance_scale is not None:
            payload["guidance_scale"] = guidance_scale
        if watermark is not None:
            payload["watermark"] = watermark
        if user.strip():
            payload["user"] = user.strip()
        return payload

    def _extract_images(
        self,
        *,
        response_payload: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """提取接口响应中的图片结果项。"""
        data_items = response_payload.get("data")
        if not isinstance(data_items, list) or not data_items:
            raise ValueError("图片生成接口返回中缺少 data 列表。")
        images: list[dict[str, Any]] = []
        for item in data_items:
            if not isinstance(item, dict):
                raise ValueError("图片生成接口返回的 data 项结构非法。")
            if not item.get("b64_json") and not item.get("url"):
                raise ValueError("图片生成接口返回项中既没有 url，也没有 b64_json。")
            images.append(item)
        return images

    @staticmethod
    def _normalize_image(image: str) -> str:
        """把图生图输入统一整理为豆包接口可接受的图片字段。

        支持三种输入：
        1. `http://` 或 `https://` 开头的图片 URL；
        2. 已经带 `data:image/...;base64,` 前缀的 Data URL；
        3. 不带前缀的纯 Base64 图片内容，此时默认补成 `data:image/png;base64,`。
        """
        normalized_image = image.strip()
        if not normalized_image:
            return ""
        if normalized_image.startswith(("http://", "https://")):
            return normalized_image
        if normalized_image.startswith("data:image/"):
            return normalized_image
        return f"data:image/png;base64,{normalized_image}"

    @staticmethod
    def _resolve_api_key() -> str:
        """按常见命名顺序解析 Seedream/火山方舟鉴权信息。

        优先读取更具语义性的专用环境变量，避免误用项目中其他模型提供方的
        通用 `API_KEY`。但若项目本身已经约定了统一的 `API_KEY`，则仍允许
        作为最后兜底项使用。
        """
        for env_name in (
            "SEEDREAM_API_KEY",
            "ARK_API_KEY",
            "VOLCENGINE_ARK_API_KEY",
            "DOUBAO_API_KEY",
        ):
            env_value = os.getenv(env_name, "").strip()
            if env_value:
                return env_value
        return ""

    @staticmethod
    def _resolve_api_base() -> str:
        """按常见命名顺序解析图片生成接口基础地址。"""
        for env_name in (
            "SEEDREAM_API_BASE",
            "ARK_API_BASE",
            "VOLCENGINE_ARK_API_BASE",
            "DOUBAO_API_BASE",
        ):
            env_value = os.getenv(env_name, "").strip()
            if env_value:
                return env_value
        return DEFAULT_ARK_BASE_URL


def generate_seedream_image(
    prompt: str,
    *,
    image: str = "",
    api_key: str = "",
    api_base: str = "",
    model: str = DEFAULT_SEEDREAM_MODEL,
    size: str = DEFAULT_IMAGE_SIZE,
    n: int = 1,
    seed: int | None = None,
    guidance_scale: float | None = None,
    watermark: bool | None = False,
    response_format: str = "url",
    user: str = "",
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> SeedreamImageResult:
    """以函数形式暴露最小生图入口，便于直接调用。

    Args:
        prompt: 生图提示词。
        image: 可选参考图，支持图片 URL、Data URL 或纯 Base64 图片内容。
        api_key: 火山方舟 API Key。
        api_base: 图片生成接口基础地址。
        model: Seedream 模型名。
        size: 输出尺寸。
        n: 生成张数。
        seed: 随机种子。
        guidance_scale: 提示词遵循强度，也可理解为文本权重。值越大，模型自由度越小，
            与提示词的一致性越强。根据火山方舟官方 API Explorer，取值范围为
            `[1, 10]`；其中 `doubao-seedream-3.0-t2i` 默认值为 `2.5`，
            `doubao-seededit-3.0-i2i` 默认值为 `5.5`。该参数并非所有模型都支持，
            官方说明明确 `doubao-seedream-5.0-lite/4.5/4.0` 不支持，调用前应结合
            当前模型能力确认。
        watermark: 是否添加水印。
        response_format: 返回格式，支持 `url` 与 `b64_json`。
        user: 业务用户标识。
        timeout: HTTP 超时时间。

    Returns:
        生图结果对象，包含接口直接返回的图片结果项列表。
    """
    client = SeedreamClient(
        api_key=api_key,
        api_base=api_base,
        model=model,
        timeout=timeout,
    )
    return client.generate(
        prompt,
        image=image,
        size=size,
        n=n,
        seed=seed,
        guidance_scale=guidance_scale,
        watermark=watermark,
        response_format=response_format,
        user=user,
    )
