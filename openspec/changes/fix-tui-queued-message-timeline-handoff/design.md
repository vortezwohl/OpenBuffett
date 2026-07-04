## Context

当前 `AgentWorkbenchApp` 的队列提交流程把一条用户消息同时放进了两套状态语义：

- 在 `_pending_turns` 中，它是“尚未正式发出、等待处理的提交”；
- 在 `_items` 中，它又已经是一条 `kind="user"` 的 timeline 会话项，只是当 `queue_state == "queued"` 时被 `_visible_timeline_items()` 隐藏。

这种“双重建模”会导致排队消息进入执行态时没有真正新增一条会话事件，而只是把旧的隐藏项重新显示出来。结果是：

- queue tray 中的消息会先消失；
- 主 timeline 底部不一定出现新的 `User >`；
- 消息的可见位置取决于最初提交时插入 `_items` 的位置，而不是正式开始执行的时间顺序。

这个问题集中在 `src/tui/app.py` 的本地状态层，不需要改 EasyHarness runtime、工具协议或事件格式。

## Goals / Non-Goals

**Goals:**

- 让 queue tray 与 timeline 拥有单一且清晰的职责边界。
- 让排队消息只在“正式开始执行”时进入主 timeline。
- 让第二条及后续排队消息在开始执行时，以新的 `User >` 会话项出现在正确的时间位置。
- 让失败、取消、继续下一条等队列推进路径共享同一套 handoff 语义。
- 用回归测试覆盖“排队中不可见”“开始执行时新增”“顺序正确”三类关键行为。

**Non-Goals:**

- 不改动 EasyHarness runtime 的 turn、tool、assistant 事件协议。
- 不重新设计 queue tray 的视觉样式或聊天视觉语言。
- 不引入排队项重排、取消单条排队消息或优先级控制。

## Decisions

### 1. 彻底拆分 queue tray 与 timeline 的数据语义

决策：排队中的用户提交只保存在 `_pending_turns`，不再在 `_enqueue_turn()` 时提前创建 `_TimelineItem(kind="user")`。

原因：

- 这能消除“同一条消息同时存在于待处理队列和 timeline”的双份真相。
- queue tray 显示“待发”，timeline 显示“已正式进入会话处理”，两者职责可以自然分开。
- 一旦移除 queued user item，timeline 的可见性逻辑无需再依赖 `queue_state == "queued"` 的隐藏规则。

备选方案：

- 保留当前模型，只在开始执行时把旧 user item 移动到 `_items` 末尾。
  不采用，因为这仍然保留了“双重建模”，只是把“隐藏项复活”改成“隐藏项搬家”，状态含义依旧混乱。

### 2. 把“正式发出用户消息”定义为 turn 启动时的显式落盘动作

决策：在 `_start_next_turn_if_idle()` 中，当某个 `_PendingTurn` 成为 active turn 时，才 append 一条新的 `User >` timeline 项，并把该 item key 绑定到 active turn。

原因：

- 这使 timeline 真正遵守事件发生顺序，而不是提交顺序。
- 用户能稳定看到“queue tray 消失”与“主 timeline 新增 `User >`”这两个连续动作。
- 后续 `thinking`、`assistant`、`tool` 都可以自然接在这条真正已发出的 user item 之后。

备选方案：

- 在 queue tray 消失时追加一条 system 文案，代替新的 `User >`。
  不采用，因为这会弱化真实会话记录，用户仍然看不到自己的消息何时正式进入对话。

### 3. 简化 active turn 绑定：user timeline key 只在 turn 激活后才存在

决策：`_PendingTurn` 不再要求在入队时就持有 `user_item_key`；它应在 turn 激活并追加 `User >` 后再绑定对应 key，供 `_finish_active_turn()`、失败收尾和取消收尾复用。

原因：

