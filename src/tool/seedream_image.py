"""Seedream 生图工具包装。

该文件把现有 `Seedream` 生图能力包装成 strands 主脑可调用的业务工具，
自身不重复实现生图逻辑，只负责参数接线和结果整理。
"""

from __future__ import annotations

from src.ext.seedream import generate_seedream_image
from src.tool.contracts import ToolContext, ToolResult, ToolSpec


def run(
    _context: ToolContext,
    *,
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
) -> ToolResult:
    """执行一次 Seedream 生图工具调用。

    Args:
        _context: 统一工具上下文；当前工具不依赖额外服务。
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
        规范化的工具结果。
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
    return ToolResult(
        content={
            "model": result.model,
            "prompt": result.prompt,
            "images": result.images,
            "response_payload": result.response_payload,
        },
        summary=summary,
        metadata={
            "model": result.model,
            "image_count": len(result.images),
            "response_format": response_format,
        },
    )


TOOL_SPEC = ToolSpec(
    name="generate_seedream_image",
    description=(
        "Generate images with Seedream. Use this when the user wants a new image "
        "or image variation and you need the SmartIPO image generation backend."
    ),
    display_name="Seedream Image",
    input_schema={
        "type": "object",
        "properties": {
            "prompt": {"type": "string", "description": "Image generation prompt."},
            "image": {
                "type": "string",
                "description": "Optional reference image as URL, data URL, or base64.",
            },
            "model": {"type": "string", "description": "Optional model override."},
            "size": {"type": "string", "description": "Optional output size."},
            "n": {
                "type": "integer",
                "description": "Number of images to generate.",
                "minimum": 1,
            },
            "seed": {"type": "integer", "description": "Optional random seed."},
            "guidance_scale": {
                "type": "number",
                "description": "Optional prompt guidance strength.",
            },
            "watermark": {
                "type": "boolean",
                "description": "Whether to add a watermark.",
            },
            "response_format": {
                "type": "string",
                "enum": ["url", "b64_json"],
                "description": "Preferred image response format.",
            },
            "user": {
                "type": "string",
                "description": "Optional business user identifier.",
            },
        },
        "required": ["prompt"],
    },
    handler=run,
)
