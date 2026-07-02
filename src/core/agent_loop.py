"""最小单轮主脑运行入口。

该文件只负责一个事情：把主脑模型、运行时和已注册工具装配成一次
strands agent 调用。它不承担多阶段业务状态机、会话持久化或前端协作。
"""

from __future__ import annotations

from typing import Any

from src.core.strands_runtime import StrandsRunResult, StrandsRuntime, build_strands_tool
from src.tool.registry import ToolRegistry


class AgentLoop:
    """执行单轮主脑调用的最小运行时。

    Args:
        model: strands 主脑模型；若运行时声明不需要模型，可传 `None`。
        tool_registry: 项目内工具注册表。
        runtime: 具体运行时；为空时使用默认 `StrandsRuntime`。
        services: 共享服务对象字典，会透传到 tool context。
        llm: 可选的文本模型调用器，供工具按需复用。
    """

    def __init__(
        self,
        *,
        model: Any,
        tool_registry: ToolRegistry,
        runtime: Any | None = None,
        services: dict[str, Any] | None = None,
        llm: Any | None = None,
    ) -> None:
        self._model = model
        self._tool_registry = tool_registry
        self._runtime = runtime or StrandsRuntime()
        self._services = services or {}
        self._llm = llm

    def run_once(
        self,
        prompt: str,
        *,
        system_prompt: str = "",
        tool_names: list[str] | tuple[str, ...] | None = None,
        services: dict[str, Any] | None = None,
    ) -> StrandsRunResult:
        """执行一轮最小 strands agent 调用。

        Args:
            prompt: 本轮用户输入。
            system_prompt: 本轮系统提示词。
            tool_names: 本轮要暴露的工具名子集；为空时暴露全部已注册工具。
            services: 本轮临时覆盖或追加的服务对象。

        Returns:
            统一的项目内运行结果。

        Raises:
            RuntimeError: 当运行时要求模型但未提供时抛出。
        """

        if getattr(self._runtime, "requires_model", True) and self._model is None:
            raise RuntimeError("AgentLoop requires a model when runtime.requires_model is true.")
        combined_services = {**self._services, **(services or {})}
        available_specs = self._tool_registry.list_tools(*(tool_names or ()))
        executed_tools = []
        tools = [
            build_strands_tool(
                tool_spec=tool_spec,
                services=combined_services,
                llm=self._llm,
                executed_tools=executed_tools,
            )
            for tool_spec in available_specs
        ]
        result = self._runtime.run(
            prompt,
            model=self._model,
            tools=tools,
            system_prompt=system_prompt,
        )
        if executed_tools and not result.tools:
            result.tools = list(executed_tools)
        return result
