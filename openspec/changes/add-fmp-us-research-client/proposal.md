## Why

`SmartIPO` 现在已经有外部能力封装入口，但 [src/ext/fmp.py](/D:/github-project/SmartIPO/src/ext/fmp.py) 仍是空文件，导致“是否参与某家美股 IPO”和“公司估值研究”这两类核心工作没有统一、可复用的数据接入层。现在补上这层是合适的，因为 FMP 已经能覆盖一期所需的大部分美股 IPO 文书、结构化财务、估值指标和辅助研究数据，再继续靠零散脚本或临时请求会迅速让后续分析能力失去边界。

## What Changes

- 新增一个最小可用的 FMP 客户端，统一封装美股 IPO 决策与估值研究所需的 HTTP 调用、鉴权、参数拼接和错误处理。
- 先接入与“是否参与某家公司 IPO”直接相关的 FMP 接口，包括 IPO 日历、IPO 披露、IPO 招股书、SEC filings、公司概况、报价与流通股本等。
- 先接入与“公司估值研究”直接相关的 FMP 接口，包括三表、as reported 财报、增长、关键指标、财务比率、企业价值、DCF、owner earnings、分析师预期和可比公司等。
- 补充管理层、内部人、机构持仓、业绩会纪要、国债利率和市场风险溢价等辅助研究接口，但不在本次变更中实现更高层的评分器、结论生成器或 UI 集成。
- 约定 API Key 从环境变量加载，并为客户端补上最小可回归测试，锁定鉴权缺失、请求参数和错误透传边界。

## Capabilities

### New Capabilities
- `fmp-us-research-client`: 定义 SmartIPO 的 FMP 客户端边界，使调用方能够稳定获取美股 IPO 决策与估值研究所需的核心数据。

### Modified Capabilities
- None.

## Impact

- 受影响代码主要位于 `src/ext/` 与 `test/`，其中 [src/ext/fmp.py](/D:/github-project/SmartIPO/src/ext/fmp.py) 将从空文件变为真实客户端实现。
- 运行时将继续复用项目已安装的 `requests` 与 `python-dotenv` 使用模式，不新增新的 HTTP SDK 或配置框架。
- 对外新增的主要是 Python 调用接口，不在本次变更中引入数据库、缓存、任务编排或分析结论层。
