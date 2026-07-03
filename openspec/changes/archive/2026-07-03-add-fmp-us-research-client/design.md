## Context

`SmartIPO` 当前已经有外部能力封装的基本落点，例如 [src/ext/seedream.py](/D:/github-project/SmartIPO/src/ext/seedream.py) 负责统一处理环境变量、请求会话和返回结果，但 [src/ext/fmp.py](/D:/github-project/SmartIPO/src/ext/fmp.py) 仍为空文件。与此同时，用户已经明确了两个真实使用场景：

1. 判断是否参与某家美股 IPO；
2. 围绕某家公司做估值研究。

这两个场景都不是“要一个通用财经 SDK”，而是要一个项目内最小可靠、可组合、边界清楚的数据接入层。FMP 本身已经覆盖了一期所需的大部分美股 IPO、财报、估值指标、卖方预期和辅助研究数据，因此本次设计重点不是再造框架，而是把这些接口按研究任务切成可直接调用的方法。

约束也很明确：
- 只做美股一期，不把 A 股/港股发行规则和本地交易所文书混进来；
- API Key 必须从环境变量加载，但允许显式参数覆盖；
- 继续沿用项目当前的 `requests + load_dotenv()` 风格，不引入新的 SDK；
- 不在本次变更中顺手实现评分器、分析器、缓存、数据库或异步任务层。

## Goals / Non-Goals

**Goals:**
- 在 [src/ext/fmp.py](/D:/github-project/SmartIPO/src/ext/fmp.py) 提供一个最小 `FmpClient`，统一管理 base URL、API Key、HTTP GET 和错误处理。
- 按“IPO 决策”和“估值研究”两个场景接入 FMP 一期核心接口。
- 让每个接口保持薄封装，尽量把 FMP 的 query 参数和返回结构原样暴露给调用方。
- 为缺少 API Key、参数透传和 HTTP 失败边界补上最小可回归测试。

**Non-Goals:**
- 不实现 IPO 参与结论、打分、排序或投研报告输出。
- 不实现 A 股、港股或非 FMP 数据源接入。
- 不新增缓存、重试策略、限流器、数据库落盘或 schema 映射层。
- 不把 FMP 数据二次加工成复杂领域对象；一期只提供可靠拉数能力。

## Decisions

### 1. 用单文件 `FmpClient` 做薄客户端，不先拆子模块

决策：在 [src/ext/fmp.py](/D:/github-project/SmartIPO/src/ext/fmp.py) 内实现一个单文件 `FmpClient`，并提供少量模块级便捷函数；不新建 `ipo.py`、`valuation.py`、`macro.py` 等多文件层级。

理由：当前仓库外部客户端规模还很小，[src/ext/seedream.py](/D:/github-project/SmartIPO/src/ext/seedream.py) 已经证明“单文件 + 清楚方法名”足够好维护。FMP 接口虽然多，但本质上只是同一 host 上的一组 GET endpoint，拆过早只会增加跳转成本。

备选方案：按研究主题拆多个模块。拒绝，因为一期仍处于“把空文件变成可用客户端”的阶段，拆模块没有带来实际收益。

### 2. 用统一 `_get()` 处理鉴权、query 拼接和错误透传

决策：客户端内部只保留一个公共 HTTP helper，例如 `_get(path, **params)`，负责：
- 拼接 `base_url + path`；
- 自动补上 `apikey`；
- 过滤值为空的 query 参数；
- 调用 `requests.Session.get(...)`；
- `raise_for_status()` 后直接返回 `response.json()`。

理由：FMP 一期主要是 GET 接口，真正需要统一的只有鉴权、参数清洗和错误边界。把所有 endpoint 都收口到一个 helper，能保证行为一致，也能把测试集中在一处。

备选方案：为每类 endpoint 建独立 request builder。拒绝，因为那是在为抽象而抽象。

### 3. 一期返回 FMP 原始 JSON，不做复杂结果映射

决策：除非某个接口明显需要统一结果容器，否则方法直接返回 `dict[str, Any]` 或 `list[dict[str, Any]]` 这类原始 JSON 结果，不创建大批 dataclass。

理由：FMP 接口形状很多，强行为每个 endpoint 建模会带来大量样板和同步维护成本，而当前真实需求只是“把研究数据稳定拿出来”。最小成本的正确解是薄封装，而不是在客户端层先做领域建模。

备选方案：仿照 `SeedreamImageResult` 为所有 endpoint 建返回对象。拒绝，因为收益很低，维护成本很高。

### 4. 用研究任务分组命名方法，而不是照着文档任意散列

决策：方法按用户任务理解来组织，分成以下几组，但仍都留在同一个类里：

- IPO 决策核心  
  `get_ipos_calendar`、`get_ipo_disclosures`、`get_ipo_prospectus`、`get_sec_filings_by_symbol`、`get_latest_sec_filings`、`get_profile`、`get_quote`、`get_shares_float`、`get_historical_price_eod_light`
- 估值研究底表  
  `get_income_statement`、`get_balance_sheet_statement`、`get_cashflow_statement`、`get_as_reported_financial_statements`、`get_financial_statement_growth`、`get_latest_financial_statements`
