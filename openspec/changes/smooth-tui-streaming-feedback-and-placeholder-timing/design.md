## Context

当前 `src/tui/app.py` 直接消费 `EasyHarness` 事件流，并把 `thinking`、`tool`、`assistant`、`compress` 的显示状态落在同一套本地时间线条目里。现状有三个结构性问题：

- 文本显示层与原始事件层没有分离，`thinking` 与 `assistant` 的 `delta` 一到就整块追加，无法稳定实现逐字符显示。
- waiting placeholder 只是一条临时 timeline item，没有“最短可见时长”或“覆盖前缓冲”语义，因此首个真实事件来得足够快时会直接把 placeholder 抹掉。
- turn 完成条件仍以“agent 原始流结束”为准，而不是以“显示层已经排空”为准，因此只要后续引入 reveal 缓冲，就会出现内部结束早于用户可见输出结束的错位。

这次设计必须在不修改 `EasyHarness` 事件协议、不中断既有 tool/compress/assistant 时间线模型的前提下，为 TUI 增加一层明确的显示调度语义。同时要满足新的硬约束：全局刷新固定为 `10ms`，thinking 动画帧固定为 `100ms`。

## Goals / Non-Goals

**Goals:**

- 为 `thinking` 和 `assistant` 增加统一的显示层 reveal 通道，使文本能按 `10ms/char` 顺序吐出。
- 为本地 `Thinking ...` placeholder 增加 `50ms` 最短可见时长，并保证首个真实动作在阈值前到达时不会立刻覆盖它。
- 为 turn 增加“原始流完成”和“显示层完成”两阶段判定，确保 timeline 不会提前收尾。
- 统一刷新与动画节拍：全局刷新 `10ms`，thinking 动画帧 `100ms`。
- 保持现有 thinking history / tool / compress 的视觉模型与时间线结构可延续，只在必要处扩展本地状态机。

**Non-Goals:**

- 不修改 `src/agent.py` 或 `EasyHarness` 发出的事件结构、事件顺序和 token 切分方式。
- 不改变 tool、compress、assistant 既有业务语义，只调整显示层调度与时间线收尾时机。
- 不把最终 assistant 回复改造成多行版式重设计；本次只解决字符 reveal、newline 规范化和 waiting feedback 生命周期。
- 不引入新的线程、外部依赖或独立动画框架。

## Decisions

### 决策 1：拆分“原始事件层”和“可见输出层”

TUI 继续按现有方式在 worker 线程中消费 `self._agent.stream(prompt)`，但不再把所有文本类事件直接同步成最终可见文本，而是拆成两层：

- 原始事件层：负责记录 tool/compress/assistant/thinking 的权威状态变化、起止时间和原始终态。
- 可见输出层：负责字符 reveal、placeholder 最短存活、延迟覆盖和最终排空后 turn 收尾。

这样能避免把 `sleep` 塞进事件线程，也避免为了“顺滑显示”篡改原始时间线语义。

备选方案：
- 直接在 `_apply_thinking_event` / `_apply_assistant_event` 中 `sleep(10ms)` 逐字追加。  
  放弃原因：会阻塞 worker 或 UI 主线程，拖慢 tool/compress 状态更新与取消响应。

### 决策 2：为文本类事件引入 reveal 队列

对 `thinking delta/completed` 与 `assistant delta/completed`，显示层维护一个按到达顺序排队的 reveal 队列。每个队列项至少包含：

- `turn_id`
- `target_kind`（`thinking_history` 或 `assistant_reply`）
- `text`
- `is_terminal`
- `terminal_status`

队列中的文本在入队前先做显示层规范化：

- `thinking`：把 `\r\n`、`\r`、`\n` 统一替换为空格，再收敛重复空白，禁止原样换行进入时间线。
- `assistant`：同样走逐字符 reveal，但是否做换行净化应以当前需求为准；本 change 只把逐字符 reveal 强制到位，不强制改 final reply 的多行语义。

每次 `10ms` 刷新 tick 最多消费一个字符并推进到对应 timeline item，直到队列清空。

备选方案：
- 按 token 块 reveal，而不是按字符。  
  放弃原因：用户要求明确是逐 `char` 输出；按 token 仍会出现大块跳变。

### 决策 3：placeholder 覆盖改为“最短可见 + 延迟回放”

本地 `Thinking ...` placeholder 在 turn 启动时创建，并记录 `min_visible_until = now + 50ms`。当首个会覆盖 placeholder 的真实事件（`thinking started/delta/completed`、`tool started`、`assistant started/delta/completed`、`compress started`）在阈值前到达时：

