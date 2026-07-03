## Why

SmartIPO 当前同时维护了 `easyharness` 依赖与一整套自研 agent runtime、tool contract、tool registry、timeline/event 机制，导致同一问题域存在两套并行抽象，结构重复、语义漂移和维护成本都在持续上升。既然项目已经明确决定放弃底层自研路线，并且不再考虑后向兼容，现在就是一次性收敛到 `easyharness` 主干语义的合适时机。

这次变更的核心不是“替换一个库”，而是把 agent、tool、事件流三条主链统一到单一架构中心，消除平行协议，给后续 TUI、WebUI、自动化工作流和新工具扩展提供更稳定的边界。

## What Changes

- **BREAKING** 以 `easyharness.Agent` 作为唯一 agent runtime 入口，移除项目自研 `Agent`/`StrandsRuntime`/`LoopEvent` 这一整套会话执行协议。
- **BREAKING** 以 `easyharness.tool` 和官方 toolset 作为唯一工具接入方式，移除项目自研 `ToolSpec`、`ToolResult`、`ToolRegistry`、tool framework 和 provider bridge。
- **BREAKING** 以 `easyharness.AgentEvent` 事件流作为唯一运行时事件来源，移除项目自研 timeline 核心机制，不再把 `core.timeline` 作为跨 UI 的底层事实标准。
- 保留 `text2text`，但将其降级为独立基础 NLP 接口，不再承担 agent runtime、tool context 或会话控制职责。
- 引入新的应用装配层，集中负责 `ModelConfig`、system prompt、默认工具集、workspace root 和 UI 注入入口，避免 UI 直接定义运行时协议。
- 将 TUI 和未来 WebUI 收敛为 `easyharness.Agent.stream()` 的消费者，只保留展示层本地 view-model，不再维护第二套事件语义。
- 用删除式迁移替代兼容式迁移，明确淘汰旧 API、旧命名和旧测试，避免“新旧双栈长期并存”。

## Capabilities

### New Capabilities
- `easyharness-agent-runtime`: 定义 SmartIPO 的唯一 agent 会话运行时必须建立在 `easyharness.Agent`、`ModelConfig` 和官方会话语义之上。
- `easyharness-tooling`: 定义 SmartIPO 的工具声明、注册、执行和默认文件工具集必须建立在 `easyharness.tool` 与官方 toolset 之上。
- `agent-event-stream-ui-integration`: 定义 TUI 和未来 WebUI 必须直接消费 `easyharness.AgentEvent` 事件流，并在展示层本地完成渲染态组装。
- `text2text-foundation-service`: 定义 `text2text` 保留为独立基础 NLP 服务，但不得再回流为 agent runtime 的替代控制层。

### Modified Capabilities
- None.

## Impact

- 受影响代码集中在 [src/core](D:/Projects/PythonProjects/SmartIPO/src/core)、[src/tool](D:/Projects/PythonProjects/SmartIPO/src/tool)、[src/app](D:/Projects/PythonProjects/SmartIPO/src/app)、[src/tui](D:/Projects/PythonProjects/SmartIPO/src/tui)、[src/service](D:/Projects/PythonProjects/SmartIPO/src/service) 和对应测试。
- 会删除当前自研的 agent runtime、tool contract/framework、timeline reducer 及相关测试；这是一轮明确的破坏性内部架构迁移。
- 运行时依赖中心将从项目内自定义协议切换到 `easyharness` 公开 SDK 与官方 fileglide toolset；模型配置装配仍留在项目内，但输出改为 `easyharness.ModelConfig`。
- TUI、未来 WebUI、自动化调用方和新工具开发方式都会发生变化，但变化方向是收敛而非扩散。
