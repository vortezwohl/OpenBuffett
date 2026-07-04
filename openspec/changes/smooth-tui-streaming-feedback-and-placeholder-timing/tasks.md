## 1. 显示层状态与 turn 收尾改造

- [x] 1.1 在 `src/tui/app.py` 中新增显示层调度状态，显式建模 reveal backlog、placeholder 延迟回放队列、`raw_stream_done` 与显示层排空判定
- [x] 1.2 把 `thinking` 与 `assistant` 文本事件改造为先入显示层 reveal 通道再进入可见时间线，而不是收到整块 delta 后直接整块追加
- [x] 1.3 调整 turn 收尾逻辑，确保只有在原始事件流结束且显示层 backlog 已排空后才真正执行 `_complete_turn` / `_finish_active_turn`

## 2. Placeholder 缓冲与刷新节拍

- [x] 2.1 为本地 `Thinking ...` placeholder 增加 `50ms` 最短可见时长，并在阈值内缓存首个会覆盖 placeholder 的真实事件
- [x] 2.2 实现 placeholder 覆盖事件的有序回放与动作结束后的 waiting feedback 回补，避免出现无活动也无 placeholder 的空窗
- [x] 2.3 把全局运行中刷新间隔改为 `10ms`，并把 thinking 动画帧间隔改为 `100ms`，同时用该刷新节拍驱动 reveal 消费与延迟回放检查

## 3. 文本规范化与回归验证

- [x] 3.1 为 preserved thinking history 增加 `\r` / `\n` 净化逻辑，确保运行时 thinking 文本进入时间线前已被规范化
- [x] 3.2 在 `test/test_tui_app.py` 中补充 `thinking` / `assistant` 逐字符 reveal 与“显示层未排空时 turn 不得提前结束”的测试
- [x] 3.3 在 `test/test_tui_app.py` 中补充 placeholder 最短可见 `50ms`、延迟覆盖顺序、全局 `10ms` 刷新和 `100ms` thinking 动画的测试
- [x] 3.4 运行 `.\.venv\Scripts\python.exe -m unittest test.test_tui_app`，确认新时序逻辑没有破坏现有时间线行为
