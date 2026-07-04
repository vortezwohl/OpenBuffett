## Context

当前问题出现在两层交界处：

- EasyHarness runtime 负责把底层 `tool_stream` 事件聚合成公开 `AgentEvent(kind="tool")`
- `src/tui/app.py` 负责把这些公开事件映射为本地 `_TimelineItem`

现场现象是：同一批 tool call 中，第一条工具活动会残留为 `Running`，其计时不断增长，而后面又会出现一条对应的 `Done` 行。根因分析表明，现有 runtime 只用单个“当前 tool”槽位跟踪活动中的工具阶段；当同批次第二条 tool started 事件到来时，会覆盖前一条活动状态，使前一条终态事件无法再稳定收口到原始 timeline 项。

约束条件：

- 用户可见行为必须真实，不能用“隐藏 Running 行”伪装修复。
- 现有 TUI 已依赖 `tool_use_id`、工具名和局部 started_at 做关联，不宜把全部容错压力压给展示层。
- 取消、失败、同名工具重复调用都必须沿用同一套生命周期规则，不能只修成功路径。

## Goals / Non-Goals

**Goals:**

- 让同一条工具调用从 `started` 到 `completed` / `failed` / `cancelled` 始终关联到同一条 timeline 项。
- 支持同批次多个 tool call 连续或重叠出现时的稳定收口，不再让第一条工具活动被后续 started 事件覆盖。
- 让同名工具重复调用时也能稳定区分不同调用实例。
- 为上游字段异常保留最小兜底逻辑，避免残留持续计时的孤儿 `Running` 项。
- 用回归测试覆盖首条工具残留、同名重复调用、取消收口三类场景。

**Non-Goals:**

- 不重做整个 EasyHarness 事件协议，也不改动底层工具执行器输出格式。
- 不改变工具活动的可见文案、配色或摘要规则，除非为验证修复不可避免。
- 不把 tool timeline 改成多行详情面板或引入新的 UI 组件。

## Decisions

### 1. 主修放在 runtime：单槽 `self._tool` 改为按 `tool_use_id` 跟踪多活跃工具

决策：把 EasyHarness runtime 中“当前工具阶段”的单槽跟踪改成基于 `tool_use_id` 的活跃工具表；started 事件入表，终态事件按 `tool_use_id` 出表并生成公开 `AgentEvent`。

原因：

- 根因在 runtime 聚合层，而不是 TUI 渲染层。若公开事件已经错绑，TUI 无法可靠恢复真实归属。
- 单槽模型只适合严格串行的工具流，不适合同批次多个 tool started 先后交错的情况。
- `tool_use_id` 已由工具执行器稳定产出，是当前最可靠的调用实例标识。

备选方案：

- 只在 `_complete_tool_phase()` 中优先信任终态 `tool_event` 字段，不引入活跃表。
  不作为最终方案，因为虽然能缓解错绑，但仍无法完整表达“当前同时存在多条活动工具”的状态，也会让取消场景只能收口最后一条。
- 只修 TUI 关联逻辑。
  不采用，因为这只能掩盖公开事件错误，不能保证终态语义真实。

### 2. TUI 保留最小兜底：在严格键匹配失败时，再按运行中同名项或 started_at 回绑

决策：`src/tui/app.py` 中继续优先按 `tool_use_id` 精确关联；若精确匹配失败，再尝试把终态事件回绑到“仍在运行的同名工具项”或 started_at 匹配项，最后才新建孤立终态项。

原因：

- runtime 修复后，TUI 大多数情况下不会触发兜底；但保留兜底能吸收少量脏事件或兼容边缘 provider 行为。
- 兜底必须保守，避免把不同调用误绑到同一项。
- 只有在原始运行项仍为 `started_at is not None` 时才允许回绑，减少错绑概率。

备选方案：

- 完全移除 TUI 兜底，要求上游事件永远完美。
  不采用，因为一旦未来 provider 或 runtime 引入新边界事件，UI 仍会出现残留 Running 项。

### 3. 取消收口改为遍历全部活跃工具，而不是只结束“最后一条”

决策：runtime 在 cancelled 结果路径下，不再只依赖单个当前工具状态，而是收口所有尚未完成的活跃工具项，并按各自 started 信息生成 cancelled 公开事件。

原因：

- 单槽模型下取消只会结束最后一个工具，前面的工具即使仍在运行列表里也会被遗漏。
- 用户观察到的“计时停不住”在取消路径上会更明显，因此必须纳入同一套修复。

备选方案：

- 取消时统一让 TUI 本地强制 stop 所有 tool 项。
  不采用，因为这会让 runtime 与公开事件流状态失真，测试也无法稳定验证。

### 4. 回归测试按“事件交错”而非单一成功路径组织

决策：新增覆盖以下路径的测试：

- `started(A) -> started(B) -> completed(A) -> completed(B)`
- 两条同名工具调用的 started/completed 交错
- 工具 started 后收到 cancelled
- TUI 在异常终态匹配下优先回绑运行中同名项，不残留持续计时项

原因：

- 现有测试几乎只覆盖“单条 started 紧接单条 completed”的理想路径，无法暴露首条工具残留问题。
- 本问题本质是生命周期交错问题，测试必须直接复现交错顺序。

## Risks / Trade-offs

- [Risk] runtime 改成多活跃工具表后，若出表条件写错，可能导致终态重复发射或活跃表泄漏。
  → Mitigation：以 `tool_use_id` 作为唯一键，终态路径统一 pop，取消路径验证表清空。
- [Risk] TUI 兜底过于激进时，可能把不同同名工具误绑到同一条 timeline 项。
  → Mitigation：兜底只在精确键失败且目标项仍在运行时触发，并优先匹配 started_at，再匹配同名运行项。
- [Risk] 修改 runtime 可能影响既有取消语义或其它 phase 的收口顺序。
  → Mitigation：测试只聚焦 tool phase，不改变 thinking / assistant 收口协议，并增加 cancelled 场景回归。

## Migration Plan

1. 先修改 EasyHarness runtime 的工具阶段跟踪结构与终态收口逻辑。
2. 再调整 `src/tui/app.py` 的 tool 终态关联兜底逻辑。
3. 补充 runtime/TUI 回归测试，先复现首条 tool 残留，再验证修复通过。
4. 本地运行相关测试集，确认没有新的重复 tool 行或残留 Running 项。

回滚策略：

- 若 runtime 变更引入更广泛的 tool 事件回归，可整体回滚本次 change，恢复单槽模型与旧 TUI 兜底逻辑。
- 因为本次变更不涉及数据迁移，回滚只需恢复代码与测试。

## Open Questions

- 当前仓库是否直接维护 EasyHarness runtime 兼容层源码，还是需要以本仓库 vendor/适配方式覆盖 site-packages 行为；实现前需要确认落点。
- 若极端情况下终态事件缺失 `tool_use_id` 且同批次存在多个同名运行项，是否接受 TUI 仅按最早运行项保守回绑；当前建议接受，但必须在 design 执行时记录这一限制。
