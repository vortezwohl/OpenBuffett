## ADDED Requirements

### Requirement: 系统必须提供统一的 FMP 美股研究客户端入口
系统 MUST 在 [src/ext/fmp.py](/D:/github-project/SmartIPO/src/ext/fmp.py) 提供统一的 FMP 客户端入口，使调用方能够通过同一对象访问美股 IPO 决策与估值研究所需的数据接口，而不是自行拼接 URL 和鉴权参数。

#### Scenario: 调用方通过同一客户端访问多个研究接口
- **WHEN** 调用方创建一个 FMP 客户端并在同一进程内连续请求 IPO、财报和估值类数据
- **THEN** 系统 MUST 通过同一个客户端实例提供这些方法入口
- **AND** 调用方 MUST NOT 需要为每个 endpoint 手工重复处理鉴权或基础 URL

### Requirement: 系统必须从环境变量解析 FMP 鉴权配置
系统 MUST 支持从环境变量加载 FMP API Key，并允许显式传入参数覆盖环境变量值；当调用方未显式传入基础地址时，系统 MUST 使用默认 FMP stable base URL。

#### Scenario: 未显式传入配置时从环境变量加载
- **WHEN** 调用方创建客户端时未传入 `api_key` 和 `api_base`
- **THEN** 系统 MUST 尝试从环境变量读取 `FMP_API_KEY`
- **AND** 系统 MUST 使用默认的 FMP stable base URL，或从 `FMP_API_BASE` 读取显式覆盖值

#### Scenario: 显式参数优先于环境变量
- **WHEN** 调用方在创建客户端时显式传入 `api_key` 或 `api_base`
- **THEN** 系统 MUST 优先使用显式传入的值
- **AND** 系统 MUST NOT 再用环境变量覆盖这些显式参数

#### Scenario: 缺少 API Key 时快速失败
- **WHEN** 调用方未传入 `api_key` 且环境变量中也不存在 `FMP_API_KEY`
- **THEN** 系统 MUST 在执行请求前抛出明确异常
- **AND** 系统 MUST NOT 发起匿名 HTTP 请求

### Requirement: 系统必须提供美股 IPO 决策核心接口
系统 MUST 提供覆盖美股 IPO 决策核心任务的接口方法，至少包括 IPO 日历、IPO 披露、IPO 招股书、SEC filings、公司概况、报价、流通股本和历史价格。

#### Scenario: 拉取即将上市公司的 IPO 日历与披露信息
- **WHEN** 调用方需要查看未来一段时间内的美股 IPO 安排和基础披露
- **THEN** 系统 MUST 提供对应的 IPO 日历和 IPO 披露方法
- **AND** 这些方法 MUST 支持把必要的日期和筛选参数传递给 FMP

#### Scenario: 查询单家公司 IPO 前后需要的核心公开信息
- **WHEN** 调用方需要围绕某个美股 IPO 标的查看 prospectus、SEC filings、profile、quote 或 shares float
- **THEN** 系统 MUST 提供对应的方法入口
- **AND** 这些方法 MUST 返回 FMP 原始 JSON 结果，供上层继续分析

### Requirement: 系统必须提供估值研究底表接口
系统 MUST 提供公司估值研究所需的底表接口，至少包括利润表、资产负债表、现金流量表、as reported 财报、财务增长和最新财报数据。

#### Scenario: 获取公司历史三表用于估值建模
- **WHEN** 调用方按股票代码请求年度或季度财务报表
- **THEN** 系统 MUST 提供利润表、资产负债表和现金流量表方法
- **AND** 这些方法 MUST 支持 period、limit 等常用查询参数

#### Scenario: 获取原始披露口径和增长口径数据
- **WHEN** 调用方需要 as reported 财报、财务增长或最新财报结果
- **THEN** 系统 MUST 提供对应方法
- **AND** 系统 MUST 不把这些返回值强制重塑为自定义领域对象

### Requirement: 系统必须提供估值指标与模型接口
系统 MUST 提供相对估值和绝对估值研究所需的指标接口，至少包括 key metrics、financial ratios、enterprise values、owner earnings、DCF、levered DCF、custom DCF 和分析师预期。

#### Scenario: 进行倍数法与经营质量对比
- **WHEN** 调用方需要查看 key metrics、TTM 指标、财务比率或企业价值
- **THEN** 系统 MUST 提供对应方法
- **AND** 这些方法 MUST 能按 symbol 和常见查询参数请求 FMP

#### Scenario: 进行 DCF 或一致预期研究
- **WHEN** 调用方需要查看 DCF、levered DCF、custom DCF 或 financial estimates
- **THEN** 系统 MUST 提供对应方法
- **AND** 系统 MUST 允许上层在这些原始结果上继续做自己的估值假设

### Requirement: 系统必须提供研究辅助接口
系统 MUST 提供与美股研究直接相关的辅助接口，至少包括 stock peers、company executives、executive compensation、earnings transcripts、positions summary、insider trades、treasury rates、market risk premium 和 economic indicators。

#### Scenario: 做管理层、市场预期和贴现参数辅助研究
- **WHEN** 调用方需要查看管理层信息、机构持仓、内部人交易、业绩会纪要或贴现参数
- **THEN** 系统 MUST 提供对应方法入口
- **AND** 这些方法 MUST 与核心研究方法共用同一鉴权和请求边界

### Requirement: 系统必须统一处理请求参数与 HTTP 失败边界
系统 MUST 通过统一的请求 helper 拼接 query 参数和 `apikey`，过滤空参数，并在 FMP 返回非成功状态时向上暴露真实 HTTP 错误。

#### Scenario: 统一拼接 apikey 与业务查询参数
- **WHEN** 调用方调用任意 FMP 方法并提供 symbol、date、period、limit 或其他查询参数
- **THEN** 系统 MUST 在同一 HTTP 请求中同时发送 `apikey` 和这些业务参数
- **AND** 系统 MUST 不把空字符串或空值参数无意义地附加到 query 中

#### Scenario: FMP 返回非 2xx 状态
- **WHEN** FMP 接口返回非成功状态码
- **THEN** 系统 MUST 让 HTTP 异常继续向上暴露
- **AND** 系统 MUST NOT 把失败结果伪装成空列表、空字典或成功响应

### Requirement: 系统必须把一期范围限制在 FMP 可覆盖的美股研究数据
系统 MUST 把一期能力限制在 FMP 可直接提供的美股 IPO 与估值研究数据，不把 A 股、港股发行制度细节或非 FMP 另类验证数据伪装成已支持能力。

#### Scenario: 调用方查阅一期支持范围
- **WHEN** 调用方根据客户端能力判断是否能直接研究某类数据
- **THEN** 系统 MUST 只承诺美股 IPO 与估值研究所需的 FMP 数据接口
- **AND** 系统 MUST NOT 把 A 股问询、港股配售结果或另类验证数据当成一期已接入能力