- 不立刻应用覆盖动作；
- 而是把该事件放入“待回放事件队列”；
- 等 `50ms` 窗口结束后，再按原始到达顺序回放这些事件。

这让 placeholder 至少被用户真正看到一次，同时不丢失事件顺序。

备选方案：
- 让 placeholder 与真实动作并存 `50ms`。  
  放弃原因：时间线会重复显示两个运行态，语义混乱，也违背“动作出现时覆盖自己的 thinking placeholder”的既有约束。

### 决策 4：turn 完成改为“双门闩”模型

turn 不能再只依赖 `_run_turn_worker` 结束后立即 `_complete_turn`。需要拆成：

- `raw_stream_done`：agent 原始事件流已经结束；
- `display_drain_done`：待回放事件队列为空、reveal 队列为空、挂起的文本终态已提交、没有还需要回补的 waiting placeholder 切换。

只有两个条件同时满足，当前 turn 才允许真正进入 `_complete_turn` / `_finish_active_turn`。

这样才能保证“用户看到的最后一个字符”和“turn 真正结束”一致。

备选方案：
- 保持当前 `_run_turn_worker -> _complete_turn` 直连，只在 `_complete_turn` 前强制 flush 当前 item。  
  放弃原因：无法处理跨多个 delta 的 reveal backlog，也无法覆盖 placeholder 延迟回放。

### 决策 5：全局刷新固定 `10ms`，动画帧独立取 `100ms`

按照你的补充要求，全局刷新间隔统一固定为 `10ms`，不做按需调速。运行中时间线的时长刷新、reveal 消费、延迟事件回放检查都共用这一时钟。

thinking 动画不再使用 `300ms`，而是改为基于同一运行时长计算 `100ms` 一帧的 `.` / `..` / `...`。动画仍然从现有 `duration_ms` 派生，不新增单独 animation timer。

备选方案：
- 维持低频全局刷新，额外为 reveal 加独立 timer。  
  放弃原因：虽然更省 CPU，但与你明确要求的“全局 10ms”不一致，也会把本次设计拆成两套节拍来源。

### 决策 6：把 thinking 文本净化放在显示层入口，而不是渲染层出口

`thinking` 文本中的换行控制不能等到 `_render_thinking_history_renderable` 再清理，否则：

- reveal 队列里仍然会带着脏字符；
- 文本合并逻辑会把不可见控制字符算进内容；
- 测试也无法准确断言“历史文本内部根本不存在 `\r/\n`”。

因此规范化必须在 reveal 入队前完成，并保证 `_merge_thinking_text` 处理的是已经净化过的字符串。

备选方案：
- 只在最终渲染时把 `\r/\n` 替换为空格。  
  放弃原因：状态与渲染看到的文本不一致，后续排查会更难。

## Risks / Trade-offs

- [全局 `10ms` 刷新提高 CPU 唤醒频率] → 通过测试覆盖活跃 turn 与空闲态，确保即使全局节拍固定，空闲时刷新逻辑仍然是轻量级 no-op。
- [显示层队列让 turn 生命周期更复杂] → 用显式字段区分 `raw_stream_done`、待回放事件、reveal backlog、挂起终态，避免把状态塞回 `metadata` 的模糊组合。
- [逐字符 reveal 可能改变已有测试的完成时机] → 所有与 `assistant` / `thinking` 收尾相关的测试都改成等待显示层排空，而不是假设事件一到文本就完整出现。
- [placeholder 最短可见时长可能让极快 tool 出现轻微延后] → 把该延后限定在首个覆盖动作的 `50ms` 窗口内，且仅影响显示层，不影响真实耗时统计。

## Migration Plan

- 仅修改 `src/tui/app.py` 与 `test/test_tui_app.py`，不涉及外部配置迁移。
- 先引入显示层队列与 turn 双门闩，再接入 placeholder 最短可见逻辑，最后统一刷新与动画常量，避免一次改动多个时序源。
- 若实现阶段发现 `assistant` 的换行语义必须保持多行，可只对 `thinking` 强制净化，并在实现说明中明确该边界。

## Open Questions

- 当前需求已经明确要求 `thinking` 禁止任何 `\r/\n`，但没有同样强制要求最终 assistant 回复也去换行。本方案默认 assistant 只做逐字符 reveal，不额外压平换行；若你后续希望 assistant 也变成单行，需要在实现前再扩一条 spec。
