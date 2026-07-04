# tui-first-frame-render-consistency Specification

## Purpose
TBD - created by archiving change fix-tui-first-frame-repaint-consistency. Update Purpose after archive.
## Requirements
### Requirement: TUI 首次打开后的稳定结果必须与 resize 往返后的稳定结果一致
SmartIPO TUI MUST 保证应用首次打开后的稳定界面表面，与用户执行拉宽再拉回后的稳定界面表面保持一致，不得出现仅首帧可见的横向暗条、未完整刷新的面板内部或边框差异。

#### Scenario: 首次打开不出现仅首帧存在的脏画面
- **WHEN** 用户首次打开 `AgentWorkbenchApp`
- **THEN** 系统 MUST 呈现稳定且完整的状态栏、timeline、queue tray 和输入区表面
- **AND** 系统 MUST NOT 只在首次打开时出现 resize 后会消失的暗条或脏画面

#### Scenario: resize 往返后结果与首帧稳定结果等价
- **WHEN** 用户把终端窗口拉宽后再拉回原始宽度
- **THEN** 系统 MUST 回到与首次打开稳定结果等价的界面表面
- **AND** 关键区域的边框、背景和内容排列 MUST NOT 因为经历过 resize 而与首帧稳定结果不同

