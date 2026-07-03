"""Textual 本地工作台入口。

该包只导出 TUI 应用对象。默认 agent 装配位于 `src.app`，避免 UI 包重新
暴露运行时工厂或形成第二个装配入口。
"""

from src.tui.app import AgentWorkbenchApp

__all__ = ["AgentWorkbenchApp"]