- 这与新的语义一致：排队中的 turn 还没有 timeline 用户项。
- 可以避免 `_finish_active_turn()` 去更新一个并不存在或尚未正式发出的 user item。
- active turn 的生命周期会更清晰：入队、激活、落盘、收尾四个阶段彼此分明。

备选方案：

- 继续让 `_PendingTurn` 强制持有 `user_item_key`，空缺时用占位符或临时 key。
  不采用，因为这会引入额外哑状态，徒增维护成本。

### 4. 删除 queued user 可见性过滤，改为直接渲染真实会话历史

决策：移除 `_visible_timeline_items()` 中基于 `queue_state == "queued"` 隐藏 user item 的规则；timeline 只渲染已经真实存在于 `_items` 的会话历史。

原因：

- 这个过滤规则本身就是旧模型的补丁层，删除后状态与视图会更直接一致。
- 减少“为什么这个 user item 存在却不可见”的隐式认知负担。
- 也能降低未来再出现滚动、排序、刷新边界问题时的定位难度。

备选方案：

- 保留过滤逻辑，以兼容旧测试和旧 metadata。
  不采用，因为这会让新旧语义并存，后续实现仍容易回归到“先插入再隐藏”的路径。

### 5. 回归测试围绕 handoff 时刻组织，而不是只看最终态

决策：新增测试专门验证“排队中”“前一轮结束后一瞬间”“后一轮完成后”三个时刻的 timeline 与 queue tray 状态，而不是仅断言最终 assistant 回复都存在。

原因：

- 当前 bug 正是发生在 queue tray 到 timeline 的切换瞬间，只看最终态无法发现。
- 这类测试能为失败后续跑、取消后续跑等共享状态流提供更稳的保护。

备选方案：

- 只追加一条最终文本快照断言。
  不采用，因为它无法约束“正式发出时必须新增 `User >`”这一关键行为。

## Risks / Trade-offs

- [Risk] `_PendingTurn` 结构变化会影响现有测试辅助函数和手工构造 active turn 的测试。 → Mitigation：同步调整测试辅助入口，避免继续依赖“入队即有 user_item_key”的旧前提。
- [Risk] 如果 turn 激活后到首次 `thinking`/`assistant` 之间的刷新顺序处理不当，可能短暂出现 timeline 空窗。 → Mitigation：继续沿用 `_start_local_thinking()` 在 turn 激活时立即补 waiting placeholder 的做法。
- [Risk] 删除 queued user 过滤后，若仍有旧路径偷偷往 `_items` 追加 queued user，界面会直接暴露脏状态。 → Mitigation：让 `_enqueue_turn()` 成为唯一入队入口，并在测试中明确断言 queued 阶段 timeline 不含该消息。
- [Trade-off] 队列消息不再保留“最初提交时刻”的 timeline 插入位置信息。 → 这是刻意选择，因为用户更关心“何时正式发出”，而不是“何时排进待处理列表”。

## Migration Plan

1. 调整 `_PendingTurn` 与 `_enqueue_turn()`，让排队阶段不再创建 user timeline 项。
2. 调整 `_start_next_turn_if_idle()`，在 turn 激活时追加新的 `User >` 并绑定到 active turn。
3. 调整 `_finish_active_turn()`、失败/取消收尾路径与 `_refresh_turn_queue_metadata()`，使它们只处理 active turn 的真实 user timeline 项。
4. 删除 queued user 的 timeline 可见性过滤，并保留 queue tray 对 `_pending_turns` 的纯读取渲染。
5. 增加 handoff 场景回归测试，覆盖串行成功、失败续跑、取消续跑。

回滚策略：

- 若新模型引入不可接受的回归，可整体回滚该 change，恢复“入队即创建 user item”的旧路径。
- 本次变更仅涉及本地状态与测试，不涉及数据迁移或外部接口兼容。

## Open Questions

- 当前没有额外开放问题；实现阶段若发现 `/new` 或测试辅助入口仍隐含依赖旧 `user_item_key` 语义，应作为同一 change 内的配套清理一并处理。
