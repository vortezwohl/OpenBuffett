## Context

这轮变更同时涉及 `src/tui/app.py` 和 `src/agent.py` 两个集中装配点，但都属于边界清晰的 UI / runtime 默认配置调整，不需要下沉到业务工具或底层 provider 适配层。当前工具活动主行和 compression 活动都由 TUI 本地 `_TimelineItem` 渲染体系负责；默认模型上下文预算和 conversation manager 保留策略则由 `build_default_agent()` 统一装配。

问题本质上分成两类：

- 展示层问题：工具活动主行当前使用高亮绿色和白色硬编码，并额外拼接 `{}` 语法块，视觉上过亮且扫描噪音偏高。
- 生命周期问题：compression 事件当前按“每个事件直接追加一条时间线项”的方式处理，导致 `started` 和终态事件拆成两条消息，并且 `started` 项的本地计时不会被收口。

此外，当前默认模型配置没有显式设置 `context_window_limit`。对 `openai/deepseek-v4-pro` 这类不在 `strands` 预置窗口表中的模型，EasyHarness 会回退到 200,000 token 默认值，因此即使我们想把 compression 预算调高到 900,000，也必须在本项目装配层显式覆盖。

## Goals / Non-Goals

**Goals:**

- 让工具活动主行形成更克制的次级色层级，同时保留状态标签和普通文本的可区分性。
- 移除工具主行中的 `{}` 字符，但保留稳定、可扫读的文本结构。
- 让一次 compression 在本地时间线中始终对应同一条 `_TimelineItem`，并在成功时收口为单条 `Conversation compressed` 消息。
- 显式把默认上下文窗口预算提升到 900,000 token，并把保留消息数调整为 6，确保主动压缩预算符合预期。
- 把所有行为变化落实到可测试的文本断言和必要的样式断言上。

**Non-Goals:**

- 不修改 EasyHarness / Strands 的上游实现，不改第三方库源码。
- 不重做整套 TUI 主题系统，不引入新的主题配置文件或颜色 token 框架。
- 不扩展 compression 事件协议字段；只消费现有 `started_at`、`duration_ms`、`status` 和 `text` / `data`。
- 不改变工具详情下挂行的整体语义，只调整工具主行和 compression 主行行为。

## Decisions

### 1. 工具主行继续保留分段渲染，但取消括号语法块

决策：继续使用 Rich `Text.append()` 分段渲染工具活动主行，而不是退回整行纯文本；同时去掉 `{ ` 和 ` }` 两段，改为 `duration 路 Tool <name> 路 <status>`。

原因：

- 你的需求不是简单删字符，而是“删掉括号后仍保持 Tool / 状态标签和普通文本不同色”，这要求继续使用分段样式而不是整行统一着色。
- 当前实现已经把 `Tool`、工具名、状态、摘要拆成多个 span，局部调整成本最低。
- 去掉括号后，主行结构仍可依赖固定分隔符 ` 路 ` 保持扫描稳定性。

备选方案：

- 保留括号但把颜色调暗。  
  不采用，因为这没有满足你明确提出的“删掉 { 和 }”要求。

- 把整行主文本统一成一个样式，只给状态加粗。  
  不采用，因为这会丢掉 `Tool` 和状态标签与普通工具名之间的结构层级。

### 2. 颜色调整限定在工具主行 span 常量，不扩散到全局主题

决策：只新增或调整工具主行相关样式常量，例如工具标签 / 状态标签的次级绿色、工具名摘要的次级浅色；不连带修改 Header、聊天前缀或 thinking 历史的既有颜色规则。

原因：

- 本轮需求只指向 tool call 颜色，不应顺手扩散成整套主题重做。
- 当前 TUI 已经存在多个语义颜色常量，工具主行可以局部替换，不需要引入新的全局主题抽象。
- 这样可以把变更控制在当前任务边界内，减少无关回归。

备选方案：

- 顺手统一所有绿色系常量。  
  不采用，因为这会把需求从局部样式修正扩散成主题重构。

### 3. compression 事件改为“单活动项收口”，模式对齐 tool 生命周期

决策：compression 事件不再每次都 `_append_item()`；而是像 tool 一样在 `started` 时创建活动项，在 `completed` / `failed` / `cancelled` 时回填同一条 item，结束时清理 `started_at`。

原因：