- 估值指标与模型  
  `get_key_metrics`、`get_key_metrics_ttm`、`get_financial_ratios`、`get_financial_ratios_ttm`、`get_enterprise_values`、`get_owner_earnings`、`get_dcf_advanced`、`get_levered_dcf`、`get_custom_dcf_advanced`
- 可比公司与研究辅助  
  `get_financial_estimates`、`get_price_target_consensus`、`get_stock_peers`、`get_company_executives`、`get_executive_compensation`、`get_earnings_transcripts`、`get_positions_summary`、`get_latest_insider_trades`、`search_insider_trades`、`get_insider_trade_statistics`
- 贴现参数与宏观辅助  
  `get_treasury_rates`、`get_market_risk_premium`、`get_economic_indicators`

理由：命名直接对应研究动作，后续写分析流程时最容易读懂，也避免只按 FMP 文档标题机械映射。

备选方案：统一叫 `fetch_<endpoint_slug>`。拒绝，因为调用点会失去研究语义。

### 5. API Key 和 base URL 采用显式参数优先、环境变量兜底

决策：客户端初始化支持：
- `api_key`
- `api_base`
- `timeout`

环境变量约定：
- `FMP_API_KEY`
- `FMP_API_BASE`

默认 base 设为 `https://financialmodelingprep.com/stable`。

理由：这和项目现有的 [src/ext/seedream.py](/D:/github-project/SmartIPO/src/ext/seedream.py) 以及 [src/service/model_hub.py](/D:/github-project/SmartIPO/src/service/model_hub.py) 风格一致，简单直接，也便于测试时显式覆盖。

备选方案：再建一层专门的配置对象或 settings 类。拒绝，因为现在没有必要。

### 6. 为测试预留最小注入点，但不引入测试专用框架

决策：客户端内部仍默认自建 `requests.Session()`，但允许初始化时注入一个 session 对象，便于单测直接替换。测试继续使用仓库现有 `unittest + patch` 风格。

理由：如果完全不留注入点，测试就只能 patch 很深的 `requests.Session.get`；而如果为此引入新 mock 工具或 HTTP 框架，又太重。可选 session 参数是最小且够用的折中。

备选方案：只 patch 全局 `requests.get`。拒绝，因为实际实现会持有 session，patch 粒度不稳。

### 7. 一期只覆盖文章里 FMP 真能提供的数据，不伪装成全栈投研源

决策：设计层明确排除以下数据类型：
- A 股/港股 IPO 发行制度细节；
- 融资融券、隐含波动率、做空比例、超额认购倍数等 FMP 当前非强覆盖项；
- 海关、门店、App、招聘、专利、供应链交叉验证等另类数据。

理由：用户要的是“完整落地方案”，不是“把做不到的东西也写进承诺”。边界写清楚，后续实现和验收才不会失真。

备选方案：把所有研究数据口径都先挂进设计文档。拒绝，因为那会把不可交付范围伪装成需求。

## Risks / Trade-offs

- [FMP 接口较多，首版方法列表容易过长] → 通过单一 `_get()` 和按研究主题分组命名控制复杂度，不额外拆模块。
- [直接返回原始 JSON，调用方需要理解 FMP 结构] → 这是有意为之；先把拉数边界做稳，后续真实出现重复解析时再补高层 helper。
- [某些文档页可见但 FMP 实际套餐权限不同] → 客户端只负责请求和错误透传，不在 SDK 层隐藏权限失败；测试重点锁定本地行为，不伪造线上可用性。
- [美股一期方法仍然不少] → 通过任务拆分分批实现，先完成 IPO 核心和估值核心，再补研究辅助接口。
- [不做缓存可能导致重复调用] → 当前阶段先接受这一点；只有当调用链和成本真实出现问题时，再考虑在客户端外围加缓存。

## Migration Plan

1. 在 [src/ext/fmp.py](/D:/github-project/SmartIPO/src/ext/fmp.py) 内实现 `FmpClient`、环境变量解析函数、统一 `_get()` 和第一批方法。
2. 先补 IPO 核心与估值核心方法，再补辅助研究方法，避免一次性大 diff 难以验证。
3. 在 `test/` 新增或扩展 FMP 客户端测试，覆盖缺失 key、query 拼接、代表性 endpoint path 和 HTTP 错误透传。
4. 若实现过程中发现某些 endpoint 名称或 query 口径与文档不一致，以 FMP 实际返回为准做最小修正，但不扩大范围。
5. 若需要回滚，只需回退 [src/ext/fmp.py](/D:/github-project/SmartIPO/src/ext/fmp.py) 及对应测试，不涉及数据迁移。

## Open Questions

- 是否需要在一期顺手提供按 CIK/CIK symbol 的补充检索方法。当前建议只加用户明确需要的版本，避免过量包装。
- 是否需要把 `quote`、`profile` 这类通用接口额外暴露为模块级函数。当前建议只保留类方法和极少量常用便捷函数。
- 某些 FMP endpoint 的 query 细节是否需要限制白名单。当前建议除明显必要字段外尽量透传，避免客户端层过度约束。
