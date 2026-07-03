## ADDED Requirements

### Requirement: UI 必须直接消费 EasyHarness AgentEvent 流
TUI 和未来 WebUI MUST 直接消费 `easyharness.Agent.stream()` 产生的 `AgentEvent` 流作为运行时事实来源。系统 MUST NOT 再要求 UI 先消费项目私有 `LoopEvent`、timeline reducer 或其他中间事件协议。

#### Scenario: TUI 提交一轮任务
- **WHEN** 用户在 TUI 中提交一轮任务
- **THEN** TUI MUST 直接从 `Agent.stream()` 读取 `AgentEvent`
- **AND** TUI MUST NOT 依赖项目私有事件桥接器才能接收运行时状态

#### Scenario: WebUI 复用同一会话协议
- **WHEN** 未来 WebUI 接入同一 agent 会话能力
- **THEN** WebUI MUST 复用相同的 `AgentEvent` 事实源
- **AND** WebUI MUST NOT 需要额外学习第二套 SmartIPO 私有事件合同

### Requirement: UI 必须可见 thinking、tool、assistant 和 system 事件
UI MUST 能基于 `AgentEvent` 渲染 thinking、tool、assistant 和 system 事件，并明确展示 started、delta、completed、failed 这些状态变化。

#### Scenario: 工具执行成功
- **WHEN** 事件流中出现某个工具的 started 和 completed 事件
- **THEN** UI MUST 展示该工具的运行中状态和完成状态
- **AND** UI MUST 能读取事件中的名称、持续时间和附加数据用于展示

#### Scenario: 工具执行失败
- **WHEN** 事件流中出现某个工具的 failed 事件
- **THEN** UI MUST 明确展示失败而不是把该轮调用渲染成成功
- **AND** 失败文本 MUST 对用户可见

#### Scenario: assistant 流式输出
- **WHEN** 事件流中出现 assistant started、delta 和 completed 事件
- **THEN** UI MUST 以流式方式累计展示 assistant 文本
- **AND** completed 后的展示结果 MUST 与最终输出保持一致

### Requirement: UI 本地状态必须局限于展示层
UI 可以为滚动跟随、折叠详情、本地动画、最小时长显示等展示需要维护本地状态，但这些状态 MUST 仅存在于展示层。系统 MUST NOT 再把这些展示态抽象成跨 UI 共享的核心 runtime 协议。

#### Scenario: 快速工具调用需要最小可见时长
- **WHEN** UI 希望让极快完成的工具调用仍短暂显示运行态
- **THEN** UI MUST 在本地实现或放弃实现这一展示策略
- **AND** 该策略 MUST NOT 反向要求 runtime 提供新的项目私有事件类型

#### Scenario: 详情折叠与展开
- **WHEN** UI 需要对长工具结果进行折叠或展开
- **THEN** UI MUST 在本地根据 `AgentEvent.data` 组织展示
- **AND** 系统 MUST NOT 再引入跨 UI 共享的 timeline entry 合同来承载这类展示偏好
