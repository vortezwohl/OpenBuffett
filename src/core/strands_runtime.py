"""Strands 运行时薄桥接层。

该文件负责把项目内 `ToolSpec` 包成 strands 可调用工具，并把 strands
的单轮执行结果整理成项目内统一结构，避免业务层直接依赖框架细节。
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any

from strands import Agent, tool

from src.tool.contracts import ToolContext, ToolResult, ToolSpec


@dataclass(slots=True)
class StrandsToolSummary:
    """描述一条已执行工具的最小摘要。

    Args:
        name: 工具名。
        summary: 用户可读摘要。
        metadata: 工具附加元数据。
    """

    name: str
    summary: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StrandsRunResult:
    """描述一次主脑回合的最小结果。

    Args:
        text: 模型最终文本回复。
        tools: 本轮已执行工具摘要列表。
        error: 运行时主动返回的错误文本。
    """

    text: str = ""
    tools: list[StrandsToolSummary] = field(default_factory=list)
    error: str = ""


class StrandsRuntime:
    """执行单轮 strands agent 调用。"""

    requires_model = True

    def __init__(self, *, agent_factory: Any = Agent) -> None:
        """初始化运行时。

        Args:
            agent_factory: 可注入的 Agent 构造器，便于测试替身接管。
        """

        self._agent_factory = agent_factory

    def run(
        self,
        prompt: str,
        *,
        model: Any,
        tools: list[Any],
        system_prompt: str,
    ) -> StrandsRunResult:
        """执行一轮主脑调用并返回统一结果。

        Args:
            prompt: 本轮用户输入。
            model: strands 主脑模型。
            tools: 已包装好的 strands tools。
            system_prompt: 本轮系统提示词。

        Returns:
            统一的项目内运行结果。
        """

        agent = self._agent_factory(
            model=model,
            tools=tools,
            system_prompt=system_prompt,
        )
        result = agent(prompt)
        return StrandsRunResult(text=str(result).strip())


def build_tool_context(
    *,
    services: dict[str, Any] | None = None,
    llm: Any | None = None,
) -> ToolContext:
    """构造一份共享给工具调用的最小上下文。

    Args:
        services: 共享服务对象字典。
        llm: 可选文本模型调用器。

    Returns:
        工具处理函数可复用的调用上下文。
    """

    return ToolContext(
        services=services or {},
        llm=llm,
    )


def build_strands_tool(
    *,
    tool_spec: ToolSpec,
    services: dict[str, Any] | None = None,
    llm: Any | None = None,
    executed_tools: list[StrandsToolSummary] | None = None,
):
    """把一个项目内 `ToolSpec` 包装为 strands tool。

    Args:
        tool_spec: 项目内工具描述。
        services: 透传给工具上下文的服务对象。
        llm: 透传给工具上下文的文本模型调用器。
        executed_tools: 本轮已执行工具摘要收集器。

    Returns:
        strands 可直接使用的工具对象。
    """

    def _call(**kwargs):
        context = build_tool_context(
            services=services,
            llm=llm,
        )
        result = tool_spec.handler(context, **kwargs)
        if executed_tools is not None:
            executed_tools.append(
                StrandsToolSummary(
                    name=tool_spec.name,
                    summary=result.summary,
                    metadata=result.metadata,
                )
            )
        return _serialize_tool_result(result)

    return tool(
        _call,
        name=tool_spec.name,
        description=tool_spec.description,
        inputSchema=tool_spec.input_schema,
    )


def _serialize_tool_result(result: ToolResult) -> str:
    """把工具结果整理为主脑可读文本。"""

    if result.summary:
        return result.summary
    if isinstance(result.content, str):
        return result.content
    return json.dumps(result.content, ensure_ascii=False, default=str)
