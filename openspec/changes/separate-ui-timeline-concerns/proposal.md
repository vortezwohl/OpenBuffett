## Why

当前会话时间线把一部分 UI 展示决策下沉到了 core：底层会拼接工具标题、展示名和提示文案。这让 core 和 TUI/WebUI 的职责边界变脏，也让后续 UI 扩展继续被底层实现牵着走。

同时，TUI 里的工具执行过程虽然已经有事件流，但用户仍然可能看不到运行中的工具条目和计时，尤其是快速工具。现在需要把语义状态和视觉表现重新拆开，并补齐 TUI 对工具活动的可见性保证。

## What Changes

- **BREAKING** 调整会话时间线语义边界：core 只保留原始工具名、工具类别、状态、时长和结果数据，不再在底层拼接展示标题、展示名或提示文案。
- **BREAKING** 调整 strands runtime 发出的工具事件载荷，去掉仅服务于 UI 的展示层字段和文案，保留 UI 必需的原始语义数据。
- 为 TUI 增加明确的工具活动可见性规则：工具开始时立即进入聊天时间线并开始计时，工具完成时展示结果概要；过快完成的工具也必须让用户看见至少一次运行中状态。
- 补充针对 core 时间线语义和 TUI 运行中工具可见性的测试，避免后续回退。

## Capabilities

### New Capabilities
- `conversation-timeline-boundaries`: 规范跨 UI 时间线状态层只输出原始语义数据，不直接承担展示文本拼接。
- `workbench-tool-activity-visibility`: 规范 Textual workbench 必须在工具执行过程中展示运行中条目、计时和完成结果。

### Modified Capabilities
- 无

## Impact

- Affected code:
  - `src/core/strands_runtime.py`
  - `src/core/timeline.py`
  - `src/tui/app.py`
  - `test/test_strands_runtime.py`
  - `test/test_timeline.py`
  - `test/test_tui_app.py`
- APIs:
  - `LoopEvent.payload` 的工具事件字段会发生破坏性调整
  - `ConversationTimeline` 输出条目的字段语义会收紧为原始状态模型
- Systems:
  - Textual workbench
  - 后续 WebUI 可复用的 timeline state
