## Why

当前 TUI 的流式反馈还有三个直接可见的问题：运行时 `thinking` 文本会把 `\r` / `\n` 原样带进时间线，`thinking` 与最终回复会按整块 delta 跳动式更新，本地 `Thinking ...` 占位又可能在首个真实事件到来时瞬间消失。与此同时，刷新节拍、占位生命周期和 turn 完成时机并未统一建模，导致用户容易把“还在显示层排队的内容”误判为卡死或闪烁。

这轮需要把显示层行为正式收口成可验证协议，尤其要纳入新增硬约束：全局屏幕刷新间隔统一为 `10ms`，thinking 动画帧间隔改为 `100ms`。

## What Changes

- 为运行时 `thinking` 历史文本增加显示层规范化，禁止把任何 `\n` 或 `\r` 直接渲染到时间线中。
- 为 `thinking` 和最终 `assistant` 回复引入有序逐字符显示通道，收到 token 后按固定 `10ms/char` 节拍顺滑吐出，而不是整块 delta 直接跳变。
- 为 turn 内本地 `Thinking ...` 占位增加最短可见时长 `50ms`，在该窗口内到达的首个真实动作需要延后覆盖，而不是立刻把占位抹掉。
- 统一 turn 内显示层完成判定：只要仍有待回放事件、待吐出字符或待提交终态，turn 就不得提前结束，也不得让 waiting placeholder 无故消失。
- 把全局屏幕刷新间隔固定为 `10ms`，并把 thinking `.` / `..` / `...` 动画帧间隔固定为 `100ms`。

## Capabilities

### New Capabilities
- `tui-streaming-text-reveal-pacing`: 规定 `thinking` 与 `assistant` 流式文本的顺序缓冲、逐字符显示节拍和 turn 结束前排空规则。
- `tui-turn-wait-feedback-buffering`: 规定本地 `Thinking ...` 占位的最短可见时长、真实事件的延后覆盖规则和空窗回补规则。
- `tui-runtime-refresh-cadence`: 规定运行中时间线的全局刷新间隔与 thinking 动画节拍。

### Modified Capabilities
- `tui-thinking-history-visual-treatment`: 补充 preserved thinking history 的文本净化要求，禁止把运行时 `thinking` 中的 `\r` / `\n` 原样显示到时间线。

## Impact

- 受影响模块：`src/tui/app.py` 的事件消费、显示层缓冲、turn 完成判定、thinking placeholder 生命周期与动画刷新逻辑；`test/test_tui_app.py` 的时间线回归测试与节拍测试。
- 受影响行为：`thinking` 历史文本展示、`assistant` 与 `thinking` 的流式输出节奏、placeholder 首帧可见性、turn 内等待反馈、刷新与动画频率。
- 非目标模块：`src/agent.py`、EasyHarness 事件协议、工具真实耗时来源、OpenSpec 以外的业务逻辑。
