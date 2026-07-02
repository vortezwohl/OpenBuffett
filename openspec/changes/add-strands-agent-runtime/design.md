## Context

`SmartIPO` 目前已经有两类明确能力：一类是 [src/base/text2text.py](/D:/github-project/SmartIPO/src/base/text2text.py) 这样的纯文本模型封装，另一类是 [src/ext/seedream.py](/D:/github-project/SmartIPO/src/ext/seedream.py) 这样的业务能力封装。仓库也已经声明了 `strands-agents[litellm]` 依赖，但还没有一个统一的主脑运行时把模型决策和工具执行连起来。

当前阶段最需要的不是完整应用框架，而是一个最小可靠闭环：主脑能拿到工具列表，能决定是否调用工具，工具结果能回到同一轮响应里，并且这套链路能够被 fake runtime 测试锁住。项目还很早，最容易犯的错不是能力不够，而是提前把 profile、session、事件总线、数据库和多模型编排一口气做满。

## Goals / Non-Goals

**Goals:**
- 提供一个最小 strands agent runtime，完成单轮 agent 调用和 tool call 闭环。
- 建立统一但极薄的工具契约，让现有业务能力可以被 strands 暴露。
- 保持 `Text2Text` 继续服务纯文本调用，新增独立的 agent 模型装配入口。
- 先接入一个真实工具，优先使用 `Seedream` 生图能力验证整条链路。
- 为运行时提供 fake runtime 测试入口，覆盖成功、失败和工具暴露边界。

**Non-Goals:**
- 不引入 `resume-maker` 那种 session repository、阶段状态机、TUI facade 或 observation 落库。
- 不做多 profile、多 runtime mode、多租户或权限系统。
- 不在本次变更中统一 `ifindapi`、`opentrade`、`prompt4py` 等全部能力，只为它们保留同一种接入面。
- 不新增工具插件系统、事件总线或额外 orchestration 框架。

## Decisions

### 1. 用单独的 `base/agent.py` 承担主脑模型装配

决策：新增一个独立的 strands 模型装配入口，例如 `src/base/agent.py`，负责创建 `LiteLLMModel` 与最小 runtime 所需的模型对象；`Text2Text` 保持纯文本职责，不承担 tool-call 语义。

理由：`Text2Text` 的职责已经很明确，继续往里塞主脑运行时只会把“文本生成”和“带工具的 agent 决策”搅在一起。最优雅的拆法不是再建一套复杂抽象，而是单独给主脑一个名字清楚的入口。

备选方案：直接在 `Text2Text` 上追加 tool-call 方法。拒绝，因为这会污染已有概念边界。

### 2. 用 `ToolSpec` + `ToolRegistry` 表达可暴露能力

决策：新增 `src/tool/contracts.py` 和 `src/tool/registry.py`，只保留最小的 `ToolContext`、`ToolResult`、`ToolSpec` 和内存注册表。

理由：这本质上是 Command 描述，不是插件平台。需要的是统一暴露面，而不是复杂装配系统。`resume-maker` 里这层是值得复用的，但要收缩成项目当前真正需要的最小形态。

备选方案：直接把 Python 函数裸传给 strands。拒绝，因为这样后续真实业务工具一多，元数据、说明和测试入口会散掉。

### 3. 用 `core/strands_runtime.py` 做薄 Adapter，不把 strands 散进业务代码

决策：新增一个很薄的运行时桥接层，负责：
- 创建 `Agent(model, tools, system_prompt)`；
- 把 `ToolSpec` 包成 strands tool callable；
- 返回统一的 `StrandsRunResult(text, tools, error)`。

理由：项目需要的是 Adapter，不是第二个框架。把 strands 细节压在一个薄文件里，后续业务层看到的就是稳定的项目内返回结构。

备选方案：让调用方直接面向 strands `Agent` 编程。拒绝，因为 strands 细节会迅速泄漏到各个调用点。

### 4. `AgentLoop` 第一版只提供单轮运行，不做状态机

决策：新增 `src/core/agent_loop.py`，只提供类似 `run_once(prompt, system_prompt, tool_names=None, services=None)` 的最小入口。它负责从 `ToolRegistry` 选择暴露哪些工具，再调用 `StrandsRuntime` 完成一轮。

理由：当前仓库还没有需要 `resume-maker` 那种多阶段流程的业务现实。优雅不是多做，而是只把真实变化点包住。

备选方案：照搬 `resume-maker` 的大 `AgentLoop`。拒绝，因为这会把简历业务状态机一并搬进来。

### 5. 第一批真实工具只接 `Seedream`

决策：新增一个 `Seedream` tool wrapper，输入尽量贴近现有 [generate_seedream_image](/D:/github-project/SmartIPO/src/ext/seedream.py:263) 的函数签名，内部直接调用现有业务函数并返回结构化 `ToolResult`。

理由：最小可靠闭环必须落到真实业务，不然运行时只是空壳。`Seedream` 已经有清晰输入输出，最适合做第一批工具。

备选方案：先做一堆示例工具。拒绝，因为样例工具不产生真实约束。

### 6. 测试采用 fake runtime，不依赖真实外部 LLM

决策：新增最小测试，注入 fake runtime 或 fake agent，覆盖：
- Agent 构造成功；
- 暴露工具被调用；
- 工具失败能向上抛错；
- 未暴露工具不可被使用。

理由：这类运行时最怕只在真实网络请求里“看起来能跑”，但没有稳定回归面。`resume-maker` 的 fake runtime 思路正确，SmartIPO 只要保留最小版本。

备选方案：只做集成测试。拒绝，因为外部依赖太多，定位太差。

## Risks / Trade-offs

- [第一版只支持单轮运行，暂时不含多轮 memory] → 先把单轮 tool loop 跑稳，后续真有需求再在 `AgentLoop` 外围加会话层。
- [`ToolContext` 现在字段过少，后续可能要补服务对象] → 预留 `services` 字典，但不先抽象成复杂容器。
- [`Seedream` 返回图片 URL / Base64，模型回填文本可能不够友好] → tool wrapper 统一返回简明 summary，原始结果仍保留在 `ToolResult.content`。
- [后续接入更多工具时 registry 可能变大] → 先保持显式注册；当工具数真的多到影响维护，再考虑按模块拆分构建函数。
- [真实 strands API 细节可能与假设有小偏差] → 先用构造测试锁定 `LiteLLMModel` 与 `Agent` 的最小本地 API。

## Migration Plan

1. 新增 `src/base/agent.py`，隔离主脑模型装配。
2. 新增 `src/tool/contracts.py` 与 `src/tool/registry.py`，建立最小工具契约。
3. 新增 `src/core/strands_runtime.py` 与 `src/core/agent_loop.py`，完成单轮运行闭环。
4. 新增 `Seedream` tool wrapper，并把它注册到默认工具表。
5. 补上 fake runtime 测试与最小构造测试。

本次没有数据迁移，也不涉及持久化结构变更。若实现失败，回滚代码即可。

## Open Questions

- 第一版是否还需要顺手接一个文本类工具，而不是只接 `Seedream`。当前建议先不要，等真实调用需求出现。
- `ToolContext` 是否需要内建 logger。当前建议不加，现有模块级 logger 已够用。
- 后续若接入 `opentrade`，是否需要 capability 级别的工具分组。当前建议先保持平铺注册。
