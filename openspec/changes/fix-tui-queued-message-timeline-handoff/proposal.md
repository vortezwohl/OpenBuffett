## Why

当前 TUI 把排队消息同时建模为“已进入 timeline 的用户消息”和“queue tray 中的待处理提交”，只是通过渲染层把 `queue_state == "queued"` 的用户项隐藏起来。这样会导致排队消息在正式发出时并没有新增一条 `User >` 会话记录，而只是把一条旧的隐藏项重新显示出来；从用户视角看，消息会先从 queue tray 消失，却没有在主 timeline 底部留下明确的发送留痕。

这个问题已经直接影响会话时间线的真实性与可理解性。现在需要把“待发消息”和“已正式进入本轮处理的消息”拆成两种清晰语义，避免继续依赖隐藏/解隐藏的折中建模。

## What Changes

- 调整 TUI 队列消息的状态模型，让排队中的用户提交只存在于 queue tray，而不提前写入主 timeline。
- 调整 turn 启动时机的 timeline 落盘语义：消息正式开始执行时，才追加对应的 `User >` 会话项。
- 清理依赖 `queue_state == "queued"` 隐藏 timeline 用户项的渲染逻辑，避免旧消息“复活式出现”。
- 为队列推进、失败后续跑、取消后续跑等场景补充回归测试，验证用户消息会在正确时刻、正确顺序进入 timeline。

## Capabilities

### New Capabilities
- `tui-queued-message-timeline-handoff`: 定义排队消息从 queue tray 进入正式会话时间线时的可见性、落盘时机与顺序要求。

### Modified Capabilities
- 无

## Impact

- 受影响代码：`src/tui/app.py`
- 受影响测试：`test/test_tui_app.py`
- 受影响系统：TUI turn queue、timeline 渲染、queue tray 渲染与相关本地状态流
