## 1. 模型与装配主干切换

- [x] 1.1 将模型装配层从返回 `strands` 模型改为返回 `easyharness.ModelConfig`，并保持现有集中配置与环境变量校验规则。
- [x] 1.2 新建或重写默认 agent 装配入口，使其直接构造 `easyharness.Agent`，集中注入 system prompt、默认工具集与 workspace root。
- [x] 1.3 调整默认 prompt 与工具命名文案，移除对旧工具名、旧 runtime 名词和旧事件阶段的依赖。

## 2. 工具体系迁移到 EasyHarness

- [x] 2.1 盘点现有自定义工具，区分“保留为业务工具”与“由官方 fileglide toolset 替代”的边界。
- [x] 2.2 将官方文件系统能力切换为 `build_fileglide_tools(default_root=...)`，移除默认主链对自研 fileglide tool specs 的依赖。
- [x] 2.3 将 Seedream 等保留业务工具改写为 `@easyharness.tool(...)` 形式，并使用 `ToolOutput` 或合法公共返回值表达结果。
- [x] 2.4 删除 `ToolSpec`、`ToolResult`、`ToolRegistry` 和 tool framework 在主链路中的使用点。

## 3. TUI 事件消费与展示层重写

- [x] 3.1 将 TUI 的会话执行改为调用 `agent.stream()`，直接消费 `AgentEvent`。
- [x] 3.2 在 TUI 内部实现仅供展示使用的本地 view-model，覆盖 thinking、tool、assistant、system 四类事件。
- [x] 3.3 重建工具结果、失败态、流式输出、最小可见时长和折叠详情的展示逻辑，确保不再依赖 `LoopEvent` 和 `ConversationTimeline`。
- [x] 3.4 确认 TUI 启动与新会话重置入口只依赖 composition layer，不再自行装配 runtime 协议。

## 4. text2text 边界收敛

- [x] 4.1 盘点 `text2text` 当前调用点，区分“基础 NLP 使用”与“误入 agent runtime 主链”的使用场景。
- [x] 4.2 保留 `text2text` 的独立接口与必要调用点，同时删除其与 agent runtime、tool context、事件流和默认主脑控制的耦合。
- [x] 4.3 补充代码注释或模块说明，明确 `text2text` 是基础服务而不是第二套 agent runtime。

## 5. 删除旧 runtime 与旧事件体系

- [x] 5.1 删除 `src/core/agent.py`、`src/core/strands_runtime.py` 及相关旧导出，收敛到 EasyHarness 单一 runtime。
- [x] 5.2 删除 `src/core/events.py`、`src/core/timeline.py` 和所有对它们的主链依赖。
- [x] 5.3 删除 `src/tool/contracts.py`、`src/tool/framework/*`、`src/tool/registry.py` 以及不再需要的自研 fileglide 工具实现。
- [x] 5.4 清理仓库中的旧导入路径、旧命名、旧注释和残留兼容层，确保不存在“表面已删、实则仍可回流”的私有协议。

## 6. 测试与验证门禁重建

- [x] 6.1 删除或重写依赖 `ToolSpec`、`StrandsRunResult`、`LoopEvent`、`ConversationTimeline` 的旧测试。
- [x] 6.2 新增模型装配测试，验证默认装配返回 `ModelConfig` 且集中采样参数约束仍有效。
- [x] 6.3 新增工具装配测试，验证官方 fileglide toolset 与项目业务工具可被同一 EasyHarness agent 装配和调用。
- [x] 6.4 新增 TUI 冒烟测试，验证用户输入、thinking、tool、assistant 和失败态都来自 `AgentEvent` 流并正确渲染。
- [x] 6.5 新增 `text2text` 边界测试，验证其仍可独立调用且不再承担 agent runtime 主链职责。

## 7. 文档与收尾检查

- [x] 7.1 更新 README 或相关开发说明，明确 SmartIPO 已完全迁移到 EasyHarness 主干架构。
- [x] 7.2 复查默认入口、依赖列表和目录职责，确认仓库不再宣传或暗示自研 agent/tool/timeline 主机制。
- [x] 7.3 运行最终验证命令集并记录结果，确保实现完成后可直接进入评审或下一轮功能开发。
