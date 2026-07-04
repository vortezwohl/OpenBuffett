## Why

当前 TUI 在一批连续 tool call 中会稳定留下第一条 `Running` 工具活动，导致计时持续累加且与后续 `Done` 行并存。这会直接破坏时间线可信度，让用户无法判断真实执行状态，也说明现有 tool 生命周期聚合逻辑不能正确处理同批次多工具活动。

## What Changes

- 修正 tool 生命周期事件的关联逻辑，确保同一条工具调用从 `started` 到终态只收口到一条 timeline 项。
- 补齐“同批次多条 tool call”场景下的状态跟踪规则，避免第一条或同名工具调用被后续 started 事件覆盖。
- 为 TUI 增加保守兜底关联策略，防止上游事件字段异常时残留永不停止的 `Running` 工具项。
- 增加针对重叠 started、同名工具重复调用、取消收口的回归验证。

## Capabilities

### New Capabilities
- `tui-tool-activity-lifecycle`: 规范 TUI 中工具活动行的创建、关联、收口与异常兜底行为，确保工具时间线与真实运行状态一致。

### Modified Capabilities
- 无

## Impact

- 受影响代码：`src/tui/app.py`、EasyHarness runtime 适配层、相关测试。
- 受影响系统：本地 TUI 时间线渲染、工具事件聚合、取消与失败收口路径。
- 风险点：若事件关联修复不完整，可能引入工具终态错绑、重复收口或取消场景回归。
