# tui-unified-repaint-lifecycle Specification

## Purpose
TBD - created by archiving change fix-tui-first-frame-repaint-consistency. Update Purpose after archive.
## Requirements
### Requirement: mount 与 resize 必须共享统一的完整 repaint 生命周期
SmartIPO TUI MUST 让首次挂载后的绘制与终端尺寸变化后的重绘走同一套完整重排/重绘生命周期，不得让 mount 与 resize 分别使用不同的局部刷新时序。

#### Scenario: 首次挂载通过统一 repaint 路径完成首帧
- **WHEN** `AgentWorkbenchApp` 完成挂载并准备呈现首帧
- **THEN** 系统 MUST 通过统一的完整 repaint 路径完成布局与表面绘制
- **AND** 系统 MUST NOT 在最终布局稳定前直接写入依赖当前尺寸的局部内容

#### Scenario: resize 通过同一 repaint 路径完成重绘
- **WHEN** 终端尺寸发生变化
- **THEN** 系统 MUST 复用与首次挂载相同的完整 repaint 路径完成重排和重绘
- **AND** 系统 MUST NOT 再单独维护一套只属于 resize 的局部刷新顺序

