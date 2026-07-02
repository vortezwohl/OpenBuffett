## Why

`SmartIPO` 已经具备 `Text2Text` 和 `Seedream` 这类单点能力，但还没有一个统一、可扩展、又不过度设计的 agent 运行时骨架。既然仓库已经引入了 `strands-agents` 依赖，现在继续靠零散函数直接拼接能力会让后续接入行情、研报、图像和文件工具时越来越乱。

现在推进这项变更是合适的，因为项目还处在早期，运行时边界还没有固化。此时补上一套最小可靠可用的 strands agent loop / tool call loop，可以在复杂度还低的时候把主脑、工具和业务能力的职责切清楚。

## What Changes

- 新增一个最小 strands 主脑运行时，负责执行单轮 agent 调用并返回统一结果。
- 新增项目内的最小工具契约与工具注册表，用统一方式暴露业务能力给 strands。
- 把现有 `Seedream` 生图能力包装成第一批真实可调用工具，作为运行时闭环的起点。
- 保持 `Text2Text` 继续承担纯文本生成职责，不把 tool-call 语义塞回文本模型封装。
- 为 strands runtime 增加可注入 fake runtime 的最小测试入口，锁定成功、失败和工具暴露边界。

## Capabilities

### New Capabilities
- `strands-agent-runtime`: 定义 SmartIPO 的最小 strands agent loop、tool call loop、工具暴露边界和可测试运行时入口。

### Modified Capabilities
- None.

## Impact

- 受影响代码主要位于 `src/base/`、`src/core/`、`src/tool/` 与 `test/`。
- 运行时将开始真实使用已存在的 `strands-agents[litellm]` 依赖，但不新增新的 orchestration 框架。
- 对外 API 仍以当前 Python 调用为主，本次不引入 TUI、数据库或远程服务层。
