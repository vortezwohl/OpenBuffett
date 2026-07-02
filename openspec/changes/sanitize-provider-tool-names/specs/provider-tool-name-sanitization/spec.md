## ADDED Requirements

### Requirement: 系统必须对暴露给 provider 的工具名做合法化处理
系统 MUST 在把内部 `ToolSpec` 暴露给 provider 前，对工具名进行合法化处理，确保生成出的外部工具名满足当前 provider 对 `function.name` 的格式约束。

#### Scenario: 内部工具名包含点号
- **WHEN** 系统需要把如 `text.write`、`file.create`、`batch.run` 这类内部工具暴露给 provider
- **THEN** 系统 MUST 生成只包含字母、数字、下划线或连字符的外部工具名
- **AND** 系统 MUST NOT 把带点号的内部工具名直接传给 provider

### Requirement: 系统必须保留内部工具语义并支持反向映射
系统 MUST 保留内部 `ToolSpec.name` 作为项目内唯一工具标识，并 SHALL 通过稳定映射让 provider 发起的工具调用能够准确回落到原始内部工具 handler。

#### Scenario: provider 发起合法化后的工具调用
- **WHEN** provider 使用合法化后的外部工具名请求调用某个工具
- **THEN** 系统 MUST 把这次调用路由到对应原始 `ToolSpec` 的 handler
- **AND** 事件、摘要与执行记录 MUST 继续使用原始内部工具名

### Requirement: 系统不得通过全仓重命名来解决 provider 兼容问题
系统 MUST 仅在 provider 适配边界处理工具名兼容问题，而 MUST NOT 为了满足外部 schema 约束去修改内部注册表、工具筛选参数或业务代码中的原始工具名。

#### Scenario: 现有内部代码引用点号工具名
- **WHEN** 代码通过 `ToolRegistry`、`tool_names` 或测试替身引用如 `text.write` 的内部工具名
- **THEN** 系统 MUST 继续支持这些原始名字
- **AND** 本轮修复 MUST NOT 要求调用方改用 `text_write` 之类的新内部名字
