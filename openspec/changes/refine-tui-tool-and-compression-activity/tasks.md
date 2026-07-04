## 1. Runtime Compression Budget

- [x] 1.1 在 `src/agent.py` 的默认 `ModelConfig` 中显式设置 `context_window_limit=900000`
- [x] 1.2 将默认 `EventingSummarizingConversationManager` 的 `preserve_recent_messages` 调整为 6，并补充或更新对应默认装配断言

## 2. Tool Activity Visual Hierarchy

- [x] 2.1 调整 `src/tui/app.py` 中工具主行相关颜色常量，把亮绿色和纯白色替换为各自体系内的次级色
- [x] 2.2 重构工具主行的 Rich 渲染和纯文本格式化逻辑，移除 `{` / `}` 并保持 `Tool`、工具名、状态标签的可区分结构
- [x] 2.3 更新 `test/test_tui_app.py` 中与工具主行文本格式和样式层级相关的断言

## 3. Compression Activity Lifecycle

- [x] 3.1 重构 `src/tui/app.py` 的 compression 事件处理逻辑，使单次 compression 运行只对应一条本地时间线项
- [x] 3.2 在 compression 成功终态时输出单条 `Conversation compressed` 消息，并保持失败与取消终态的真实语义
- [x] 3.3 更新 `test/test_tui_app.py` 中与 compression 双消息、计时收口和终态文案相关的断言

## 4. Verification

- [x] 4.1 运行与 `src/tui/app.py`、`src/agent.py` 相关的目标测试，确认工具主行、compression 生命周期和默认压缩预算行为通过验证
