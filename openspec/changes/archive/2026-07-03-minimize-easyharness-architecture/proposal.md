## Why

SmartIPO 已经把 agent、工具和事件流主链迁移到 EasyHarness，但仓库仍保留了项目自研 LLM/text2text、ModelHub、model_config 表、`app` 装配包和未使用的 `util` helper。它们现在不再提供真实架构能力，反而让后续开发者误以为项目仍需要维护一套 EasyHarness 之外的底层框架。

这次变更要把 SmartIPO 从“已接入 EasyHarness”推进到“只在业务边界保留项目代码”：底层会话、纯文本调用、工具协议和模型配置形状全部交给 EasyHarness，项目只维护业务工具、外部数据客户端和 UI 展示。

## What Changes

- **BREAKING** 删除 `src.core.llm`、`src.core.text2text` 以及对应公开导出和边界测试，不再维护项目私有 LLM/text2text 抽象。
- **BREAKING** 取消 `src.service.model_hub.ModelHub` 和多 channel/call-name 配置表，默认模型装配收敛为一个直接返回 `easyharness.ModelConfig` 的最小函数。
- **BREAKING** 删除 `src/model_config.py` 中的 dataclass/dict 配置模型，改为当前真实需要的常量或内联默认值。
- **BREAKING** 将 `src/app/default_agent.py` 的职责改名并压平为更明确的 agent composition 入口，例如 `src/agent.py`，避免 `app` 包与 TUI app、业务应用概念混淆。
- **BREAKING** 删除未被生产代码或测试调用的 `src/util` 包；未来需要 helper 时，就近放在真实调用模块内，直到出现多个真实调用点再提升。
- 保留 `src/tui` 作为 UI 层，继续直接消费 `easyharness.AgentEvent`，不抽出新的共享 timeline/view-model 协议。
- 保留 `src/tool` 中的项目业务工具声明，继续用 `easyharness.tool`；保留 `src/ext` 中的外部服务客户端，因其代表真实业务边界。
- 更新 README、测试和 OpenSpec 能力定义，明确纯文本调用的默认路径是 `easyharness.Agent` 不装载工具，而不是 SmartIPO 自研 text2text。

## Capabilities

### New Capabilities

- `minimal-easyharness-agent-composition`: 定义 SmartIPO 默认 agent 装配必须是薄 composition 层，只负责模型常量、system prompt、工具列表和 workspace root，不再引入 ModelHub、私有 text2text 或多调用点配置框架。
- `easyharness-native-text-generation`: 定义纯文本生成必须复用 EasyHarness 原生 agent 能力，通过禁用文件工具和传入空工具列表实现，不再维护项目私有 text2text 抽象。
- `lean-project-surface`: 定义项目包结构只保留真实业务边界和 UI 边界，禁止长期保留未使用 helper、误导性 package 名称和“为了以后”的装配层。

### Modified Capabilities

- `text2text-foundation-service`: 将“必须保留项目私有 text2text”改为“必须删除项目私有 text2text，并以 EasyHarness 原生纯文本 agent 替代”。
- `easyharness-agent-runtime`: 收紧默认 agent 装配要求，禁止通过 `ModelHub`、多调用点配置表或项目 LLM 包装层创建默认 runtime。

## Impact

- 受影响代码集中在 `src/core`、`src/service`、`src/model_config.py`、`src/app`、`src/util`、`src/tui`、`README.md` 和对应测试。
- 这是内部破坏性重构；不保留兼容 shim，不支持旧的 `Text2Text`、`LLM`、`ModelHub`、`src.app.default_agent` 导入路径。
- 外部依赖原则不变：继续依赖 EasyHarness、Textual、requests 等现有依赖；本变更不新增新依赖。
- 验证门禁需要重写：删除 text2text/model_hub 测试，新增最小 agent composition、纯文本 EasyHarness agent、包结构瘦身和未使用 helper 清理测试。
