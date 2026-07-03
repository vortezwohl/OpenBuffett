## ADDED Requirements

### Requirement: Agent 会话运行时必须基于 EasyHarness 公共 SDK
系统 MUST 以 `easyharness.Agent` 作为唯一公开的 agent 会话运行时入口。项目实现 MUST NOT 再要求调用方通过项目自研 `Agent`、`StrandsRuntime`、`SessionRunner` 或等价私有 bridge 才能启动会话。

#### Scenario: 创建默认 agent
- **WHEN** 调用方请求创建 SmartIPO 默认 agent
- **THEN** 系统 MUST 返回一个基于 `easyharness.Agent` 语义工作的会话对象
- **AND** 调用方 MUST NOT 需要导入项目私有 runtime bridge 类型

### Requirement: Agent 会话必须暴露 EasyHarness 原生会话语义
系统 MUST 通过 EasyHarness 原生语义提供同步执行、流式执行和会话重置能力。项目 MUST NOT 再定义第二套并行的回合执行合同或结果对象来表达相同语义。

#### Scenario: 执行一轮同步会话
- **WHEN** 调用方执行一轮同步会话
- **THEN** 系统 MUST 提供 EasyHarness 原生的最终文本结果语义
- **AND** 系统 MUST NOT 要求调用方消费项目私有 `StrandsRunResult` 一类结果对象

#### Scenario: 执行一轮流式会话
- **WHEN** 调用方执行一轮流式会话
- **THEN** 系统 MUST 以 `easyharness.AgentEvent` 序列输出运行时事件
- **AND** 系统 MUST NOT 在主链路中先生成项目私有事件再二次转译

#### Scenario: 重置会话
- **WHEN** 调用方请求重置当前会话
- **THEN** 系统 MUST 清除当前会话上下文并开始新的 EasyHarness 会话
- **AND** 后续回合 MUST NOT 继续复用重置前的会话历史

### Requirement: 模型装配必须输出 EasyHarness ModelConfig
系统 MUST 保留项目集中模型配置与环境变量解析规则，但其装配结果 MUST 是 `easyharness.ModelConfig`，以便 agent runtime 直接消费。

#### Scenario: 构造默认模型配置
- **WHEN** 调用方请求默认主脑模型配置
- **THEN** 系统 MUST 返回 `easyharness.ModelConfig`
- **AND** 返回值 MUST 包含模型名、API Key、base URL 以及集中配置中的采样参数

#### Scenario: 防止调用点绕过集中采样配置
- **WHEN** 调用方试图在默认 agent 装配入口直接覆写温度、top_p 或 seed
- **THEN** 系统 MUST 拒绝该请求
- **AND** 系统 MUST 继续要求这些采样参数由项目集中配置定义
