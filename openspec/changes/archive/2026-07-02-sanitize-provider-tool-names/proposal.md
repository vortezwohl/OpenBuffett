## Why

当前 SmartIPO 的内部工具名大量使用点号命名，例如 `text.write`、`file.create`。这对项目内部可读，但在 OpenAI-compatible tool schema 里会直接触发 `function.name` 校验失败，导致 workbench 无法正常进入 agent loop。

## What Changes

- 在 strands/provider 适配边界增加一层工具名规范化，把内部工具名映射为符合 provider 约束的外部工具名。
- 保留项目内部 `ToolSpec.name`、`ToolRegistry`、`tool_names` 与事件展示里的原始点号语义，不做全仓工具重命名。
- 为运行时增加“外部工具名 -> 内部工具定义”的稳定映射，确保模型发起工具调用时仍能落回原始 handler。
- 增加针对 provider-facing 工具名合法性和调用映射的测试，覆盖 fileglide 工具这类点号命名场景。

## Capabilities

### New Capabilities
- `provider-tool-name-sanitization`: 约束暴露给 provider 的工具名必须经过合法化处理，并能稳定映射回原始内部工具。

### Modified Capabilities
- None.

## Impact

- 受影响代码主要位于 `src/core/strands_runtime.py` 与相关测试。
- 不新增依赖，不改变内部工具注册表接口，不修改 fileglide 工具名和 TUI 展示语义。
- 这是一次适配层修复，不是业务层或工具层重命名。
