## ADDED Requirements

### Requirement: TUI workbench SHALL show running tool activity in the conversation timeline
Textual workbench MUST 在工具执行过程中把工具条目展示在聊天时间线中，并持续更新运行时长，而不是只在工具结束后展示结果。

#### Scenario: Running tool appears immediately after tool start
- **WHEN** workbench 收到 `tool_started` 事件
- **THEN** 聊天时间线 MUST 立即出现对应的运行中工具条目
- **THEN** 条目 MUST 显示正在运行状态和递增的计时

#### Scenario: Running tool timer keeps refreshing before completion
- **WHEN** 工具仍处于运行状态
- **THEN** workbench MUST 周期性刷新该条目的运行时长
- **THEN** 在工具完成前，条目 MUST 保持可见

### Requirement: TUI workbench SHALL preserve visible running state for fast tools
对于极快完成的工具，Textual workbench MUST 保证用户仍能观察到至少一次运行中状态，再切换到完成或失败状态。

#### Scenario: Fast tool still shows running activity before completion
- **WHEN** 某个工具从开始到完成的时间短于界面的最小可见阈值
- **THEN** workbench MUST 先展示该工具的运行中条目
- **THEN** 完成态更新 MUST 在至少一次可见运行态之后发生

#### Scenario: Completed tool shows summary after visible running state
- **WHEN** 工具完成且运行中状态已经对用户可见
- **THEN** workbench MUST 把同一条工具条目更新为完成状态
- **THEN** 条目 MUST 展示结果概要，且在有详细结果时按 UI 规则决定是否折叠
