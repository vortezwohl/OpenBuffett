## Context

当前 `unify-conversation-timeline` 已经把运行时事件归约成统一时间线状态，但实现里仍然混入了展示层职责：

- `src/core/strands_runtime.py` 在工具事件中附带 `display_name` 和面向用户的提示文案。
- `src/core/timeline.py` 负责把工具类别和展示名拼成标题。
- `src/tui/app.py` 只消费已经被加工过的标题和文案，缺少对运行中工具条目的明确可见性策略。

这导致两个问题：

1. core 和 UI 边界不干净，后续 WebUI 也会被同一套展示决策绑住。
2. TUI 对快速工具的运行态可见性没有硬保证，事件即使流到了界面，也可能因为开始和结束太快而让用户看起来像“没显示”。

约束很明确：

- 不考虑后向兼容。
- 底层不插手 UI 层的展示细节。
- 保留 `llm.py` / `text2text` 等既有非本次范围内容，不顺手扩散。

## Goals / Non-Goals

**Goals:**

- 让 core 时间线和 runtime 只暴露原始语义状态，不再输出展示标题、展示名和用户提示文案。
- 让 TUI 独立决定工具名称、状态、结果和 thinking/tool activity 的视觉呈现。
- 让 TUI 在工具执行期间稳定显示运行中 timeline 和计时，快速工具也至少可见一次运行态。
- 用测试固定住新的职责边界和可见性行为。

**Non-Goals:**

- 不实现 WebUI。
- 不重新设计整个事件系统。
- 不引入新的 presenter、view-model 层或额外依赖。
- 不保留旧事件字段和旧时间线字段的兼容分支。

## Decisions

### 1. Core 事件只保留语义字段

`strands_runtime` 发出的 `tool_started` / `tool_completed` / `tool_failed` 事件只保留：

- `tool_name`
- `tool_kind`
- `duration_ms`
- `result_preview`
- `result_detail`
- `collapsible`
- `collapsed_by_default`
- 失败时的原始错误文本

不再下发 `display_name`、`message` 这类直接面向 UI 的字段。

原因：

- 这些字段本质是展示决策，不是运行时语义。
- 同一条事件在 TUI 和未来 WebUI 中可能需要完全不同的展示方式。

备选方案：

- 保留 `display_name` 但约定 UI 可忽略。放弃，原因是底层继续越界，而且调用方很容易继续依赖它。

### 2. ConversationTimeline 只做状态归约，不做标题格式化

`ConversationTimeline` 只维护条目状态和原始元数据，不再负责：

- 工具类别中文标签转换
- 工具标题拼接
- 展示文案组装

工具条目里保留原始 metadata，例如：

- `tool_name`
- `tool_kind`
- `error`

原因：

- timeline 是跨 UI 复用的状态层，最稳定的契约是语义字段，不是格式化字符串。

备选方案：

- 在 timeline 增加“默认标题生成器”。放弃，原因是这仍然是在 core 做 UI 工作，只是换了一个接口名。

### 3. TUI 负责工具条目的完整展示逻辑

`src/tui/app.py` 负责：

- 工具标题和副标题怎么显示
- 状态标签文案
- 结果概要和详细结果的折叠呈现
- thinking 动画
- 工具运行态的最小可见时长策略

推荐的最小规则：

- 收到 `tool_started` 后立刻渲染运行中条目并开始计时。
- 收到 `tool_completed` / `tool_failed` 后，如果该工具运行时间低于最小可见阈值，则延迟界面上的完成态更新，先保证用户看见一次运行中状态。

原因：

- “用户是否能看到”是纯 UI 问题，应该在 UI 层解决。
- 用一个很小的阈值就够，不需要改 runtime 节奏。

备选方案：

- 在 runtime 人为 sleep 或缓冲工具完成事件。放弃，原因是底层会被 UI 体验绑架，污染所有消费者。

### 4. 测试改成验证“中途可见”而不是只看最终态

测试需要新增两类断言：

- core 测试：确认不再输出 UI 文案字段，只保留语义字段。
- TUI 测试：在工具尚未完成时检查聊天时间线里已经有运行中的工具条目和时长；快速工具完成时检查运行态至少出现过一次。

原因：

- 现在的问题能漏过去，就是因为测试只看“最后有没有结果”。

## Risks / Trade-offs

- [风险] 去掉 `display_name` / `message` 后，现有 TUI 渲染会立刻坏掉。  
  → Mitigation: 同一轮里先收紧 core 契约，再把 TUI 渲染切到 metadata 驱动，不保留混合状态。

- [风险] 最小可见时长如果过大，会让界面显得迟钝。  
  → Mitigation: 阈值保持很小，只用于视觉完成态，不阻塞真实工具执行。

- [风险] 事件字段收缩后，后续 WebUI 若直接复用旧字段会失效。  
  → Mitigation: 本轮明确不考虑后向兼容，并在 spec 中把新契约写死。

## Migration Plan

1. 收紧 `strands_runtime` 工具事件字段，删掉展示层字段。
2. 收紧 `ConversationTimeline`，改为只保存语义状态和 metadata。
3. 调整 TUI 渲染逻辑和本地最小可见时长策略。
4. 更新单元测试，先覆盖 core 契约，再覆盖 TUI 中途可见性。

回滚策略很简单：整轮回滚该 change；不做兼容桥接。

## Open Questions

- TUI 的工具标题最终是显示原始 `tool_name`，还是显示 `[tool_kind] tool_name`。这属于 UI 细节，实现时选一个最直接且稳定的版本即可。
- 最小可见时长阈值取 150ms 还是 250ms。实现时按最小不突兀原则定一个固定值即可，不需要抽配置。
