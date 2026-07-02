## ADDED Requirements

### Requirement: 系统必须提供最小可用的 strands agent 运行时
系统 MUST 提供一个基于 `strands-agents` 的最小主脑运行时，使调用方能够在单轮请求中传入 prompt、system prompt 和暴露工具集合，并获得统一的项目内运行结果。

#### Scenario: 单轮主脑调用返回统一结果
- **WHEN** 调用方发起一次 agent 运行并传入 prompt、system prompt、模型对象和工具列表
- **THEN** 系统 MUST 通过 strands `Agent` 执行这一轮调用
- **AND** 系统 MUST 返回统一的项目内结果结构，而不是把 strands 原始对象直接暴露给业务层

### Requirement: 系统必须把业务工具以统一契约暴露给 strands
系统 MUST 定义统一的工具契约与工具注册表，所有暴露给主脑的业务能力 MUST 通过该契约注册，再由运行时包装为 strands tools。

#### Scenario: 已注册工具被包装为 strands tool
- **WHEN** 一个业务工具按照项目工具契约完成注册
- **THEN** 运行时 MUST 能把该工具包装为 strands 可调用工具
- **AND** 调用方 SHALL 能按工具名选择是否将其暴露给本轮主脑

### Requirement: 系统必须保持文本模型与主脑运行时分离
系统 MUST 保持纯文本模型封装与主脑 agent 运行时职责分离；纯文本调用 SHALL 继续使用文本模型封装，而 strands 主脑 SHALL 通过独立模型装配入口创建。

#### Scenario: 主脑模型装配不复用 Text2Text 作为 tool runtime
- **WHEN** 调用方需要创建可执行 tool call 的主脑模型
- **THEN** 系统 MUST 使用独立的主脑模型装配入口
- **AND** 系统 MUST NOT 要求 `Text2Text` 直接承担 tool-call 运行时职责

### Requirement: 系统必须先接入至少一个真实业务工具形成闭环
系统 MUST 先把至少一个现有真实业务能力暴露给 strands 运行时，作为最小可靠可用的 tool call 闭环起点。

#### Scenario: Seedream 能力作为真实工具被主脑调用
- **WHEN** 主脑本轮暴露了 Seedream 相关工具且模型决定调用它
- **THEN** 系统 MUST 执行现有 Seedream 业务函数
- **AND** 系统 MUST 把工具结果整理为主脑可读的结果内容返回给同一轮运行时

### Requirement: 系统必须提供可注入 fake runtime 的测试入口
系统 MUST 提供不依赖真实外部 LLM 的最小测试入口，以验证主脑运行、工具暴露和工具失败边界。

#### Scenario: fake runtime 驱动一次工具成功调用
- **WHEN** 测试注入 fake runtime 并模拟一次已暴露工具的调用
- **THEN** 系统 MUST 能验证该工具被执行
- **AND** 系统 MUST 能验证统一运行结果按预期返回

#### Scenario: fake runtime 触发工具失败
- **WHEN** 测试注入 fake runtime 且工具执行抛出异常
- **THEN** 系统 MUST 让异常继续向上暴露
- **AND** 系统 MUST NOT 把该失败伪装成成功回复

#### Scenario: 未暴露工具不会被当前回合使用
- **WHEN** 调用方在本轮只暴露工具子集
- **THEN** 系统 MUST 只向主脑提供该子集
- **AND** 未被暴露的工具 MUST NOT 进入当前主脑回合
