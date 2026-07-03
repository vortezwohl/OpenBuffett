## 1. Agent 装配压平

- [x] 1.1 新建 `src/agent.py`，集中放置默认 system prompt、默认工具名、默认工具构造和默认 agent 构造入口。
- [x] 1.2 在 `src/agent.py` 中实现最小 `build_default_model_config()`，直接读取 `API_KEY`、`API_BASE` 并返回 `easyharness.ModelConfig`。
- [x] 1.3 保持 `build_default_tools(workspace_root)` 只组合 EasyHarness 官方 fileglide toolset 与 Seedream 业务工具对象。
- [x] 1.4 保持 `build_default_agent(workspace_root)` 直接返回 `easyharness.Agent`，不接受采样参数覆写，不经过 ModelHub 或 text2text。

## 2. 删除旧抽象与误导性包

- [x] 2.1 删除 `src/core/llm.py`、`src/core/text2text.py` 和 `src/core/__init__.py`，移除项目私有 LLM/text2text 导出。
- [x] 2.2 删除 `src/service/model_hub.py` 和 `src/service/__init__.py`，移除 `ModelHub` 与 `create_default_model_hub()`。
- [x] 2.3 删除 `src/model_config.py`，移除 channel 配置表、brain model 配置表和对应 dataclass。
- [x] 2.4 删除 `src/app/default_agent.py` 和 `src/app/__init__.py`，用 `src.agent` 作为唯一默认 agent 装配入口。
- [x] 2.5 删除整个 `src/util` 包，不迁移未使用 helper，不新增替代公共 helper 层。

## 3. 导入路径与文档收敛

- [x] 3.1 将 TUI 默认 agent 导入路径从 `src.app.default_agent` 改为 `src.agent`。
- [x] 3.2 将工具测试和 TUI 测试中的默认 agent 导入路径改为 `src.agent`。
- [x] 3.3 更新 README，删除 `Text2Text` 独立基础 NLP 接口表述，说明纯文本调用复用 EasyHarness 无工具 Agent。
- [x] 3.4 复查包导出，确保 README 和源码不再推荐 `src.core`、`src.service`、`src.app.default_agent`、`src.util`。

## 4. 测试门禁重建

- [x] 4.1 删除 `test_text2text_boundary.py`，不再测试已删除的私有 text2text 抽象。
- [x] 4.2 重写 `test_model_hub.py` 为默认模型配置测试，验证 `build_default_model_config()` 返回 `ModelConfig`、读取环境变量并在缺少 `API_KEY` 时失败。
- [x] 4.3 调整 `test_tooling.py`，验证默认工具集合和默认 agent 都来自 `src.agent`，并继续覆盖 Seedream 工具输出。
- [x] 4.4 新增或调整瘦身回归测试，确认旧导入路径和旧包名不再存在于仓库主链中。
- [x] 4.5 保持 `test_tui_app.py` 覆盖 `AgentEvent` 展示流，不引入共享 timeline/view-model 协议。

## 5. 验证与收尾

- [x] 5.1 运行 `python -m unittest discover -s test -v`，确保全部测试通过。
- [x] 5.2 用 `rg "Text2Text|ModelHub|model_config|src\\.app|src\\.util|src\\.service|src\\.core" src test README.md` 复查旧抽象残留。
- [x] 5.3 用文件树复查 `src` 顶层只保留 agent composition、TUI、业务工具和外部客户端边界。
- [x] 5.4 记录未纳入本轮的后续问题：FMP 是否需要包装成 EasyHarness 工具、是否出现真实 `build_text_agent()` 调用点。
