## 1. 收紧 core 时间线契约

- [x] 1.1 调整 `src/core/strands_runtime.py` 的工具事件载荷，删除 `display_name`、`message` 等展示层字段，只保留语义字段
- [x] 1.2 调整 `src/core/timeline.py`，移除工具标题格式化和类别中文映射，只保留状态归约与原始 metadata
- [x] 1.3 更新 `test/test_strands_runtime.py` 和 `test/test_timeline.py`，验证 core 不再输出 UI 专用字段

## 2. 修正 TUI 工具活动展示

- [x] 2.1 调整 `src/tui/app.py`，改由 TUI 自己基于原始 `tool_name` / `tool_kind` 渲染工具条目文本
- [x] 2.2 在 `src/tui/app.py` 中实现工具运行态最小可见时长，保证快速工具也会先显示一次运行中状态
- [x] 2.3 保持工具完成态的概要、详细结果折叠和 thinking 动画行为，但不再依赖 core 提供展示文案

## 3. 验证运行中可见性

- [x] 3.1 更新 `test/test_tui_app.py`，增加“工具执行中已显示 timeline 和计时”的断言
- [x] 3.2 增加“快速工具至少出现一次运行态再切完成态”的测试
- [x] 3.3 运行最小验证命令，确认单元测试和 `compileall` 通过
