## Context

SmartIPO 当前已经完成一轮 EasyHarness 主干迁移：默认 runtime 使用 `easyharness.Agent`，工具声明使用 `easyharness.tool`，TUI 直接消费 `easyharness.AgentEvent`。这解决了“项目自研 agent/tool/timeline 双栈”的最大问题，但实现表面积还没有同步收缩。

当前仓库中仍存在几类迁移残留：

- `src/core/llm.py` 与 `src/core/text2text.py`：生产主链没有调用，只在测试和 README 中被保留为“独立 NLP 接口”。
- `src/service/model_hub.py` 与 `src/model_config.py`：为了一个默认模型维护 `ModelHub` 类、channel dataclass、call-name dataclass 和配置字典。
- `src/app/default_agent.py`：实际职责是 agent composition，但 `app` 包名容易和 Textual `App`、业务应用层混淆。
- `src/util/*`：当前未被生产代码或测试调用，且多数 helper 属于旧项目泛用工具，而不是 SmartIPO 当前真实业务边界。

这次设计的核心判断是：既然底层已经交给 EasyHarness，SmartIPO 自己不应再维护任何“看起来像框架”的薄层。项目代码只保留三类东西：

```text
┌────────────────────────────────────────────┐
│ SmartIPO 项目边界                          │
├────────────────────────────────────────────┤
│ 1. agent composition: 选择模型、prompt、工具 │
│ 2. business tools/ext: Seedream、FMP 等业务边界 │
│ 3. UI: TUI 对 AgentEvent 的本地展示          │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ EasyHarness 边界                            │
├────────────────────────────────────────────┤
│ Agent / ModelConfig / AgentEvent / tool     │
│ 文件工具、会话控制、纯文本调用、工具协议       │
└────────────────────────────────────────────┘
```

## Goals / Non-Goals

**Goals:**

- 删除项目私有 `LLM` / `Text2Text`，纯文本生成统一走 EasyHarness 原生 `Agent`。
- 删除 `ModelHub` 和多调用点配置表，把默认模型装配压缩成一个直接函数。
- 将 `src/app/default_agent.py` 压平为语义明确的 `src/agent.py`。
- 删除未使用的 `src/util` 包，避免旧 helper 继续制造“公共工具层”错觉。
- 保留 EasyHarness 之外真正必要的项目代码：TUI、业务工具、外部服务客户端。
- 更新测试和 README，让文档与测试强制约束“最小表面积”。

**Non-Goals:**

- 不修改 EasyHarness SDK，不复制或封装其内部 runtime。
- 不新增依赖，不引入配置框架、插件框架或多 agent 编排层。
- 不重构 FMP/Seedream 业务客户端内部实现，除非导入路径因目录瘦身必须调整。
- 不把 TUI 本地 `_TimelineItem` 抽成共享协议；展示态仍留在 UI 内部。
- 不保留旧导入路径兼容 shim；这是内部破坏性收敛。

## Decisions

### 1. 删除项目私有 text2text，而不是继续“降级保留”

决策：删除 `src/core/llm.py`、`src/core/text2text.py` 和 `src/core/__init__.py` 的公开导出；移除 `test_text2text_boundary.py`。

理由：

- EasyHarness 已经能通过 `Agent(model=..., tools=[], enable_fileglide=False)` 提供纯文本会话能力。
- 当前 `Text2Text` 只在测试中被证明“可以构造”，没有生产调用点。
- 继续保留会制造第二套模型调用入口，后续开发者会自然纠结“该用 Text2Text 还是 Agent”。

替代方案：

- 保留 `Text2Text` 作为基础服务。
  放弃。这个选择在迁移早期保守，但现在它只是重复 EasyHarness 的底层职责。

### 2. 用一个函数替代 ModelHub 类和配置表

决策：删除 `ModelHub` 类、`create_default_model_hub()`、`AGENT_SESSION_ROUND`、`CHANNEL_CONFIGS`、`BRAIN_MODEL_CONFIGS`、`ChannelConfig` 和 `BrainModelConfig`。保留或内联一组默认常量，并提供一个直接函数，例如：

```python
def build_default_model_config() -> ModelConfig:
    ...
```

该函数只做四件事：

1. 读取 `API_KEY`，缺失时 fail fast；
2. 读取 `API_BASE`，缺失时使用默认 DeepSeek base；
3. 组装 `openai/deepseek-v4-pro`；
4. 设置固定采样参数。

理由：

- 当前只有一个默认模型、一个调用点、一个 channel。
- dataclass + dict + hub 类没有抽象收益，只增加改动点和测试负担。
- 如果未来真实出现多个模型用途，再用真实调用方拉出最小数据结构即可。

替代方案：

- 保留 `model_config.py` 只存常量。
  可接受，但更小的实现是把常量放在 `src/agent.py` 内，直到第二个模块真实复用它。

### 3. 将 composition 入口压平到 `src/agent.py`

决策：把 `src/app/default_agent.py` 中的默认 prompt、默认工具名、`build_default_tools()`、`build_default_agent()`、模型配置函数迁移到 `src/agent.py`。

