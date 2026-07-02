## ADDED Requirements

### Requirement: Read-only fileglide tools SHALL expose a stable scoped path contract
项目内只读 fileglide 工具 MUST 对 `root`、`start`、`target` 的语义给出稳定契约：`root` 表示作用域根，`start`/`target` 表示该作用域内的起始路径或目标路径。

#### Scenario: Relative start is resolved within explicit root
- **WHEN** 调用方提供 `root` 和相对 `start` 或相对 `target`
- **THEN** 工具 MUST 在该 root 内解析对应路径
- **THEN** 返回结果中的相对路径语义 MUST 与该 root 保持一致

### Requirement: Wrapper SHALL canonicalize unambiguous absolute paths for read-only tools
对于无歧义的只读调用，若调用方把绝对路径直接传入 `start` 或 `target`，wrapper MUST 在进入 fileglide facade 前将其规范化为“锚点 root + 相对路径”。

#### Scenario: Absolute directory start is normalized for listing
- **WHEN** 调用方在 `path.list` 或 `file.list` 中未提供 `root`，但把绝对目录路径传给 `start`
- **THEN** wrapper MUST 将该绝对路径拆分为锚点 root 和相对 `start`
- **THEN** 工具调用 MUST 进入本地执行，而不是直接因作用域检查失败

#### Scenario: Absolute file target is normalized for text read
- **WHEN** 调用方在 `text.read` 中未提供 `root`，但把绝对文件路径传给 `target`
- **THEN** wrapper MUST 将该绝对路径拆分为锚点 root 和相对 `target`
- **THEN** 后续读取结果 MUST 与同一文件的规范化相对调用保持一致

### Requirement: Wrapper SHALL reject conflicting root and absolute target combinations explicitly
若调用方同时提供 `root` 与绝对 `start`/`target`，且目标不在该 root 内，wrapper MUST 返回显式契约错误，而不是把底层通用作用域异常原样暴露为唯一反馈。

#### Scenario: Absolute target outside provided root fails with contract-aware diagnostic
- **WHEN** 调用方传入 `root=\"D:\\github-project\\SmartIPO\"` 且 `target=\"C:\\temp\\note.txt\"`
- **THEN** wrapper MUST 拒绝本次调用
- **THEN** 失败文本 MUST 明确指出 `root` 与目标路径冲突，并提示正确传参方向

### Requirement: Wrapper SHALL preserve explicit scope boundaries
规范化与错误包装 MUST 不得突破调用方已经显式声明的作用域边界。

#### Scenario: Explicit root is never widened silently
- **WHEN** 调用方已经显式提供 `root`
- **THEN** wrapper MUST NOT 为了兼容绝对路径而静默扩大 root 到盘符根或文件系统根
- **THEN** 若现有 root 无法覆盖目标，系统 MUST 以契约错误结束该调用
