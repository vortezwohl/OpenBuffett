## REMOVED Requirements

### Requirement: text2text 必须作为独立基础 NLP 接口保留
**Reason**: 当前项目已经以 EasyHarness 作为唯一底层 runtime，EasyHarness 无工具 Agent 可以覆盖纯文本生成；继续保留项目私有 text2text 会让“底层交给 EasyHarness”的架构目标失焦。

**Migration**: 删除 `src.core.llm` 和 `src.core.text2text`。所有纯文本生成需求改用 EasyHarness Agent 无工具模式，并复用默认 `ModelConfig` 构造逻辑。

### Requirement: agent runtime 主链不得依赖 text2text 作为控制层
**Reason**: 删除 text2text 后，该防回流规则不再需要单独存在；新的约束由 `easyharness-native-text-generation` 和 `minimal-easyharness-agent-composition` 覆盖。

**Migration**: 用新的测试确认默认 agent 装配不导入 `Text2Text`、`LLM` 或 `src.core`。

### Requirement: text2text 的保留不得重新引入第二套主脑抽象
**Reason**: text2text 不再保留，因此无需继续维护“保留但禁止扩张”的折中规则。

**Migration**: 删除相关文档、测试和导出；README 只描述 EasyHarness 原生能力。

