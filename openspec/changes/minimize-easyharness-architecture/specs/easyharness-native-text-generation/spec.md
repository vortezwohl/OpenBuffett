## ADDED Requirements

### Requirement: 纯文本生成必须复用 EasyHarness 原生 Agent
系统 MUST 使用 EasyHarness 原生 `Agent` 表达纯文本生成能力。项目 MUST NOT 再维护 `Text2Text`、`LLM` 或等价私有模型调用抽象作为第二套文本生成入口。

#### Scenario: 业务流程只需要纯文本生成
- **WHEN** 某个业务流程只需要基础文本回复且不需要文件工具或业务工具
- **THEN** 系统 MUST 使用 `easyharness.Agent` 的无工具配置完成该调用
- **AND** 系统 MUST NOT 要求调用方导入项目私有 `Text2Text`

#### Scenario: 构造无工具文本 agent
- **WHEN** 调用方需要构造纯文本 agent
- **THEN** 系统 MUST 允许通过 `tools=[]` 且 `enable_fileglide=False` 的 EasyHarness agent 配置表达该能力
- **AND** 该能力 MUST 继续使用 `easyharness.ModelConfig` 作为模型配置来源

### Requirement: 项目不得暴露私有 LLM 抽象
系统 MUST 删除并停止导出项目私有 LLM 基类和 Text2Text 实现。仓库测试和文档 MUST NOT 将这些类型描述为可用公共入口。

#### Scenario: 检查公共导入表面
- **WHEN** 开发者检查 SmartIPO 包导出和 README
- **THEN** 系统 MUST NOT 暴露 `LLM` 或 `Text2Text` 作为推荐入口
- **AND** 文档 MUST 指向 EasyHarness 原生 agent 语义

## REMOVED Requirements

### Requirement: text2text 必须作为独立基础 NLP 接口保留
**Reason**: EasyHarness 已经提供原生 agent 会话能力，且无工具配置可以覆盖纯文本生成场景；继续维护项目私有 text2text 会重新形成第二套模型调用入口。

**Migration**: 纯文本调用迁移到 `easyharness.Agent(model=..., system_prompt=..., tools=[], enable_fileglide=False)`。需要默认模型时复用 SmartIPO 的最小 agent composition 模型配置函数。

