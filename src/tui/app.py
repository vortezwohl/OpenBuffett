"""基于 Textual 的 EasyHarness 本地 agent 工作台。

该文件只负责界面层：接收用户输入、消费 `easyharness.AgentEvent` 流、
维护本地展示态并渲染单列会话记录。运行时、工具合同和事件事实来源均由
EasyHarness 提供，本文件不得重新定义跨 UI 共享的 runtime 或 timeline 协议。
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from easyharness import AgentEvent
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.text import Text
from textual import work
from textual.app import App, ComposeResult, ScreenStackError
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.widgets import Footer, Header, Input, Static

from src.agent import build_default_agent

_TIMELINE_REFRESH_INTERVAL_SECONDS = 0.05
_THINKING_ANIMATION_FRAME_MS = 150


@dataclass(slots=True)
class _TimelineItem:
    """TUI 本地展示项，不作为跨层运行时合同导出。"""

    key: str
    kind: str
    title: str
    body: str = ""
    status: str = "completed"
    name: str = ""
    preview: str = ""
    detail: str = ""
    started_at: datetime | None = None
    duration_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class _PendingTurn:
    """描述一条待执行或正在执行的用户提交。"""

    turn_id: str
    prompt: str
    user_item_key: str


class AgentWorkbenchApp(App[None]):
    """运行 SmartIPO EasyHarness agent 的单列本地工作台。"""

    CSS = """
    Screen {
        layout: vertical;
        color: white;
    }

    #body {
        height: 1fr;
        padding: 0 1;
    }

    #status-banner {
        height: auto;
        padding: 0 1;
        color: white;
        border: round #d8ffe0;
    }

    #timeline-scroll {
        height: 1fr;
        border: round #d8ffe0;
        color: white;
        padding: 0 1;
    }

    #timeline-view {
        width: 1fr;
        height: auto;
    }

    #queue-tray {
        height: auto;
        margin-top: 1;
        padding: 0 1;
        color: white;
        border: round #effff1;
    }

    #chat-input {
        margin-top: 1;
        color: white;
        border: round #effff1;
    }
    """

    BINDINGS = [
        Binding("ctrl+n", "new_session", "新会话"),
    ]

    def __init__(self, *, agent: Any | None = None) -> None:
        """初始化工作台。

        Args:
            agent: 可选 EasyHarness agent 兼容对象；测试可注入假对象。
        """

        super().__init__()
        self._agent = agent or build_default_agent()
        self._items: list[_TimelineItem] = []
        self._item_counter = 0
        self._turn_count = 0
        self._turn_serial = 0
        self._status_message = "工作台已就绪。"
        self._active_by_kind: dict[str, str] = {}
        self._active_tools: dict[str, str] = {}
        self._pending_turns: deque[_PendingTurn] = deque()
        self._active_turn: _PendingTurn | None = None

    def compose(self) -> ComposeResult:
        """构建 TUI 布局。"""

        yield Header()
        with Vertical(id="body"):
            yield Static(id="status-banner")
            with VerticalScroll(id="timeline-scroll"):
                yield Static(id="timeline-view")
            yield Static(id="queue-tray")
            yield Input(
                placeholder="SmartIPO 在线为你解答 ...",
                id="chat-input",
            )
        yield Footer()

    def on_mount(self) -> None:
        """挂载后刷新界面并启动本地运行态计时。"""

        self._refresh_view(force_follow=True)
        self.set_interval(
            _TIMELINE_REFRESH_INTERVAL_SECONDS,
            self._refresh_running_items,
        )
        self.call_after_refresh(self._focus_chat_input)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """把输入框内容提交给 EasyHarness agent。"""

        prompt = event.value.strip()
        event.input.value = ""
        if not prompt:
            return
        self._enqueue_turn(prompt)
        self._start_next_turn_if_idle()
        self._refresh_view(force_follow=True)

    def action_new_session(self) -> None:
        """清空界面并重置当前 EasyHarness 会话。"""

        reset = getattr(self._agent, "reset", None)
        if callable(reset):
            reset()
        self._items = []
        self._item_counter = 0
        self._turn_count = 0
        self._active_by_kind.clear()
        self._active_tools.clear()
        self._pending_turns.clear()
        self._active_turn = None
        self._status_message = "已创建新会话。"
        self._refresh_view()

    @work(thread=True, group="agent", exit_on_error=False)
    def _run_turn_worker(self, turn_id: str, prompt: str) -> None:
        """在后台线程中执行一轮流式会话。"""

        try:
            for event in self._agent.stream(prompt):
                self.call_from_thread(self._apply_agent_event_for_turn, turn_id, event)
            self.call_from_thread(self._complete_turn, turn_id)
        except Exception as error:  # pragma: no cover
            self.call_from_thread(self._show_error, turn_id, f"处理失败: {error}")

    def _apply_agent_event_for_turn(self, turn_id: str, event: AgentEvent) -> None:
        """仅当事件属于当前活跃轮次时，才把它应用到本地展示态。"""

        if not self._is_active_turn(turn_id):
            return
        self._apply_agent_event(event)

    def _apply_agent_event(self, event: AgentEvent) -> None:
        """把 EasyHarness 事件应用到 TUI 本地展示态。"""

        if event.kind != "thinking":
            self._finalize_provisional_thinking()
        if event.kind == "thinking":
            self._apply_thinking_event(event)
        elif event.kind == "tool":
            self._apply_tool_event(event)
        elif event.kind == "assistant":
            self._apply_assistant_event(event)
        elif event.kind == "system":
            self._apply_system_event(event)
        elif event.kind == "compress":
            self._apply_compress_event(event)
        self._status_message = self._format_event_status(event)
        self._refresh_view(force_follow=True)

    def _apply_thinking_event(self, event: AgentEvent) -> None:
        if event.status == "started":
            item = self._get_active_thinking_item()
            if item is None:
                self._active_by_kind["thinking"] = self._append_item(
                    kind="thinking",
                    title="thinking",
                    body=event.text or "",
                    status="started",
                    started_at=self._parse_started_at(event.started_at),
                )
                return
            item.status = "started"
            if event.text:
                item.body = event.text
            item.metadata["provisional"] = False
            return
        item = self._get_active_thinking_item()
        if item is None:
            return
        if event.status == "delta" and event.text:
            item.body += event.text
            item.metadata["provisional"] = False
            return
        if event.status in {"completed", "failed"}:
            self._sync_running_item_duration(item)
            if event.text:
                item.body = event.text
            item.status = event.status
            item.duration_ms = max(item.duration_ms, event.duration_ms or 0)
            item.started_at = None
            item.metadata["provisional"] = False
            self._active_by_kind.pop("thinking", None)

    def _apply_tool_event(self, event: AgentEvent) -> None:
        tool_key = self._tool_event_key(event)
        if event.status == "started":
            self._active_tools[tool_key] = self._append_item(
                kind="tool",
                title="",
                body="",
                name=event.name or "tool",
                status="started",
                started_at=self._parse_started_at(event.started_at),
                metadata=self._event_data_dict(event),
            )
            return
        item = self._get_item(self._active_tools.get(tool_key, ""))
        if item is None:
            key = self._append_item(
                kind="tool",
                title="",
                body="",
                name=event.name or "tool",
                status=event.status,
                metadata=self._event_data_dict(event),
            )
            item = self._get_item(key)
        if item is None:
            return
        item.status = event.status
        item.duration_ms = event.duration_ms or item.duration_ms
        item.started_at = None
        item.metadata.update(self._event_data_dict(event))
        output = self._extract_tool_output(event)
        item.preview = output.get("preview") or event.text or item.preview
        item.detail = output.get("detail") or output.get("model_text") or item.detail
        if event.text and not item.preview:
            item.preview = event.text
        if event.status in {"completed", "failed"}:
            self._active_tools.pop(tool_key, None)

    def _apply_assistant_event(self, event: AgentEvent) -> None:
        if event.status == "started":
            self._active_by_kind["assistant"] = self._append_item(
                kind="assistant",
                title="🤖",
                status="started",
                started_at=self._parse_started_at(event.started_at),
            )
            return
        item = self._get_item(self._active_by_kind.get("assistant", ""))
        if item is None and event.text:
            key = self._append_item(
                kind="assistant",
                title="🤖",
                body="",
                status=event.status,
                started_at=self._parse_started_at(event.started_at),
            )
            item = self._get_item(key)
            self._active_by_kind["assistant"] = key
        if item is None:
            return
        if event.status == "delta" and event.text:
            item.body += event.text
            return
        if event.status in {"completed", "failed"}:
            if event.text:
                item.body = event.text
            item.status = event.status
            item.duration_ms = event.duration_ms or item.duration_ms
            item.started_at = None
            self._active_by_kind.pop("assistant", None)

    def _apply_system_event(self, event: AgentEvent) -> None:
        self._append_item(
            kind="system",
            title="SmartIPO",
            body=event.text or "",
            status=event.status,
            started_at=self._parse_started_at(event.started_at),
            duration_ms=event.duration_ms or 0,
            metadata=self._event_data_dict(event),
        )

    def _apply_compress_event(self, event: AgentEvent) -> None:
        self._append_item(
            kind="compress",
            title="SmartIPO",
            body=event.text or "",
            status=event.status,
            started_at=self._parse_started_at(event.started_at),
            duration_ms=event.duration_ms or 0,
            metadata=self._event_data_dict(event),
        )

    def _complete_turn(self, turn_id: str) -> None:
        """标记一轮流式会话自然完成。"""

        if not self._is_active_turn(turn_id):
            return
        self._settle_running_turn_items("completed")
        self._finalize_provisional_thinking()
        self._turn_count += 1
        self._finish_active_turn(queue_state="completed", status_message="回复完成。")

    def _show_error(self, turn_id: str, message: str) -> None:
        """在本地展示态中追加错误消息。"""

        if not self._is_active_turn(turn_id):
            return
        self._settle_running_turn_items("failed", message=message)
        self._finalize_provisional_thinking()
        self._append_item(
            kind="system",
            title="SmartIPO",
            body=message,
            status="failed",
        )
        self._turn_count += 1
        self._finish_active_turn(queue_state="failed", status_message=message)

    def _append_user_message(
        self,
        content: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """追加用户消息条目，可附带队列状态元数据。"""

        return self._append_item(
            kind="user",
            title="👨‍💻",
            body=content,
            metadata=metadata,
        )

    def _start_local_thinking(self) -> None:
        """在收到真实事件前先启动本地 thinking 占位与计时。"""

        if self._get_active_thinking_item() is not None:
            return
        self._active_by_kind["thinking"] = self._append_item(
            kind="thinking",
            title="thinking",
            status="started",
            started_at=datetime.now(timezone.utc),
            metadata={"provisional": True},
        )

    def _finalize_provisional_thinking(self) -> None:
        """当真实输出已开始时，收口仅用于等待态展示的本地 thinking。"""

        item = self._get_active_thinking_item()
        if item is None or not item.metadata.get("provisional", False):
            return
        self._sync_running_item_duration(item)
        item.status = "completed"
        item.started_at = None
        item.metadata["provisional"] = False
        self._active_by_kind.pop("thinking", None)

    def _enqueue_turn(self, prompt: str) -> None:
        """把一条用户提交加入本地执行队列。"""

        turn_id = self._next_turn_id()
        user_item_key = self._append_user_message(
            prompt,
            metadata={
                "turn_id": turn_id,
                "queue_state": "queued",
                "queue_position": 0,
            },
        )
        self._pending_turns.append(
            _PendingTurn(
                turn_id=turn_id,
                prompt=prompt,
                user_item_key=user_item_key,
            )
        )
        self._refresh_turn_queue_metadata()

    def _start_next_turn_if_idle(self) -> None:
        """若当前没有活跃轮次，则启动队首消息。"""

        if self._active_turn is not None or not self._pending_turns:
            return
        turn = self._pending_turns.popleft()
        self._active_turn = turn
        self._refresh_turn_queue_metadata()
        self._start_local_thinking()
        self._status_message = "正在处理排队消息。"
        self._refresh_view(force_follow=True)
        self._run_turn_worker(turn.turn_id, turn.prompt)

    def _finish_active_turn(self, *, queue_state: str, status_message: str) -> None:
        """收尾当前活跃轮次，并在可能时启动下一条。"""

        if self._active_turn is None:
            return
        item = self._get_item(self._active_turn.user_item_key)
        if item is not None:
            item.metadata["queue_state"] = queue_state
            item.metadata["queue_position"] = None
            item.status = "failed" if queue_state == "failed" else "completed"
        self._active_turn = None
        self._refresh_turn_queue_metadata()
        self._status_message = status_message
        self._refresh_view(force_follow=True)
        self._start_next_turn_if_idle()

    def _refresh_turn_queue_metadata(self) -> None:
        """同步当前活跃条目与待处理条目的队列状态。"""

        if self._active_turn is not None:
            active_item = self._get_item(self._active_turn.user_item_key)
            if active_item is not None:
                active_item.metadata["queue_state"] = "running"
                active_item.metadata["queue_position"] = 0
        for index, turn in enumerate(self._pending_turns, start=1):
            item = self._get_item(turn.user_item_key)
            if item is None:
                continue
            item.metadata["queue_state"] = "queued"
            item.metadata["queue_position"] = index
            item.status = "completed"

    def _settle_running_turn_items(self, status: str, *, message: str = "") -> None:
        """收口当前仍处于 started 的展示项，避免失败后残留运行态。"""

        for key in list(self._active_by_kind.values()):
            item = self._get_item(key)
            if item is None or item.started_at is None:
                continue
            self._sync_running_item_duration(item)
            item.status = status
            item.started_at = None
        self._active_by_kind.clear()
        for key in list(self._active_tools.values()):
            item = self._get_item(key)
            if item is None:
                continue
            self._sync_running_item_duration(item)
            item.status = status
            item.started_at = None
            if message and "error" not in item.metadata:
                item.metadata["error"] = message
        self._active_tools.clear()

    def _is_active_turn(self, turn_id: str) -> bool:
        """判断某个 turn_id 是否仍对应当前活跃轮次。"""

        return self._active_turn is not None and self._active_turn.turn_id == turn_id

    def _next_turn_id(self) -> str:
        """生成当前会话内唯一的轮次编号。"""

        self._turn_serial += 1
        return f"turn-{self._turn_serial}"

    def _append_item(
        self,
        *,
        kind: str,
        title: str,
        body: str = "",
        status: str = "completed",
        name: str = "",
        preview: str = "",
        detail: str = "",
        started_at: datetime | None = None,
        duration_ms: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        self._item_counter += 1
        key = f"{kind}-{self._item_counter}"
        self._items.append(
            _TimelineItem(
                key=key,
                kind=kind,
                title=title,
                body=body,
                status=status,
                name=name,
                preview=preview,
                detail=detail,
                started_at=started_at,
                duration_ms=duration_ms,
                metadata=metadata or {},
            )
        )
        return key

    def _get_item(self, key: str) -> _TimelineItem | None:
        for item in self._items:
            if item.key == key:
                return item
        return None

    def _get_active_thinking_item(self) -> _TimelineItem | None:
        """返回当前仍处于活动中的 thinking 条目。"""

        key = self._active_by_kind.get("thinking", "")
        if not key:
            return None
        return self._get_item(key)

    @staticmethod
    def _sync_running_item_duration(item: _TimelineItem) -> None:
        """用当前 UTC 时间刷新单个运行中条目的本地耗时。"""

        if item.started_at is None:
            return
        duration_ms = int(
            (datetime.now(timezone.utc) - item.started_at).total_seconds() * 1000
        )
        item.duration_ms = max(0, duration_ms)

    def _refresh_running_items(self) -> None:
        """刷新仍处于 started 状态的本地展示时长。"""

        changed = False
        now = datetime.now(timezone.utc)
        for item in self._items:
            if item.started_at is None:
                continue
            duration_ms = int((now - item.started_at).total_seconds() * 1000)
            duration_ms = max(0, duration_ms)
            if duration_ms != item.duration_ms:
                item.duration_ms = duration_ms
                changed = True
        if changed:
            self._render_timeline()

    def _refresh_view(self, *, force_follow: bool = False) -> None:
        """刷新顶部状态和会话记录。"""

        try:
            self.query_one("#status-banner", Static).update(
                Text(self._render_status_banner())
            )
        except (NoMatches, ScreenStackError):
            return
        self._render_timeline(force_follow=force_follow)
        self._render_queue_tray()

    def _render_timeline(self, *, force_follow: bool = False) -> None:
        """刷新主会话记录区域。"""

        try:
            timeline_widget = self.query_one("#timeline-view", Static)
            scroll_widget = self.query_one("#timeline-scroll", VerticalScroll)
        except (NoMatches, ScreenStackError):
            return
        should_follow = force_follow or self._should_follow_scroll(scroll_widget)
        timeline_widget.update(Text(self._render_timeline_text()))
        if should_follow:
            self.call_after_refresh(
                scroll_widget.scroll_end,
                animate=False,
                force=True,
                immediate=True,
            )

    def _render_queue_tray(self) -> None:
        """刷新待处理消息托盘。"""

        try:
            queue_widget = self.query_one("#queue-tray", Static)
        except (NoMatches, ScreenStackError):
            return
        queue_widget.display = bool(self._pending_turns)
        queue_widget.update(self._render_queue_tray_renderable())

    def _render_status_banner(self) -> str:
        """渲染顶部状态摘要。"""

        return (
            "SmartIPO\n"
            f"已完成 {self._turn_count} 轮\n"
            f"{self._status_message}"
        )

    def _render_timeline_text(self) -> str:
        """把本地展示项渲染为文本。"""

        visible_items = [
            item
            for item in self._items
            if not (
                item.kind == "user"
                and str(item.metadata.get("queue_state", "")).strip() == "queued"
            )
        ]
        if not visible_items:
            return "还没有消息。"
        return "\n\n".join(self._format_timeline_item(item) for item in visible_items)

    def _render_queue_tray_text(self) -> str:
        """把待处理队列渲染为纯文本，便于测试验证。"""

        if not self._pending_turns:
            return ""
        return "\n".join(turn.prompt for turn in self._pending_turns)

    def _render_queue_tray_renderable(self) -> object:
        """把待处理队列渲染为居中泡泡。"""

        if not self._pending_turns:
            return Text("")
        bubbles = [
            Align.center(
                Panel.fit(
                    Text(turn.prompt, style="bold white"),
                    border_style="#effff1",
                    padding=(0, 1),
                )
            )
            for turn in self._pending_turns
        ]
        return Group(*bubbles)

    def _format_timeline_item(self, item: _TimelineItem) -> str:
        if item.kind in {"user", "assistant", "system", "compress"}:
            return self._format_message_item(item)
        if item.kind == "thinking":
            return f"{self._format_duration(item.duration_ms)} · 思考 {self._thinking_label(item)}"
        return self._format_tool_item(item)

    def _format_message_item(self, item: _TimelineItem) -> str:
        if item.kind == "user":
            return self._format_user_item(item)
        if item.kind == "assistant":
            return self._format_assistant_item(item)
        if item.status == "failed":
            return f"{item.title} · {item.body}"
        return f"{item.title} · {item.body}"

    @staticmethod
    def _format_user_item(item: _TimelineItem) -> str:
        """按队列状态渲染用户消息。"""

        return f"{item.title} {item.body}"

    @staticmethod
    def _format_assistant_item(item: _TimelineItem) -> str:
        """按聊天风格渲染助手消息。"""

        return f"{item.title} {item.body}"

    def _format_tool_item(self, item: _TimelineItem) -> str:
        lines = [
            f"工具 {item.name or 'tool'} · {self._format_status_label(item.status)} · {self._format_duration(item.duration_ms)}"
        ]
        tool_use_id = self._tool_use_id_from_metadata(item.metadata)
        if tool_use_id:
            lines.append(f"调用 {tool_use_id}")
        error = str(item.metadata.get("error", "")).strip()
        if item.status == "failed" and not error:
            error = item.preview or item.body
        if error:
            lines.append(f"错误 {error}")
        if item.preview:
            lines.append(f"概要 {item.preview}")
        if item.detail and item.detail != item.preview:
            lines.append(f"结果 {item.detail}")
        return "\n".join(lines)

    def _focus_chat_input(self) -> None:
        """让输入框在启动后获得焦点。"""

        self.query_one("#chat-input", Input).focus()

    @staticmethod
    def _format_status_label(status: str) -> str:
        if status == "started":
            return "进行中"
        if status == "delta":
            return "更新中"
        if status == "failed":
            return "失败"
        return "完成"

    @staticmethod
    def _format_duration(duration_ms: int) -> str:
        return f"{duration_ms / 1000:.2f}s"

    @staticmethod
    def _thinking_label(item: _TimelineItem) -> str:
        body = item.body.strip()
        if item.status != "started":
            return body or "thinking"
        cycle = (item.duration_ms // _THINKING_ANIMATION_FRAME_MS) % 3
        suffix = (".", "..", "...")[cycle]
        if body:
            return body
        return suffix

    @staticmethod
    def _parse_started_at(value: str | None) -> datetime | None:
        if not value:
            return datetime.now(timezone.utc)
        try:
            normalized = value.replace("Z", "+00:00")
            return datetime.fromisoformat(normalized)
        except ValueError:
            return datetime.now(timezone.utc)

    @staticmethod
    def _event_data_dict(event: AgentEvent) -> dict[str, Any]:
        if isinstance(event.data, dict):
            return dict(event.data)
        if event.data is None:
            return {}
        return {"data": event.data}

    @staticmethod
    def _extract_tool_output(event: AgentEvent) -> dict[str, Any]:
        data = AgentWorkbenchApp._event_data_dict(event)
        output = data.get("output")
        if isinstance(output, dict):
            return {
                "preview": str(output.get("preview") or "").strip(),
                "detail": str(output.get("detail") or "").strip(),
                "model_text": str(output.get("model_text") or "").strip(),
            }
        return {}

    @staticmethod
    def _tool_event_key(event: AgentEvent) -> str:
        data = AgentWorkbenchApp._event_data_dict(event)
        tool_use_id = str(data.get("tool_use_id", "")).strip()
        return tool_use_id or event.name or "tool"

    @staticmethod
    def _tool_use_id_from_metadata(metadata: dict[str, Any]) -> str:
        return str(metadata.get("tool_use_id", "")).strip()

    @staticmethod
    def _format_event_status(event: AgentEvent) -> str:
        if event.kind == "thinking":
            if event.status == "started":
                return "SmartIPO 正在思考"
            if event.status == "failed":
                return event.text or "思考没有完成"
            return "思考完成"
        if event.kind == "assistant":
            if event.status == "started":
                return "SmartIPO 正在组织回复"
            if event.status == "delta":
                return "SmartIPO 正在组织回复"
            if event.status == "failed":
                return event.text or "回复没有完成"
            return "回复完成"
        if event.kind == "tool":
            name = event.name or "tool"
            if event.status == "started":
                return f"正在调用 {name}"
            if event.status == "failed":
                return f"{name} 调用失败"
            return f"{name} 调用完成"
        if event.kind == "compress":
            return "上下文已整理"
        return event.text or "系统消息"

    @staticmethod
    def _should_follow_scroll(scroll_widget: VerticalScroll) -> bool:
        """仅当用户靠近底部时才自动跟随。"""

        return (scroll_widget.max_scroll_y - scroll_widget.scroll_y) <= 2
