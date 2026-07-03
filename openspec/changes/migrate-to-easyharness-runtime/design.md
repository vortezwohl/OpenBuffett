## Context

SmartIPO 当前已经安装并依赖 `easyharness`，但运行时主路径仍然由项目自研协议主导：

- [src/core/agent.py](D:/Projects/PythonProjects/SmartIPO/src/core/agent.py:1) 负责项目自定义会话控制；
- [src/core/strands_runtime.py](D:/Projects/PythonProjects/SmartIPO/src/core/strands_runtime.py:1) 负责自研 Strands bridge、tool callback bridge 和事件转译；
- [src/tool/contracts.py](D:/Projects/PythonProjects/SmartIPO/src/tool/contracts.py:1)、[src/tool/framework](D:/Projects/PythonProjects/SmartIPO/src/tool/framework) 和 [src/tool/registry.py](D:/Projects/PythonProjects/SmartIPO/src/tool/registry.py:1) 负责自研工具合同与注册；
- [src/core/events.py](D:/Projects/PythonProjects/SmartIPO/src/core/events.py:1) 和 [src/core/timeline.py](D:/Projects/PythonProjects/SmartIPO/src/core/timeline.py:1) 负责自研事件流和 timeline reducer；
- [src/tui/app.py](D:/Projects/PythonProjects/SmartIPO/src/tui/app.py:1) 依赖这些自研事件与 timeline 语义；
- [src/service/model_hub.py](D:/Projects/PythonProjects/SmartIPO/src/service/model_hub.py:1) 目前返回 `strands` 运行时模型，而不是 `easyharness.ModelConfig`。

这意味着项目同时维护了两套平行结构：

```text
依赖层：
easyharness

真实主干：
SmartIPO Agent -> StrandsRuntime -> ToolSpec/Registry -> LoopEvent -> Timeline
```

这类双栈结构在短期能提高局部可控性，但在长期会形成三类系统性问题：

1. 语义重复：同一个概念在 `easyharness` 与项目内各自拥有一套定义；
2. 漂移风险：上游 SDK 已有公开 contract，项目内仍持续自造 bridge 和兼容层；
3. 迁移阻抗：TUI、未来 WebUI、自动化入口、新工具开发者必须学习项目私有协议，而不是官方主干协议。

本次变更的根本约束已经由需求明确给出：

- 不考虑后向兼容；
- 放弃自研 agent、tool contract、timeline 主机制；
- 保留 `text2text`，但只作为基础 NLP 接口；
- 整体技术架构必须彻底收敛到 `easyharness`。

这使得本次设计不应选择“兼容层长期共存”，而应选择“删除式迁移 + 单中心架构”。

## Goals / Non-Goals

**Goals:**

- 将 SmartIPO 的唯一 agent runtime 定义为 `easyharness.Agent`。
- 将 SmartIPO 的唯一工具声明和默认文件工具能力定义为 `easyharness.tool` 与官方 `build_fileglide_tools(...)`。
- 将 SmartIPO 的唯一运行时事件事实源定义为 `easyharness.AgentEvent`。
- 将模型装配层统一改造成输出 `easyharness.ModelConfig`，继续保留项目自己的集中配置与环境变量解析能力。
- 将 TUI 和未来 WebUI 收敛为 `Agent.stream()` 的消费者，而不是自研 runtime/timeline 的消费者。
- 保留 `text2text` 的独立服务价值，但切断其与 agent runtime 主干的耦合。
- 通过删除旧层和重写测试，阻止自研协议在未来回流。

**Non-Goals:**

- 不扩展 `easyharness` SDK 本身，不在本次变更中修改其站点包源码。
- 不为旧的 `ToolSpec`、`LoopEvent`、`ConversationTimeline` 提供兼容 shim。
- 不在本次变更中同时引入新的插件系统、权限系统、工作流编排系统或多 agent 编排框架。
- 不重写 `text2text` 的底层 LiteLLM 调用逻辑，除非它阻塞“与 agent runtime 解耦”的目标。
- 不把展示层本地 view-model 再上升成新的跨 UI 共享底层协议。

## Decisions

### 1. 以 `easyharness.Agent` 取代项目自研会话 runtime

运行时主入口将收敛为：

```text
composition layer
  -> easyharness.Agent(
       model=ModelConfig,
       system_prompt=...,
       tools=[...],
       enable_fileglide=False/True
     )
```

项目不再保留以下自研运行时主干：

- `src/core/agent.py`
- `src/core/strands_runtime.py`
- 基于 `StrandsRunResult` 的额外返回合同

原因：

