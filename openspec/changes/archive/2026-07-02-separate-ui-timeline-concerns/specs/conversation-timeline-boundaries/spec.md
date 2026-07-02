## ADDED Requirements

### Requirement: Core timeline state SHALL remain presentation-agnostic
会话时间线核心状态层 MUST 只暴露跨 UI 复用所需的原始语义数据，不得在 core 中拼接任何特定 UI 的工具标题、状态文案或提示文案。

#### Scenario: Tool events are reduced without UI-formatted titles
- **WHEN** runtime 发出 `tool_started`、`tool_completed` 或 `tool_failed` 事件
- **THEN** core 归约后的时间线条目 MUST 保留 `tool_name`、`tool_kind`、状态、时长和结果数据
- **THEN** core MUST NOT 依赖 `display_name` 或拼出类似“文件工具 · Text read”的标题

#### Scenario: Tool event payload excludes presentation-only fields
- **WHEN** strands runtime 为工具调用构造 `LoopEvent.payload`
- **THEN** payload MUST 只包含 UI 消费所需的原始语义字段
- **THEN** payload MUST NOT 包含仅服务于展示的 `display_name` 或面向用户的完成/失败提示文案

### Requirement: Core timeline entries SHALL preserve raw tool identity
会话时间线核心状态层 MUST 保留原始工具身份，以便不同 UI 独立决定如何展示。

#### Scenario: Raw tool name remains available to UI consumers
- **WHEN** 某个工具条目被追加到时间线
- **THEN** UI 消费方 MUST 能从条目或其 metadata 中读取原始 `tool_name`
- **THEN** 该名称 MUST 与内部工具注册名一致，不经过翻译或二次命名

#### Scenario: Tool failures stay semantic in the core layer
- **WHEN** 工具调用失败
- **THEN** core 时间线条目 MUST 标记失败状态并保留原始错误信息
- **THEN** core MUST NOT 把错误加工成特定界面的展示句式