理由：

- 当前 `app` 包只有默认 agent 装配，不代表业务应用层。
- `src/tui/app.py` 已经使用 Textual `App` 概念，`src/app` 与 `tui/app.py` 同时存在会增加命名歧义。
- `src/agent.py` 是对调用方最直接的入口：它就是构建 SmartIPO agent 的地方。

替代方案：

- 改名为 `src/composition/default_agent.py`。
  放弃。composition 包会为一个文件再建一层目录，仍然偏框架化。

### 4. 保留 `tool` 与 `ext`，因为它们是业务边界

决策：保留 `src/tool/seedream_image.py`、`src/ext/seedream.py`、`src/ext/fmp.py`。

理由：

- `tool` 是 EasyHarness 工具合同下的业务工具声明层，是真实 extension point。
- `ext` 是外部服务客户端边界，负责 HTTP、鉴权、参数清洗和错误透传，这些不是 EasyHarness 的职责。
- 删除或合并它们会把业务 I/O 细节塞进 agent composition，反而降低清晰度。

替代方案：

- 把 Seedream tool 和 Seedream client 合并。
  暂不采用。一个是 EasyHarness 工具声明，一个是外部 API client，职责不同且已有测试覆盖工具返回。

### 5. 删除未使用 util，而不是整理 util

决策：删除整个 `src/util` 包。

理由：

- 搜索结果显示 util 函数没有被生产代码或测试调用。
- helper 只有在多个真实调用点复用时才值得提升为公共层。
- 当前 util 内容包含旧项目文本处理、随机采样、序列化、校验等泛用函数，会误导后续开发者继续往里堆“方便函数”。

替代方案：

- 保留 `serialization.local_file_to_base64()`，可能将来图片工具会用。
  放弃。当前没有调用点；将来图生图需要本地文件输入时，优先在 Seedream tool 附近实现最小逻辑。

### 6. 测试门禁转向“禁止回胖”

决策：删除旧 text2text/model_hub 测试，新增或调整测试来覆盖：

- 默认 agent 仍返回 `easyharness.Agent`；
- 默认工具集合仍包含官方 fileglide 和 Seedream 业务工具；
- 纯文本 agent 可通过 EasyHarness Agent 无工具模式构造；
- 代码库不再暴露 `Text2Text`、`ModelHub`、`src.app.default_agent`、`src.util`；
- TUI 仍只消费 `AgentEvent` 并从 `src.agent` 获取默认 agent。

理由：

- 测试不应保护已决定删除的旧抽象。
- 本轮最重要的长期价值是防止底层包装层回流。

## Risks / Trade-offs

- [Risk] 删除 `Text2Text` 后，未来某个业务流程需要单次纯文本调用。→ Mitigation：用 EasyHarness Agent 无工具模式；如果未来需要更低层 SDK 能力，先证明 EasyHarness 不能满足，再引入最小专用函数。
- [Risk] 删除 `ModelHub` 会降低多模型扩展能力。→ Mitigation：当前没有多模型需求；未来出现第二个真实模型调用点时再引入字典或小 dataclass。
- [Risk] 破坏旧导入路径会让未搜索到的外部脚本失败。→ Mitigation：这是内部项目破坏性重构；README 明确新入口，测试覆盖仓库内导入。
- [Risk] `src/agent.py` 聚合 prompt、模型和工具后文件变大。→ Mitigation：这是有意选择；一个 composition 文件比多个薄层更容易审查。超过真实维护阈值再拆。
- [Risk] 删除 util 可能丢掉未来可复用函数。→ Mitigation：未使用代码不是资产；Git 历史可恢复。

## Migration Plan

1. 新建 `src/agent.py`，搬迁并最小化默认 agent composition。
2. 将 TUI 和测试导入从 `src.app.default_agent` 改为 `src.agent`。
3. 删除 `src/app`、`src/service`、`src/model_config.py`、`src/core`、`src/util` 中不再需要的文件。
4. 重写测试：保留 tooling、TUI、FMP、Seedream 相关门禁，删除保护旧抽象的测试。
5. 更新 README，说明 SmartIPO 的底层能力由 EasyHarness 提供，项目只保留 agent composition、业务工具、外部服务客户端和 UI。
6. 运行 `python -m unittest discover -s test -v`。
7. 用 `rg` 复查旧名词和旧导入路径：`Text2Text|ModelHub|model_config|src\\.app|src\\.util|src\\.service|src\\.core`。

回滚策略：

- 本变更不提供运行时兼容回滚。
- 若实施切片失败，回退该切片文件改动；不要在主干内新增 compat shim。

## Open Questions

- `src/ext/fmp.py` 是否最终应该被包装成 EasyHarness 工具，取决于下一轮 IPO research workflow 是否需要 agent 直接调用 FMP；本轮不提前做。
- `src/agent.py` 是否需要导出 `build_text_agent()` 作为纯文本便捷函数。默认建议暂不导出，测试只验证 EasyHarness 无工具模式可行；等真实调用点出现再加。
