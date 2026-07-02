## Context

当前运行时里，`build_strands_tool(...)` 直接把 `tool_spec.name` 传给了 strands 的 `tool(...)` 包装器。与此同时，fileglide 工具集合大量使用点号命名，例如 `file.create`、`text.write`、`text.replace-lines`。这种命名在项目内部是合理的，但对 OpenAI-compatible provider 来说不合法，会在请求发出前就被拒绝。

这个问题的关键不在工具逻辑本身，而在“内部工具语义”和“provider tool schema”之间缺少一层边界适配。

## Goals / Non-Goals

**Goals:**
- 修复 provider 对 `function.name` 的格式校验错误。
- 保持内部工具名、注册表接口、`tool_names` 参数和事件展示语义不变。
- 让 provider-facing 工具名可以稳定映射回原始内部工具。
- 用最小测试覆盖这个适配边界。

**Non-Goals:**
- 不改 `fileglide_tools.py` 里的原始 `ToolSpec.name`。
- 不全仓把点号工具名改成下划线工具名。
- 不修改 TUI 的展示文案或工具事件结构。
- 不引入新的工具层抽象、权限模型或 provider 特化注册表。

## Decisions

### 1. 只在 strands/provider 适配边界做工具名规范化

决策：在 `src/core/strands_runtime.py` 中引入一个最小工具名规范化函数，例如把 `.` 替换为 `_`，并仅用于 provider-facing `tool(...)` 包装名。

理由：问题出在边界输出，不在内部工具定义。边界修正是最小且正确的修法。

备选方案：直接修改所有 `ToolSpec.name`。拒绝，因为那会连带影响注册表、测试、工具筛选与事件展示。

### 2. 保留内部名，外部名单向导出，执行仍绑定原始 handler

决策：provider 看到的是合法化后的名字，但真正执行的仍是原始 `tool_spec.handler`，事件里也继续记录 `tool_spec.name`。

理由：这样既满足 provider 约束，又不牺牲内部一致性。

备选方案：在系统内部全面切换到外部名。拒绝，因为这是把外部兼容性泄漏进内部设计。

### 3. 只补边界测试，不扩大测试面

决策：增加小而准的测试，验证：
- 合法化后的 provider-facing name 不含点号；
- 合法化不会改变内部事件和工具调用语义。

理由：这是一个边界兼容 bug，不需要顺手重写整套 runtime 测试。

## Risks / Trade-offs

- [两个内部名字规范化后可能碰撞] → 先采用可预测的单规则映射，并补一条冲突检测或至少在设计里保留显式失败路径。
- [修复只覆盖 `.`，遗漏其他非法字符] → 规范化规则直接收敛到 provider 允许字符集，而不是只做点号替换的特判。
- [边界名变化让调试困难] → 事件和执行记录继续保留内部原始工具名。

## Migration Plan

1. 在 `strands_runtime` 增加 provider-facing 工具名规范化和映射逻辑。
2. 保持现有工具定义与调用方不变。
3. 增加边界测试，验证合法名生成和调用回落。
4. 运行现有测试，确认 workbench/runtime 行为未回归。

## Open Questions

- 当前是否需要把合法化后的 provider name 暴露到调试日志中。建议本轮不做，先把运行修通。
