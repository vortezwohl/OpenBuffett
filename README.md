# SmartIPO

SmartIPO 已收敛到 EasyHarness 主干架构：

- 默认 agent runtime 使用 `easyharness.Agent`。
- 默认文件系统工具使用 EasyHarness 官方 fileglide toolset。
- 自定义业务工具使用 `easyharness.tool` 声明。
- TUI 直接消费 `easyharness.AgentEvent` 流，不再维护项目自研 timeline 协议。
- `src.core.text2text.Text2Text` 仅作为独立基础 NLP 接口保留，不承担 agent 会话控制或工具调度职责。

## 本地运行

```powershell
.\.venv\Scripts\python -m src.tui
```

运行前需要配置默认模型渠道所需的环境变量：

- `API_KEY`: 模型 API key。
- `API_BASE`: 可选，未配置时使用 `src/model_config.py` 中的默认 base URL。
