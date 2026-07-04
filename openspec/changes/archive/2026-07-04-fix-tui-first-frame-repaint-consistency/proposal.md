## Why

当前 SmartIPO TUI 在首次打开时会出现与 resize 后不同的界面表面：正常首帧存在横向暗条和未完整刷新的面板内部，而拉宽再拉回后反而得到另一种更完整的渲染结果。这说明问题不只是“横向缩放时会坏”，而是“首帧渲染路径和 resize 后重绘路径不一致”。

这个问题需要单独修正，因为当前已有的 resize 修复与主题锁定虽然改变了宽度收缩行为，却没有保证首次打开和后续重绘共享同一渲染契约。只有先统一首帧和 resize 的刷新路径，后续 TUI 的视觉调优才有稳定基线。

## What Changes

- 重新定义 TUI 的首帧渲染与 resize 后重绘关系，要求首次打开、拉宽、再拉回之后看到的是同一套界面表面和边框结果。
- 把挂载后的首次绘制与终端尺寸变化后的重绘收敛到统一刷新路径，避免一条路径先写 `Static` 内容、另一条路径再做完整 repaint。
- 调整 TUI 局部刷新时机，避免在首轮布局尚未稳定时就提前写入状态栏、timeline 和 queue tray，导致首帧脏画面。
- 补充一致性回归测试，覆盖“首次打开”和“resize 往返后”关键区域结果等价，而不是只验证宽度数值发生变化。

## Capabilities

### New Capabilities
- `tui-first-frame-render-consistency`: 定义 TUI 首次打开时的界面表面必须与 resize 往返后的稳定结果保持一致，不得出现仅首帧可见的脏画面或暗条。
- `tui-unified-repaint-lifecycle`: 定义 mount 与 resize 必须共享统一的完整重排/重绘路径，避免首帧和后续 repaint 走不同生命周期。

### Modified Capabilities
- None.

## Impact

- 受影响代码主要位于 `src/tui/app.py` 的 `on_mount()`、`on_resize()`、局部刷新调度和可能新增的统一 repaint helper。
- 需要更新 `test/test_tui_app.py`，把当前只测“缩宽后还能看”的断言扩展为“首帧与 resize 往返结果一致”的回归用例。
- 不引入新依赖，不改变 EasyHarness 事件流、TUI 主题锁定要求或聊天消息语义。
