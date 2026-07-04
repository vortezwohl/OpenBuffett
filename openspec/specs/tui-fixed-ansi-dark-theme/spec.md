# tui-fixed-ansi-dark-theme Specification

## Purpose
TBD - created by archiving change fix-tui-horizontal-resize-and-lock-theme. Update Purpose after archive.
## Requirements
### Requirement: TUI 启动后必须固定使用 ansi-dark
SmartIPO TUI MUST 在应用启动后把当前主题设置为 `ansi-dark`，并以该主题作为首屏和后续重绘的统一视觉基线。

#### Scenario: 应用启动即使用 ansi-dark
- **WHEN** 用户启动 `AgentWorkbenchApp`
- **THEN** 应用当前主题 MUST 为 `ansi-dark`
- **AND** 后续界面刷新 MUST 继续基于 `ansi-dark` 主题执行

### Requirement: 运行中的 TUI 不得向用户暴露主题切换能力
SmartIPO TUI MUST 禁用用户可触发的主题切换入口，用户在运行中的界面里不得通过命令面板或内建主题 action 修改当前主题。

#### Scenario: 命令面板不再提供 Theme 命令
- **WHEN** 系统为当前 screen 生成可用的 system commands
- **THEN** 结果中 MUST NOT 包含用于切换主题的 `Theme` 命令

#### Scenario: 主题切换 action 不改变当前主题
- **WHEN** 用户触发主题切换相关的内建 action
- **THEN** 应用当前主题 MUST 保持为 `ansi-dark`
- **AND** 系统 MUST NOT 打开新的主题选择界面来允许用户换肤

