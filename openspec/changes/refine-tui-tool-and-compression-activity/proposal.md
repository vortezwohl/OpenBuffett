## Why

当前 SmartIPO TUI 的工具活动和上下文压缩活动仍有三个直接影响使用体验的问题：工具主行颜色层级过亮、语法块包含冗余花括号、compression 生命周期没有在同一条时间线项内收口。与此同时，当前会话压缩预算仍沿用默认或早期保守值，和目标模型实际期望的长上下文使用方式不匹配。

现在推进这轮变更是合适的，因为相关渲染逻辑已集中在 `src/tui/app.py`，而压缩预算装配也集中在 `src/agent.py`。在不改动底层业务工具和主 runtime 协议的前提下，可以把 UI 可读性、压缩反馈一致性和上下文预算三个问题一次性收敛成可实现、可验证的变更。

## What Changes

- 调整工具活动主行的视觉层级，把当前亮绿色和纯白色文本都降为各自颜色体系中的次级色，保留 `Tool`、`Running`、`Done`、`Failed`、`Stopped` 等状态标签与普通文本的可区分性。
- 移除工具活动主行中的 `{` 和 `}` 语法符号，同时保持工具标签、工具名、状态标签之间仍具备明确的可扫读结构。
- 重构 compression 时间线项的生命周期，让 `started` 与 `completed` / `failed` / `cancelled` 事件更新同一条本地时间线项，避免运行中计时残留和一轮 compression 生成两条消息。
- 将 compression 成功结束后的可见消息统一收口为单条 `Conversation compressed` 终态文案，并保证失败和中断仍保留各自真实终态语义，不伪装成成功。
- 显式提升默认模型的 `context_window_limit` 到 900,000 token，并把 summarizing conversation manager 的 `preserve_recent_messages` 调整为 6 条，以匹配新的主动压缩预算策略。
- **BREAKING** 更新 TUI 可见文案和文本快照格式；依赖旧工具主行文本结构、旧 compression 双消息行为或旧压缩预算的测试断言需要同步更新。

## Capabilities

### New Capabilities
- `tui-tool-activity-visual-hierarchy`: 定义工具活动主行的次级色层级、无花括号文本结构，以及状态标签与普通文本的可区分渲染要求。
- `tui-compression-activity-lifecycle`: 定义 compression 活动必须以单条时间线项贯穿 started 到终态，并在成功时收口为单条 `Conversation compressed` 消息。
- `runtime-conversation-compression-budget`: 定义默认 SmartIPO agent 的上下文窗口预算和压缩保留消息策略，确保主动压缩按 900,000 token / 保留 6 条消息生效。

### Modified Capabilities

## Impact

- 主要影响代码位于 `src/tui/app.py` 的工具主行渲染、compression 事件归并和状态文案生成逻辑。
- 主要影响运行时装配位于 `src/agent.py` 的 `ModelConfig` 与 `EventingSummarizingConversationManager` 默认参数。
- 需要同步更新 `test/test_tui_app.py` 中与工具主行文本、颜色样式、compression 生命周期和压缩相关行为有关的断言。
- 不影响业务工具实现、FMP 工具包装、EasyHarness 事件来源和底层文件系统/网络工具协议。
