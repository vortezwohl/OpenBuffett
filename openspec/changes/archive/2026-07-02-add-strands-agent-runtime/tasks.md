## 1. 主脑与运行时骨架

- [x] 1.1 新增 `src/base/agent.py`，提供 strands `LiteLLMModel` 的最小装配入口，并与 `Text2Text` 保持职责分离
- [x] 1.2 新增 `src/core/strands_runtime.py`，实现单轮 strands `Agent` 调用和统一 `StrandsRunResult` 返回结构
- [x] 1.3 新增 `src/core/agent_loop.py`，提供只负责单轮执行的最小 `run_once(...)` 入口

## 2. 工具契约与真实工具接线

- [x] 2.1 新增 `src/tool/contracts.py`，定义最小 `ToolContext`、`ToolResult` 和 `ToolSpec`
- [x] 2.2 新增 `src/tool/registry.py`，实现最小内存注册表和默认工具装配函数
- [x] 2.3 新增 `Seedream` tool wrapper，并把现有 `generate_seedream_image` 接入默认工具注册表
- [x] 2.4 在 strands runtime 中实现 `ToolSpec -> strands tool` 的薄包装逻辑，确保调用方可按工具名选择暴露子集

## 3. 最小验证

- [x] 3.1 新增最小构造测试，验证 strands `LiteLLMModel` 与 `Agent` 可按当前配置成功装配
- [x] 3.2 新增 fake runtime 测试，验证已暴露工具可被调用且返回统一结果
- [x] 3.3 新增 fake runtime 失败测试，验证工具异常继续向上暴露且不会伪装成成功
- [x] 3.4 新增工具暴露边界测试，验证未显式暴露的工具不会进入当前主脑回合