- `easyharness` 已公开提供会话型 `run()` / `stream()` / `reset()` 语义；
- 当前自研 runtime 本质上是在复写 upstream 已经承诺的稳定表面；
- 一旦继续保留，就会把未来所有上游能力升级都变成二次桥接工程。

备选方案：

- 保留项目内 `Agent`，内部仅转调 `easyharness.Agent`。
  放弃，原因是这会继续制造第二个“伪公开入口”，让调用方继续依赖 SmartIPO 私有 runtime 名词。

### 2. 以 `easyharness.tool` 和官方 toolset 取代自研工具合同与注册表

工具层分两类处理：

- 官方文件工具：
  直接使用 `easyharness.toolset.build_fileglide_tools(default_root=...)`；
- 项目自定义业务工具：
  使用 `@easyharness.tool(...)` 装饰普通 Python 函数，并返回 `ToolOutput`、字符串或 JSON 可序列化对象。

这意味着以下项目层将被删除：

- `src/tool/contracts.py`
- `src/tool/framework/*`
- `src/tool/registry.py`
- 大部分 `src/tool/fileglide_tools.py`

保留项：

- 与业务后端耦合的具体工具实现，如 `Seedream` 调用逻辑；
- 可能需要保留少量“项目自定义工具装配清单”，但它们只负责列出工具对象，不再定义工具协议。

原因：

- `easyharness.tool` 已经把签名、参数描述、输入 schema、started/completed/failed 事件统一收束；
- 官方 fileglide toolset 已经覆盖读、搜、写、管理和 inspect 场景；
- 当前项目自研 tool framework 与其说是“业务能力”，不如说是“重复实现的一层协议”。

备选方案：

- 保留 `ToolRegistry`，但注册的对象改成 easyharness tool。
  放弃，原因是 registry 只会成为新的中间抽象，没有长期独立价值。

### 3. 以 `AgentEvent` 取代 `LoopEvent + Timeline` 的底层事实语义

新的运行时事实源是 `easyharness.Agent.stream(prompt)` 产生的 `AgentEvent`：

- `kind`: `thinking` / `tool` / `assistant` / `compress` / `system`
- `status`: `started` / `delta` / `completed` / `failed`
- `text` / `name` / `started_at` / `duration_ms` / `data`

新的边界规则：

- UI 可以在本地维护“渲染用状态”；
- 但项目不再保留一个跨 UI、跨运行时的共享 timeline reducer 核心层；
- 所有 UI 都必须以 `AgentEvent` 为输入事实，而不是消费项目自造事件类型。

原因：

- 事件流本来就是 `easyharness` 已明确设计好的公共 contract；
- 当前 timeline reducer 把“展示偏好”错误提升成了“底层事实协议”；
- 一旦保留它，未来 WebUI 仍会被迫学习 SmartIPO 私有事件模型。

备选方案：

- 把现有 `ConversationTimeline` 改造成 `AgentEvent` reducer。
  放弃，原因是这仍然保留了一套跨 UI 核心展示协议，和“完全依赖 easyharness 事件流”目标冲突。

### 4. 引入单一 composition layer，集中定义模型、prompt、工具和 workspace root

应用装配层将成为唯一允许知道以下信息的模块：

- 默认 system prompt；
- `ModelConfig` 来源；
- 默认工具列表；
- `build_fileglide_tools(default_root=...)` 的 root；
- 自定义业务工具集合；
- 供 TUI / future WebUI 调用的 agent factory。

UI 层只接收：

- `Agent` 实例，或
- 一个明确的 `build_default_agent()` 工厂。

原因：

- 当前 TUI 持有过多运行时装配知识；
- 若未来增加 WebUI、CLI automation、service mode，不应复制装配逻辑；
- composition layer 是保留项目“业务选择权”的合理位置，也是架构上最接近 Facade 的位置。

备选方案：

- 让每个入口自己各写一份 agent 装配。
  放弃，原因是会立即形成 prompt、tool set、model config 和 root 语义漂移。

### 5. 保留 `text2text`，但彻底降级为基础服务

`text2text` 的保留策略是：

- 它仍然可以作为项目内部的独立 NLP/文本生成接口存在；
- 它可以被某些业务工具、预处理步骤或离线服务使用；
- 但它不再承担 agent runtime、tool context、事件流、session loop、默认主脑模型等职责。

新的架构定位：

```text
Business tool / NLP helper
  -> text2text

Agent runtime
  -> easyharness.Agent
```

原因：

- 用户明确要求保留 `text2text`；
- 它与“自研 agent 主链”是两个不同层级的概念；
- 彻底删除会丢失一个可复用的基础服务，但继续让它处于主脑路径会破坏边界。

备选方案：

