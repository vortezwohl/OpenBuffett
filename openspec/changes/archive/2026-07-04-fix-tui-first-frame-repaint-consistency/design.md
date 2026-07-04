## Context

当前 `AgentWorkbenchApp` 已经针对 resize 问题加入了表面背景和 `on_resize()` 内的 `refresh(layout=True, repaint=True)`，但用户截图表明实际结果仍然不一致：首次打开时出现横向暗条和未完整刷新的面板内部，而拉宽再拉回后，界面又变成另一种更干净的形态。

结合当前实现可以看到两条不同的生命周期：
- `on_mount()` 在应用刚挂载时直接执行 `_refresh_view(force_follow=True)`；
- `on_resize()` 在终端尺寸变化后先 `refresh(layout=True, repaint=True)`，再 `call_after_refresh(self._refresh_view)`。

这意味着首帧内容写入发生在最终布局和完整 repaint 之前，而 resize 后内容写入发生在一次更完整的表面重绘之后。问题的根源不是“缩放时会坏”，而是 mount 与 resize 本来就没有共享同一套渲染契约。

## Goals / Non-Goals

**Goals:**
- 让 TUI 首次打开时的界面表面与 resize 往返后的稳定结果保持一致。
- 让 `on_mount()` 与 `on_resize()` 走同一套完整的重排/重绘调度路径，而不是各自直接操作局部刷新。
- 避免在首轮布局尚未稳定时就提前对 `status-banner`、timeline、queue tray 执行 `Static.update(...)`。
- 把测试从“宽度值变化”提升到“首帧与 resize 往返结果一致”的回归验证。

**Non-Goals:**
- 不重新设计 TUI 主题、聊天文案或消息语义。
- 不处理 `/stop` 相关旧测试失败或其他无关交互问题。
- 不引入新的截图基线工具链或外部视觉回归服务。
- 不再次扩大到多主题或更复杂的响应式布局系统。

## Decisions

### 1. 用统一的全量 repaint 调度替代 mount / resize 各自拼逻辑

决策：新增一条统一的 repaint 调度路径，例如 `_schedule_full_repaint(...)` / `_run_full_repaint(...)`，由 `on_mount()` 和 `on_resize()` 共同调用。它负责：
- 先等待当前 refresh/layout 周期稳定；
- 再执行完整的 `layout + repaint`；
- 最后统一调用 `_refresh_view(...)` 写入局部内容。

原因：
- 当前 `on_mount()` 直接 `_refresh_view()`，而 `on_resize()` 先全量 repaint 再 `_refresh_view()`，天然会产生两种视觉结果；
- 统一入口后，首帧和 resize 后都必须经历同一组时序。

备选方案：
- 只给 `on_mount()` 前面补一个 `refresh(layout=True, repaint=True)`。
  不采用，因为这仍然保留了两条入口，后续很容易再次漂移。

### 2. 首帧内容写入必须延后到首轮布局稳定之后

决策：`on_mount()` 不再立即执行 `_refresh_view(force_follow=True)`，而是只做必要的初始调度，例如 theme、timer、focus 和一次延后的全量 repaint 调度。

原因：
- 当前截图中的横向暗条更像是“先写内容、后定布局”导致的首帧脏表面；
- `Static.update(...)` 写得过早，会把局部内容叠加到尚未稳定的容器表面上。

备选方案：
- 保持 `on_mount()` 立即 `_refresh_view()`，再额外多刷一遍。
  不采用，因为这会继续允许脏首帧短暂出现，只是随后被覆盖。

### 3. resize 只触发统一调度，不再自己拼 repaint 和 view refresh

决策：`on_resize()` 只负责请求统一 repaint，而不直接自己写 `refresh(layout=True, repaint=True)` 再单独 `_refresh_view()`。

原因：
- 如果 resize 继续保留专属逻辑，mount 和 resize 之间又会重新形成分叉；
- 统一后也更容易做防抖、去重和后续维护。

备选方案：
- 保持现有 `on_resize()` 不动，只改 mount。
  不采用，因为这样“首帧路径”和“resize 路径”仍不是同一实现。

### 4. 回归测试必须比较“初始稳定结果”和“resize 往返后稳定结果”的等价性

决策：新增一类一致性测试，流程是：
- 应用启动；
- 等待首帧稳定；
- 采集关键区域的可视输出快照；
- 执行拉宽和拉回；
- 再采集一次稳定快照；
- 断言两次结果等价。

优先比较真实渲染输出，而不是只比较 `_render_timeline_text()` 或宽度数值。实现阶段可以根据 Textual 提供的现成能力选择：
- 屏幕导出截图 / SVG；
- 或关键区域的渲染条带（strip）/表面输出快照。

原因：
- 用户报告的问题是视觉表面不一致，而不是消息文本丢失；
- 只测文本或 widget 宽度会继续漏掉这种“看起来坏了”的回归。

备选方案：
- 继续只保留 `Pilot.resize_terminal(...)` 后的宽度断言。
  不采用，因为这正是当前漏检的原因。

## Risks / Trade-offs

- [Risk] 统一 repaint 调度后，首屏出现时间可能比现在略晚一拍。 → Mitigation：接受一次小的首帧延后，换取稳定而一致的最终结果。
- [Risk] 真实渲染快照断言可能比纯文本断言更脆弱。 → Mitigation：比较关键区域的稳定输出，并尽量规避与时间、随机值相关的噪音。
- [Risk] 如果调度去重做得不好，频繁 resize 时可能重复触发多次完整 repaint。 → Mitigation：实现阶段为统一调度增加幂等或防抖约束。
- [Trade-off] 这次优先修生命周期一致性，不继续扩展到更复杂的视觉优化。 → 这是刻意收敛，先解决“初始打开和 resize 后不是同一界面”的根问题。

## Migration Plan

1. 先把 mount / resize 的局部刷新逻辑收敛到统一 repaint helper。
2. 再调整 `on_mount()` 的时序，让首次内容写入延后到布局稳定之后。
3. 最后补一致性回归测试，比较首帧稳定结果和 resize 往返后的稳定结果。

回滚策略：
- 如果统一调度引入新问题，可先回滚到当前 mount / resize 分离逻辑；
- 如果视觉一致性测试过于脆弱，可先回滚具体断言方式，而保留统一 repaint 路径。

## Open Questions

- 实现阶段需要在“导出整屏截图/SVG比较”和“比较关键 widget 的渲染条带”之间选一个更稳的测试手段。
