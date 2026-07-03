"""EasyHarness 事件流驱动的 Textual 工作台测试。

该文件验证 TUI 只消费 `easyharness.AgentEvent`，并在展示层本地维护
thinking、tool、assistant 和 system 的渲染状态，不再依赖项目私有事件流。
"""

from __future__ import annotations

import time
import unittest

from easyharness import AgentEvent
from textual.widgets import Input

from src.tui.app import AgentWorkbenchApp


class _FakeStreamingAgent:
    """用于驱动 TUI 测试的 EasyHarness agent 兼容假对象。"""

    def __init__(self, events: list[AgentEvent]) -> None:
        self.events = events
        self.reset_count = 0
        self.prompts: list[str] = []

    def stream(self, prompt: str):
        """按顺序返回预设事件。"""

        self.prompts.append(prompt)
        yield from self.events

    def reset(self) -> None:
        """记录重置次数。"""

        self.reset_count += 1


def _started_event(kind: str, *, name: str | None = None) -> AgentEvent:
    """构造 started 阶段测试事件。"""

    return AgentEvent(kind=kind, status="started", name=name)


class AgentWorkbenchAppTests(unittest.IsolatedAsyncioTestCase):
    """验证 Textual 工作台的 EasyHarness 事件流闭环。"""

    async def test_submit_task_renders_agent_event_stream(self) -> None:
        """提交任务后应按 AgentEvent 流展示用户、工具和 assistant 输出。"""

        agent = _FakeStreamingAgent(
            [
                _started_event("thinking"),
                _started_event("tool", name="fileglide_read_text"),
                AgentEvent(
                    kind="tool",
                    status="completed",
                    name="fileglide_read_text",
                    duration_ms=12,
                    data={
                        "tool_use_id": "tool-1",
                        "output": {
                            "preview": "fileglide_read_text: README.md",
                            "detail": "README.md\nline 2\nline 3",
                        },
                    },
                ),
                _started_event("assistant"),
                AgentEvent(kind="assistant", status="delta", text="已"),
                AgentEvent(kind="assistant", status="delta", text="完成"),
                AgentEvent(kind="assistant", status="completed", text="已完成"),
            ]
        )
        app = AgentWorkbenchApp(agent=agent)

        async with app.run_test() as pilot:
            input_widget = app.query_one("#chat-input", Input)
            input_widget.value = "整理 README"
            fake_event = type(
                "FakeSubmittedEvent",
                (),
                {"input": input_widget, "value": "整理 README"},
            )()
            app.on_input_submitted(fake_event)
            await pilot.pause(0.35)
            text = app._render_timeline_text()

        self.assertEqual(agent.prompts, ["整理 README"])
        self.assertIn("你: 整理 README", text)
        self.assertIn("fileglide_read_text", text)
        self.assertIn("调用: tool-1", text)
        self.assertIn("概要: fileglide_read_text: README.md", text)
        self.assertIn("结果: README.md", text)
        self.assertIn("AI: 已完成", text)

    async def test_failed_tool_event_is_visible(self) -> None:
        """工具失败事件必须在 TUI 中明确展示为失败。"""

        agent = _FakeStreamingAgent(
            [
                _started_event("tool", name="fileglide_edit_text"),
                AgentEvent(
                    kind="tool",
                    status="failed",
                    name="fileglide_edit_text",
                    duration_ms=3,
                    text="permission denied",
                    data={"tool_use_id": "tool-2", "error": "permission denied"},
                ),
            ]
        )
        app = AgentWorkbenchApp(agent=agent)

        async with app.run_test() as pilot:
            input_widget = app.query_one("#chat-input", Input)
            fake_event = type(
                "FakeSubmittedEvent",
                (),
                {"input": input_widget, "value": "写文件"},
            )()
            app.on_input_submitted(fake_event)
            await pilot.pause(0.35)
            text = app._render_timeline_text()

        self.assertIn("fileglide_edit_text | 失败", text)
        self.assertIn("错误: permission denied", text)

    async def test_system_failure_is_rendered(self) -> None:
        """系统失败事件应进入本地展示态。"""

        agent = _FakeStreamingAgent(
            [AgentEvent(kind="system", status="failed", text="模型调用失败")]
        )
        app = AgentWorkbenchApp(agent=agent)

        async with app.run_test() as pilot:
            input_widget = app.query_one("#chat-input", Input)
            fake_event = type(
                "FakeSubmittedEvent",
                (),
                {"input": input_widget, "value": "你好"},
            )()
            app.on_input_submitted(fake_event)
            await pilot.pause(0.35)
            text = app._render_timeline_text()

        self.assertIn("系统 [失败]: 模型调用失败", text)

    def test_running_thinking_entry_renders_local_animation(self) -> None:
        """thinking started 条目应以本地动画渲染。"""

        app = AgentWorkbenchApp(agent=_FakeStreamingAgent([]))
        app._append_user_message("你好")
        app._apply_agent_event(_started_event("thinking"))
        thinking_entry = app._items[-1]
        thinking_entry.duration_ms = 800

        text = app._render_timeline_text()

        self.assertIn("0.80s | AI: thinking ...", text)

    def test_new_session_resets_agent_and_local_state(self) -> None:
        """新会话应同时重置 agent 和 TUI 本地展示态。"""

        agent = _FakeStreamingAgent([])
        app = AgentWorkbenchApp(agent=agent)
        app._append_user_message("旧消息")

        app.action_new_session()

        self.assertEqual(agent.reset_count, 1)
        self.assertEqual(app._turn_count, 0)
        self.assertEqual(app._render_timeline_text(), "还没有消息。")


if __name__ == "__main__":
    unittest.main()
