## Why

当前 SmartIPO TUI 在纵向高度变化时能够正常收缩，但窗口横向缩窄后会留下旧边框残影和错位线段，界面表现接近“崩掉”，这说明现有布局和重绘策略没有把宽度变化当成一等场景处理。

同时，TUI 目前仍继承了 Textual 的主题切换入口，用户可以通过命令面板或内建 action 改变主题，导致界面视觉基线不稳定。本次需要把主题收敛到固定的 `ansi-dark`，让布局、颜色和后续视觉调优都建立在单一受控前提上。

## What Changes

- 让 TUI 在窗口横向缩窄和再次放大时都能稳定重排与重绘，不出现旧宽度残留边框、断裂线段或内容区域错位。
- 收敛主布局容器的宽度与表面绘制策略，确保状态栏、timeline、queue tray 和输入区始终以当前可用宽度为准响应式收缩。
- 把应用主题默认值显式固定为 `ansi-dark`，避免依赖 Textual 默认主题或宿主状态。
- 移除或禁用用户可触发的主题切换入口，包括命令面板中的主题命令以及相关主题切换 action，使运行中的 TUI 不再允许用户改色。
- 补充 TUI 测试，覆盖横向 resize 后的布局稳定性，以及主题固定与不可切换的行为约束。

## Capabilities

### New Capabilities
- `tui-horizontal-resize-stability`: 定义 TUI 在终端宽度变化时必须稳定重排和重绘，不得出现宽度收缩后的视觉残影或布局错位。
- `tui-fixed-ansi-dark-theme`: 定义 TUI 必须默认使用 `ansi-dark`，且不得向用户暴露运行时主题切换能力。

### Modified Capabilities
- None.

## Impact

- 受影响代码主要位于 `src/tui/app.py` 的 CSS、布局容器、挂载生命周期和主题相关 App 行为覆写。
- 如主题默认值在入口层显式设置，也可能影响 `src/tui/__main__.py` 的应用初始化方式。
- 需要更新 `test/test_tui_app.py`，加入终端宽度变化、主题命令可见性和主题 action 锁定的验证。
- 不引入新依赖，不改变 EasyHarness 事件协议，不扩展多主题配置体系。
