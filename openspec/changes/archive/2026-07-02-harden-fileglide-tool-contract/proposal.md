## Why

当前 fileglide 工具链已经能进入真实执行，但对模型而言仍然像一个不稳定协议：目录/文件工具的结果被摘要压缩，`root` 与 `start`/`target` 的作用域语义没有被清晰暴露，默认递归策略又会在 Windows 根盘触发大量权限失败。结果是模型虽然“看起来在用工具”，却拿不到足够结果、也学不会稳定纠错。

现在需要把这条链路从“能调用”提升到“可理解、可恢复、可扩展”。这不仅是修当前截图里的失败，更是为后续默认 workbench、WebUI 和更大工具集打基础。

## What Changes

- **BREAKING** 调整 fileglide 工具结果回流契约，确保模型收到的是可操作正文，而不是仅有工具名、路径名或过度摘要后的占位文本。
- 为 fileglide 只读工具建立明确的作用域路径契约，统一 `root`、`start`、`target` 的语义，并对绝对路径误用提供可诊断反馈或自动归一化。
- **BREAKING** 调整遍历类工具的默认探索策略，优先使用更安全、更可恢复的非递归根盘探索行为，避免默认撞入系统目录权限边界。
- 补充面向模型的失败语义，让 scope 违规、目标不存在、权限受限等失败能够以稳定、可纠错的文本回流给模型和 timeline。
- 为默认 workbench 工具集定义更稳的读取路径，优先保障“查看目录 -> 缩小范围 -> 读取内容”的基础探索闭环。
- 补充针对 Windows 根盘、绝对路径、结果回流正文和失败纠错链路的测试，锁住后续演进。

## Capabilities

### New Capabilities
- `tool-result-fidelity`: 规范工具结果如何完整回流给模型与 UI，避免摘要压缩掩盖关键信息。
- `fileglide-scoped-path-contract`: 规范 fileglide 工具的 `root`、`start`、`target` 语义，以及绝对路径与作用域根之间的转换规则。
- `safe-filesystem-exploration-defaults`: 规范默认 workbench 的只读探索策略、遍历默认值和常见失败后的恢复路径。

### Modified Capabilities
- 无

## Impact

- Affected code:
  - `src/core/strands_runtime.py`
  - `src/tool/fileglide_tools.py`
  - `src/tui/app.py`
  - `src/core/agent.py`
  - `test/test_strands_runtime.py`
  - `test/test_tui_app.py`
  - 可能新增专门覆盖 fileglide 路径语义与结果回流的测试文件
- APIs:
  - 工具结果返回给模型的文本语义会变化
  - fileglide 读取类工具的输入契约与默认行为会更严格和更明确
- Systems:
  - Textual workbench 默认探索链路
  - Strands 与 fileglide 之间的工具协议层
  - 后续 WebUI/其他前端可复用的工具交互语义
