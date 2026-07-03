## ADDED Requirements

### Requirement: 项目包结构必须只保留真实边界
系统 MUST 将 SmartIPO 项目代码限制在真实业务边界和 UI 边界内。长期存在的包或模块 MUST 对应当前可验证职责，例如 agent composition、业务工具、外部服务客户端或 UI 展示。

#### Scenario: 检查顶层源码目录
- **WHEN** 开发者检查 `src` 目录
- **THEN** 顶层源码 MUST NOT 包含未被当前主链使用的 `core`、`service`、`app` 或 `util` 包
- **AND** 保留的顶层模块或包 MUST 能对应当前真实职责

### Requirement: 未使用 helper 必须删除而不是整理
系统 MUST 删除未被生产代码或测试调用的 helper。项目 MUST NOT 为“以后可能用”保留公共 `util` 层，也不得把旧 helper 迁移到新目录继续保留。

#### Scenario: helper 没有真实调用点
- **WHEN** 某个 helper 只在自身定义处出现且没有生产或测试调用点
- **THEN** 系统 MUST 删除该 helper
- **AND** 系统 MUST NOT 通过重命名、移动或补文档来保留它

#### Scenario: 未来出现复用需求
- **WHEN** 未来两个或以上真实调用点需要同一段 helper 逻辑
- **THEN** 系统 MAY 在当轮需求中提取最小共享函数
- **AND** 该函数 MUST 放在最贴近调用方的模块或包内，直到有证据需要更高层公共包

### Requirement: 业务边界代码必须保留在明确位置
系统 MUST 保留并明确区分业务工具声明和外部服务客户端。EasyHarness 工具声明 MUST 位于业务工具层，HTTP/API 客户端 MUST 位于外部服务边界层。

#### Scenario: Seedream 工具调用图片生成客户端
- **WHEN** 默认 agent 需要暴露 Seedream 生图能力
- **THEN** 系统 MUST 通过 EasyHarness 工具对象暴露该业务能力
- **AND** 底层 HTTP 请求和 API 参数清洗 MUST 留在外部客户端边界内

#### Scenario: FMP 客户端保留为研究数据边界
- **WHEN** 项目需要查询 FMP IPO 或估值数据
- **THEN** 系统 MUST 保留外部客户端负责鉴权、URL、query 参数和 HTTP 错误透传
- **AND** 系统 MUST NOT 把这些 I/O 细节塞进 agent composition 入口