- 当前 bug 的根因是事件处理模式错误，不是文案错误。只改 `_compress_activity_text()` 无法消除双消息和残留计时。
- tool 活动已经有成熟的“started 创建、终态回填”模式，compression 可以复用这一思想，避免再造一套不同生命周期。
- 单项收口后，时间线语义更准确：一次 compression 就是一条活动，而不是两条相互独立的消息。

备选方案：

- 保持双消息，只在 UI 层隐藏 `started` 行。  
  不采用，因为隐藏并不会终止该 item 的本地计时，也会让内部状态继续失真。

- 在刷新时特判 compress started 项，把它替换成 completed 文案。  
  不采用，因为这会把事件驱动逻辑变成渲染时修补，状态一致性更差。

### 4. 仅成功 compression 使用精确文案 `Conversation compressed`

决策：successful compression 终态文案精确使用 `Conversation compressed`；失败和取消分别继续显示失败/中断语义，不伪装成成功。

原因：

- 用户明确要求成功后的单条消息文案为 `Conversation compressed`。
- 如果把所有终态都收口成这句，会错误掩盖失败事实，违反项目的零信任和真实状态输出约束。
- 将“单条消息”与“真实终态”同时保留，是满足体验与正确性的最小闭环。

备选方案：

- 延续当前 `Context compressed.`。  
  不采用，因为与用户要求不一致。

- 不论成败都统一成 `Conversation compressed`。  
  不采用，因为这会伪造成功状态。

### 5. 上下文预算在项目装配层显式设置 900,000 token / 6 条保留消息

决策：在 `build_default_model_config()` 中显式设置 `context_window_limit=900_000`，并在 `EventingSummarizingConversationManager` 中将 `preserve_recent_messages` 设为 6。

原因：

- 对当前模型 ID，库内查表无法得到真实 context window，若不显式覆盖就会继续使用 200,000 默认值。
- 这两个值都是本项目默认策略，不属于第三方库通用逻辑，最合理的放置位置就是本项目 agent composition 层。
- 只改 `preserve_recent_messages` 而不改 `context_window_limit` 会造成“文档写 90 万，运行时实际仍按 20 万”的伪配置。

备选方案：

- 只改 `preserve_recent_messages=6`。  
  不采用，因为主动压缩触发阈值仍会受 200,000 默认窗口限制。

- 修改第三方默认表或 conversation manager 默认常量。  
  不采用，因为这会修改库行为边界，超出当前仓库任务范围。

## Risks / Trade-offs

- [Risk] 去掉 `{}` 后，工具主行少了一层强语法块包裹，若颜色层级处理不够清晰，可能导致扫描性下降。  
  → Mitigation：保留 `Tool`、工具名、状态三段独立 span，并用测试断言固定最终文本结构。

- [Risk] compression 归并成单条活动项后，如果 started 和终态事件关联键处理不稳，可能出现终态找不到 started 项而再次回落成双条。  
  → Mitigation：为 compression 引入单独的活跃项追踪键，并补充 started→completed、started→failed 两类测试。

- [Risk] 把 `context_window_limit` 提高到 900,000 会降低主动压缩触发频率，可能让单轮输入更晚才开始压缩。  
  → Mitigation：这正是目标策略的一部分，同时保留 `preserve_recent_messages=6` 作为最小上下文保护，避免压缩过度。

- [Risk] 旧测试快照会大面积因文本变化失效。  
  → Mitigation：集中更新 `test/test_tui_app.py` 中相关断言，优先验证真实新合同而不是兼容旧字符串。

## Migration Plan

1. 先调整 `src/agent.py` 中默认 `ModelConfig` 和 conversation manager 参数，建立新的压缩预算基线。
2. 再修改 `src/tui/app.py` 中工具主行 renderable / 纯文本渲染逻辑，去掉括号并切换颜色常量。
3. 然后重构 compression 事件处理为“started 建项、终态收口”的单活动项模式，并更新成功文案为 `Conversation compressed`。
4. 最后同步更新 `test/test_tui_app.py`，覆盖工具主行文本、compression 收口行为和预算配置相关断言。

回滚策略：

- 这是纯代码路径和默认值调整，无数据迁移。
- 若上线后 UI 可读性或压缩行为不符合预期，可通过回滚对应提交恢复旧逻辑。

## Open Questions

- 当前无阻塞性开放问题。
- 若实现阶段发现 `Conversation compressed` 是否需要带句号会与现有快照风格冲突，以用户明确给出的文案为准，优先不带句号。
