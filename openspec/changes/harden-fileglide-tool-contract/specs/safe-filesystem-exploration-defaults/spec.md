## ADDED Requirements

### Requirement: Default workbench exploration SHALL favor narrow read-only traversal first
默认 workbench 的目录探索路径 MUST 优先支持“先看一层、再缩小范围、再读取内容”的只读闭环，而不是首次调用就进行深度递归扫描。

#### Scenario: Default path listing is non-recursive
- **WHEN** 模型在默认 workbench 中首次调用 `path.list` 或 `file.list`，且未显式指定 `recursive`
- **THEN** 工具 MUST 采用非递归列举策略
- **THEN** 返回结果 MUST 允许模型基于当前层条目继续缩小范围

### Requirement: Root-level exploration SHALL avoid permission-heavy defaults
当探索对象是磁盘根目录、文件系统锚点或其他高噪音根节点时，系统 MUST 默认采用更安全的列举方式，避免无显式意图的深度递归直接触发权限错误。

#### Scenario: Drive-root exploration does not recurse by default
- **WHEN** 调用方探索 `C:\\`、`D:\\` 或等价文件系统锚点，且未显式指定深度递归
- **THEN** 系统 MUST 只列举当前层内容
- **THEN** 系统 MUST 不因默认深度递归而直接进入系统目录

### Requirement: Failure diagnostics SHALL include recovery guidance for common exploration errors
对于作用域违规、目标不存在和权限受限等高频只读探索失败，系统 MUST 返回能指导下一步收敛范围或修正参数的失败文本。

#### Scenario: Permission failure suggests a narrower retry
- **WHEN** 列举型工具因系统目录权限受限而失败
- **THEN** 失败文本 MUST 指出失败与权限边界相关
- **THEN** 失败文本 MUST 提示通过更小 root、更具体 start 或显式关闭递归来重试

#### Scenario: Scope failure suggests root-relative invocation
- **WHEN** 调用方把绝对路径误填进 `start` 或 `target` 并触发契约或作用域失败
- **THEN** 失败文本 MUST 指出当前调用不符合 root-relative 契约
- **THEN** 失败文本 MUST 提示使用 `root + 相对路径` 的重试方式
