"""默认 EasyHarness agent 装配入口。

该文件承担应用 composition 层职责：定义默认 system prompt、默认工具集、
默认模型和默认 agent 组装。TUI、future WebUI 等界面层只消费这里提供的
装配结果，不再在 UI 内部定义底层协议和默认运行栈。
"""

from __future__ import annotations

import os

from easyharness import Agent
from easyharness.toolset import build_fileglide_tools

from src.service.model_hub import create_default_brain_model
from src.tool.seedream_image import SEEDREAM_IMAGE_TOOL


DEFAULT_SYSTEM_PROMPT = """
你是 SmartIPO 的本地 coding agent。
- 接到任务后要按可验证的小步骤推进，直到任务自然结束或明确遇到阻塞。
- 使用 EasyHarness 提供的 fileglide 工具完成本地文件读取、搜索、编辑、移动和检查。
- 文件修改前先读取必要上下文，避免无根据猜测。
- 工具失败时直接暴露失败原因，不要伪装成成功。
- 默认使用中文简体回答用户；工具合同和底层事件语义由 EasyHarness 负责。
""".strip()

DEFAULT_FILEGLIDE_TOOL_NAMES = (
    "fileglide_list_tree",
    "fileglide_search_paths",
    "fileglide_read_text",
    "fileglide_search_text",
    "fileglide_edit_text",
    "fileglide_manage_paths",
    "fileglide_inspect_path",
)

DEFAULT_BUSINESS_TOOL_NAMES = (
    "generate_seedream_image",
)

DEFAULT_WORKBENCH_TOOL_NAMES = (
    *DEFAULT_FILEGLIDE_TOOL_NAMES,
    *DEFAULT_BUSINESS_TOOL_NAMES,
)


def build_default_tools(workspace_root: str | None = None) -> list[object]:
    """构造默认 EasyHarness 工具对象集合。

    Args:
        workspace_root: 默认文件工具作用域根目录；为空时使用当前工作目录。

    Returns:
        可直接传入 `easyharness.Agent` 的工具对象列表。
    """

    root = workspace_root or os.getcwd()
    return [
        *build_fileglide_tools(default_root=root),
        SEEDREAM_IMAGE_TOOL,
    ]


def build_default_agent(workspace_root: str | None = None) -> Agent:
    """构造默认 EasyHarness 本地 agent。"""

    return Agent(
        model=create_default_brain_model(),
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        tools=build_default_tools(workspace_root),
        enable_fileglide=False,
    )
