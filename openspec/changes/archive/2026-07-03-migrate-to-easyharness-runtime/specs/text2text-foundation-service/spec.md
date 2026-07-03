## ADDED Requirements

### Requirement: text2text 必须作为独立基础 NLP 接口保留
系统 MUST 保留 `text2text` 作为可独立调用的基础文本生成/NLP 接口。其存在价值 MUST 独立于 agent runtime，不因本次 EasyHarness 迁移而被整体移除。

#### Scenario: 业务侧需要直接文本生成
- **WHEN** 某个业务流程只需要基础文本生成能力而不需要 agent 会话控制
- **THEN** 系统 MUST 允许其直接调用 `text2text`
- **AND** 该调用 MUST NOT 依赖 `easyharness.Agent` 会话对象

### Requirement: agent runtime 主链不得依赖 text2text 作为控制层
系统 MUST 禁止把 `text2text` 用作 agent runtime 的会话控制、工具调度、事件流桥接或默认主脑执行主干。EasyHarness agent 主链 MUST 与 `text2text` 控制职责解耦。

#### Scenario: 构造默认 agent
- **WHEN** 系统构造默认 EasyHarness agent
- **THEN** 该装配过程 MUST 仅依赖 `ModelConfig`、system prompt 和工具集合
- **AND** 该装配过程 MUST NOT 先经过 `text2text` 包装才能工作

#### Scenario: 执行一轮 agent 会话
- **WHEN** 调用方执行一轮 agent 会话
- **THEN** 会话执行、工具调用和事件流 MUST 由 EasyHarness runtime 负责
- **AND** `text2text` MUST NOT 充当中间 runtime bridge

### Requirement: text2text 的保留不得重新引入第二套主脑抽象
系统 MUST 确保 `text2text` 只作为基础能力存在，而不是重新演化为第二套“轻量 agent”或“备用主脑”抽象。仓库中的默认主脑语义 MUST 唯一指向 EasyHarness。

#### Scenario: 新增需要 LLM 的业务能力
- **WHEN** 开发者为新业务能力引入 LLM 调用
- **THEN** 若该能力需要会话控制、工具调用或事件流，开发者 MUST 使用 EasyHarness agent 主链
- **AND** 若该能力只需要纯文本生成，系统 MUST 允许开发者直接使用 `text2text`，但 MUST NOT 为其补建新的会话 runtime 抽象
