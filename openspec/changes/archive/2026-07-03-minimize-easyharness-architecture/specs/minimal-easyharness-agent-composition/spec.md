## ADDED Requirements

### Requirement: 默认 agent 装配必须是薄 composition 层
系统 MUST 通过一个语义明确的 agent composition 入口创建 SmartIPO 默认 agent。该入口 MUST 只负责默认模型配置、system prompt、默认工具列表和 workspace root 绑定，不得引入项目私有 runtime、ModelHub、多调用点配置框架或 text2text 包装层。

#### Scenario: 创建默认 agent
- **WHEN** 调用方请求创建 SmartIPO 默认 agent
- **THEN** 系统 MUST 直接返回基于 `easyharness.Agent` 的会话对象
- **AND** 创建过程 MUST NOT 依赖 `ModelHub`、`Text2Text`、`LLM` 或项目私有 runtime bridge

#### Scenario: 构造默认工具集合
- **WHEN** 系统构造默认 agent 工具集合
- **THEN** 系统 MUST 使用 EasyHarness 官方 fileglide toolset 和项目业务工具对象列表
- **AND** 工具组合 MUST NOT 经过项目私有工具注册表或额外 provider bridge

### Requirement: 默认模型配置必须直接映射到 EasyHarness ModelConfig
系统 MUST 用最小逻辑构造 `easyharness.ModelConfig`。默认模型配置 MUST 来自当前真实需要的常量和环境变量，不得为了单一模型调用点维护 channel 表、brain model 表、ModelHub 类或等价泛化结构。

#### Scenario: 环境变量完整时创建模型配置
- **WHEN** `API_KEY` 已配置且调用方请求默认模型配置
- **THEN** 系统 MUST 返回 `easyharness.ModelConfig`
- **AND** 返回值 MUST 包含默认模型名、API key、base URL、temperature、top_p 和 seed

#### Scenario: 缺少 API key
- **WHEN** `API_KEY` 未配置或为空
- **THEN** 系统 MUST 在构造默认模型配置时显式失败
- **AND** 系统 MUST NOT 延迟到 EasyHarness 底层请求时才暴露缺失鉴权

### Requirement: agent composition 入口命名必须避免应用层歧义
系统 MUST 使用能直接表达 agent 装配职责的模块名作为默认入口，例如 `src.agent`。系统 MUST NOT 长期保留 `src.app.default_agent` 这类容易与 UI app 或业务应用层混淆的导入路径。

#### Scenario: TUI 获取默认 agent
- **WHEN** TUI 需要默认 agent 实例
- **THEN** TUI MUST 从明确的 agent composition 入口导入构造函数
- **AND** TUI MUST NOT 从 `src.app.default_agent` 获取默认 runtime