- 将 `text2text` 直接改造成 `easyharness` 的模型底座。
  放弃，原因是那会重新制造项目私有 runtime bridge。

### 6. 采用删除式迁移，不引入长期兼容层

迁移策略明确分两阶段：

1. 新链路搭建并验证通过；
2. 旧链路删除、测试重写、导入路径收敛。

不会存在的内容：

- `legacy_runtime.py`
- `compat_tool_registry.py`
- `loop_event_adapter.py`
- `timeline_bridge.py`

仅允许存在短生命周期、同一变更内即删除的过渡代码，不允许为“也许以后还要用”保留旧名词。

原因：

- 需求已明确“不考虑后向兼容”；
- 长期兼容层只会降低删除旧系统的执行决心；
- 对内部架构迁移而言，最危险的是“逻辑已切换，但旧概念还留在目录里继续误导后续开发者”。

备选方案：

- 先做新旧双栈，再慢慢收敛。
  放弃，原因是这更适合对外 API 迁移，不适合当前内部架构重置。

## Risks / Trade-offs

- [Risk] `easyharness.AgentEvent` 没有当前 `LoopEvent` 那样细粒度的 `tool_attempt_started` / `tool_attempt_failed` 二段式语义  
  → Mitigation：接受这是上游公共 contract 的边界，UI 改为围绕 `started/completed/failed` 设计，不再要求项目私有更细阶段。

- [Risk] 官方 fileglide tool 名称与当前项目内 `text.read`、`file.list` 等命名不同，会导致测试和 prompt 需要同步调整  
  → Mitigation：在 composition layer 中统一定义默认工具集和 prompt 文案，一次性改完，不保留别名。

- [Risk] 删除 `ConversationTimeline` 后，TUI 需要重写本地展示状态管理  
  → Mitigation：把 view-model 严格限制在 UI 文件内，只围绕显示需要实现最小状态，不重新抽象成跨层协议。

- [Risk] 当前测试大量耦合 `ToolSpec`、`StrandsRunResult`、`LoopEvent`，迁移时会出现测试大面积失效  
  → Mitigation：接受测试重写是迁移的一部分，优先重建“新主干正确性”门禁，而不是修补旧测试。

- [Risk] `text2text` 仍保留时，后续开发者可能再次把它拉回 agent 主链  
  → Mitigation：通过规格文档和目录职责明确禁止这种耦合，并在实现中移除所有旧调用路径。

- [Risk] 上游 `easyharness` SDK 后续升级可能改变公开字段细节  
  → Mitigation：项目只依赖其公开导出 `Agent / ModelConfig / AgentEvent / ToolOutput / tool` 和官方 toolset，禁止直接依赖 `_internal` 私有实现。

## Migration Plan

1. 调整模型装配层，使其输出 `easyharness.ModelConfig`，并保留项目既有配置中心与环境变量解析规则。
2. 新建或重写 composition layer，集中装配 system prompt、默认工具集、workspace root 和自定义业务工具。
3. 将自定义工具逐步迁移为 `@easyharness.tool` 风格，并用 `ToolOutput` 表达结构化结果。
4. 用官方 `build_fileglide_tools(default_root=...)` 取代项目自研 fileglide tool specs。
5. 重写 TUI，使其直接消费 `agent.stream()` 事件流并在 UI 本地维护渲染状态。
6. 删除 `src/core/agent.py`、`src/core/strands_runtime.py`、`src/core/events.py`、`src/core/timeline.py`、`src/tool/contracts.py`、`src/tool/framework/*`、`src/tool/registry.py` 及相关旧测试。
7. 重写测试门禁，覆盖新的 agent 装配、工具调用、事件流展示和 `text2text` 保留边界。
8. 复查文档、入口脚本与 prompt，确认仓库中不再残留旧 runtime 名词和旧导入路径。

回滚策略：

- 本次迁移是内部破坏性重构，不设计长期并行回滚机制；
- 若实施中某个切片失败，回滚方式应是回退该切片的代码提交，而不是在主干内保留旧 runtime 兼容层。

## Open Questions

- TUI 本地 view-model 是否需要单独拆成一个仅供 UI 使用的小模块，还是直接保留在 `src/tui/app.py` 内部；这属于实现期的组织选择，但不能上升成新的跨层协议。
- 默认 `enable_fileglide` 应设为 `False` 再显式注入官方 toolset，还是设为 `True` 并仅附加业务工具；前者更显式，后者更简洁，建议实施前做一次最小验证后定案。
- `text2text` 是否还有现存调用方依赖其流式接口返回生成器；如果有，需要在实现阶段补一轮调用点梳理，避免迁移时误删业务用途。
