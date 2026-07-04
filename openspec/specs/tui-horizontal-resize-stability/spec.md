# tui-horizontal-resize-stability Specification

## Purpose
TBD - created by archiving change fix-tui-horizontal-resize-and-lock-theme. Update Purpose after archive.
## Requirements
### Requirement: TUI 必须在终端宽度变化后稳定重排与重绘
SmartIPO TUI MUST 在终端窗口横向缩窄或再次放大后，按新的可用宽度重新布局和重绘各主区域，不得保留旧宽度下的边框残影、断裂线段或错位内容。

#### Scenario: 终端宽度缩窄后主区域按新宽度重排
- **WHEN** 已经渲染出状态栏、timeline、queue tray 或输入区的 TUI 终端宽度变小
- **THEN** 系统 MUST 让这些区域按照新的可用宽度重新布局
- **AND** timeline 中已有消息 MUST 继续可见且可读

#### Scenario: 终端宽度恢复后界面仍保持一致
- **WHEN** TUI 在缩窄后再次被放宽
- **THEN** 系统 MUST 继续按当前宽度重新布局各主区域
- **AND** 系统 MUST NOT 留下前一次宽度下的边框或线段残影

### Requirement: 带边框区域必须拥有可预测的表面绘制契约
SmartIPO TUI MUST 让承担边框展示的主区域使用一致且可预测的表面绘制策略，确保宽度变化后旧边框被新的界面表面完整覆盖。

#### Scenario: 主界面表面覆盖旧边框绘制区域
- **WHEN** 状态栏、timeline、queue tray 或输入区在旧宽度下已经绘制过边框
- **THEN** 它们在新宽度下 MUST 使用当前界面表面重新覆盖和重绘对应区域
- **AND** 系统 MUST NOT 依赖未定义的透明背景来清除旧边框

