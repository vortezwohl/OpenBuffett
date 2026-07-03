"""Textual 本地工作台入口。

该包只导出 TUI 应用对象。默认 agent 装配位于 `src.agent`，UI 层只消费
已装配好的 EasyHarness agent，不重新定义运行时入口。
"""

from src.tui.app import AgentWorkbenchApp

__all__ = ["AgentWorkbenchApp"]
