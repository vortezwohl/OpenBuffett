## 1. 队列状态模型收敛

- [x] 1.1 调整 `src/tui/app.py` 的 `_PendingTurn` 与 `_enqueue_turn()`，让排队阶段不再提前创建 user timeline 项
- [x] 1.2 清理 `_visible_timeline_items()` 中基于 `queue_state == "queued"` 隐藏 user 项的旧逻辑，并确认 queue tray 只从 `_pending_turns` 渲染

## 2. 正式发出时的 timeline handoff

- [x] 2.1 调整 `_start_next_turn_if_idle()`，在 turn 成为 active 时追加新的 `User >` timeline 项并绑定到 active turn
- [x] 2.2 调整 `_finish_active_turn()`、失败收尾和取消收尾路径，使其只更新已正式进入 timeline 的 active turn user 项
- [x] 2.3 复查 waiting placeholder、assistant/tool 事件与新 user handoff 顺序，确保后续活动始终出现在对应 `User >` 之后

## 3. 回归测试

- [x] 3.1 更新 `test/test_tui_app.py`，覆盖排队消息在 queued 阶段只出现在 queue tray、不出现在 timeline 的行为
- [x] 3.2 增加 handoff 场景测试，验证前一轮结束后下一条消息会以新的 `User >` 追加到 timeline 底部
- [x] 3.3 增加失败续跑和取消续跑测试，验证下一条 queued 消息不会消失且顺序正确
