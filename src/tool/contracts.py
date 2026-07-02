"""主脑工具契约定义。

该文件提供项目内工具暴露给 strands 运行时所需的最小静态描述和调用
上下文。它刻意保持简单，不引入插件协议、权限系统或多层抽象。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(slots=True)
class ToolContext:
    """描述一次工具调用可用的共享上下文。

    Args:
        services: 共享服务对象字典。
        llm: 可选文本模型调用器。
    """

    services: dict[str, Any] = field(default_factory=dict)
    llm: Any | None = None

    def resolve_service(self, name: str, default: Any = None) -> Any:
        """按名称读取共享服务对象。

        Args:
            name: 服务名。
            default: 未找到时返回的默认值。

        Returns:
            命中的服务对象或默认值。
        """

        return self.services.get(name, default)


@dataclass(slots=True)
class ToolResult:
    """描述一次工具调用的规范化结果。

    Args:
        content: 原始结果内容。
        summary: 主脑可直接消费的摘要文本。
        metadata: 附加元数据。
    """

    content: Any
    summary: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ToolSpec:
    """描述一个可暴露给主脑的业务工具。

    Args:
        name: 工具名。
        description: 工具职责说明。
        display_name: 面向人类的显示名。
        input_schema: strands tool 输入 schema。
        handler: 实际执行业务逻辑的处理函数。
    """

    name: str
    description: str
    display_name: str
    input_schema: dict[str, Any]
    handler: Callable[..., ToolResult]
