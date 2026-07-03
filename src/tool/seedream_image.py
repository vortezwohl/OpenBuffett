"""Seedream 生图 EasyHarness 工具。

该文件把现有 `Seedream` 生图能力包装成 EasyHarness 可调用的业务工具。
它不重复实现生图逻辑，只负责声明工具合同、连接参数和整理 `ToolOutput`，
不再依赖项目自研工具合同、结果包装或工具注册表。
"""

from __future__ import annotations

from easyharness import ToolOutput, tool

from src.ext.seedream import generate_seedream_image


@tool(
    name="generate_seedream_image",
    purpose="Generate new images or image variations with the SmartIPO Seedream backend.",
    when_to_use=(
        "Use this when the user needs a newly generated image from a text prompt, "
        "or an image variation from an optional reference image."
    ),
    parameters={
        "prompt": "Main image generation prompt.",
        "image": "Optional reference image as a URL, data URL, or base64 payload.",
        "model": "Optional backend model override.",
        "size": "Optional output size override.",
        "n": "Number of images to generate.",
        "seed": "Optional random seed for reproducibility.",
        "guidance_scale": "Optional prompt guidance strength.",
        "watermark": "Whether to add a watermark.",
        "response_format": "Preferred response format. Use url or b64_json.",
        "user": "Optional business user identifier.",
    },
    returns=(
        "A normalized image generation payload including the model, echoed prompt, "
        "generated image items, and raw backend response payload."
    ),
    common_failures=(
        "Backend request failure: the upstream image generation service is unavailable or rejects the request.",
        "Invalid input: the prompt, reference image, or requested response format is not accepted by the backend.",
    ),
)
def run(
    prompt: str,
    image: str = "",
    model: str = "",
    size: str = "",
    n: int = 1,
    seed: int | None = None,
    guidance_scale: float | None = None,
    watermark: bool | None = False,
    response_format: str = "url",
    user: str = "",
) -> ToolOutput:
    """执行一次 Seedream 生图工具调用。

    Args:
        prompt: 生图提示词。
        image: 可选参考图。
        model: 可选模型覆盖值。
        size: 输出尺寸；为空时沿用底层默认值。
        n: 生成张数。
        seed: 随机种子。
        guidance_scale: 提示词遵循强度。
        watermark: 是否添加水印。
        response_format: 返回格式。
        user: 业务用户标识。

    Returns:
        EasyHarness 可消费的结构化工具结果。
    """

    kwargs = {
        "image": image,
        "n": n,
        "seed": seed,
        "guidance_scale": guidance_scale,
        "watermark": watermark,
        "response_format": response_format,
        "user": user,
    }
    if model.strip():
        kwargs["model"] = model.strip()
    if size.strip():
        kwargs["size"] = size.strip()
    result = generate_seedream_image(
        prompt,
        **kwargs,
    )
    summary = (
        f"Seedream generated {len(result.images)} image item(s) "
        f"with model {result.model}."
    )
    content = {
        "model": result.model,
        "prompt": result.prompt,
        "images": result.images,
        "response_payload": result.response_payload,
        "image_count": len(result.images),
        "response_format": response_format,
    }
    return ToolOutput(
        data=content,
        model_text=summary,
        preview=summary,
        detail=summary,
    )


SEEDREAM_IMAGE_TOOL = run
