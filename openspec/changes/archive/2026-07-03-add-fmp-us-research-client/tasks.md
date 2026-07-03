## 1. FMP 客户端骨架

- [x] 1.1 在 `src/ext/fmp.py` 新增中文文件级说明、`load_dotenv()`、默认 base URL / timeout 常量，以及 `FmpClient` 初始化骨架
- [x] 1.2 实现 API Key 与 base URL 解析逻辑，约定 `FMP_API_KEY`、`FMP_API_BASE`，并支持显式参数覆盖环境变量
- [x] 1.3 实现统一 `_get()` helper，负责 `apikey` 注入、空参数过滤、HTTP GET、`raise_for_status()` 与 JSON 返回
- [x] 1.4 为客户端增加最小便捷入口或导出方式，确保调用方无需手工拼装 FMP 请求

## 2. IPO 决策与估值核心接口

- [x] 2.1 接入美股 IPO 决策核心方法：IPO 日历、IPO 披露、IPO 招股书、SEC filings、公司概况、报价、流通股本、历史价格
- [x] 2.2 接入估值研究底表方法：利润表、资产负债表、现金流量表、as reported 财报、财务增长、最新财报
- [x] 2.3 接入估值指标与模型方法：key metrics、TTM 指标、financial ratios、enterprise values、owner earnings、DCF、levered DCF、custom DCF
- [x] 2.4 接入研究常用横向比较方法：financial estimates、price target consensus、stock peers

## 3. 研究辅助接口与边界收口

- [x] 3.1 接入管理层与治理辅助方法：company executives、executive compensation、earnings transcripts
- [x] 3.2 接入市场辅助方法：positions summary、latest/search insider trades、insider trade statistics
- [x] 3.3 接入贴现参数与宏观辅助方法：treasury rates、market risk premium、economic indicators
- [x] 3.4 复查方法命名、注释和参数透传边界，确保一期范围只承诺美股 FMP 可覆盖数据，不混入 A/H 股或另类数据能力

## 4. 最小验证

- [x] 4.1 新增 FMP 客户端配置测试，验证缺失 `FMP_API_KEY` 时会快速失败，且显式参数优先于环境变量
- [x] 4.2 新增请求 helper 测试，验证 `_get()` 会统一拼接 `apikey`、过滤空参数并调用正确 URL
- [x] 4.3 新增代表性 endpoint 测试，至少覆盖 1 个 IPO 方法、1 个财报方法和 1 个估值指标方法的 path / 参数映射
- [x] 4.4 新增失败测试，验证 FMP 返回非 2xx 状态时 HTTP 异常继续向上暴露，不会被伪装成成功结果
