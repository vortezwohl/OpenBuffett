## 1. 运行时边界适配

- [x] 1.1 在 `src/core/strands_runtime.py` 增加 provider-facing 工具名规范化逻辑，确保导出的工具名符合当前 provider 的 `function.name` 约束
- [x] 1.2 保持内部 `ToolSpec.name`、事件负载和执行记录不变，并通过映射让外部工具名继续调用原始 handler
- [x] 1.3 为合法化后的工具名增加冲突保护或明确失败路径，避免不同内部工具名映射到同一个外部名字

## 2. 验证

- [x] 2.1 增加聚焦测试，覆盖点号工具名的 provider 导出合法性和调用映射
- [x] 2.2 运行现有测试，确认 fileglide 工具与 TUI workbench 行为不回归
