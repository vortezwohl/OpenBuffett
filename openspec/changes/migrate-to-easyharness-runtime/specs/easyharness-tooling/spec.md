## ADDED Requirements

### Requirement: 自定义工具必须使用 EasyHarness 工具合同声明
系统中的项目自定义业务工具 MUST 使用 `easyharness.tool` 公共合同声明。项目 MUST NOT 再要求工具作者编写 `ToolSpec`、`ToolResult`、`ToolRegistry` 或其他项目私有工具协议对象。

#### Scenario: 新增业务工具
- **WHEN** 开发者新增一个项目业务工具
- **THEN** 该工具 MUST 以 `easyharness.tool` 形式声明名称、用途、参数、返回说明和常见失败
- **AND** 开发者 MUST NOT 再创建项目私有工具注册对象才能让该工具可用

### Requirement: 默认文件系统工具必须使用官方 fileglide toolset
系统默认提供的文件系统读写、搜索、管理和 inspect 能力 MUST 来自官方 `build_fileglide_tools(...)`。项目 MUST NOT 再维护一套等价的自研 fileglide tool specs 作为主链路默认实现。

#### Scenario: 构造默认工具集
- **WHEN** 系统装配默认 agent 工具集
- **THEN** 系统 MUST 使用官方 fileglide toolset 作为默认文件工具来源
- **AND** 该 toolset MUST 以当前 workspace root 或显式默认 root 作为作用域根

### Requirement: 工具返回值必须遵守 EasyHarness 公共输出语义
项目工具 MUST 通过 `ToolOutput`、普通字符串或 JSON 可序列化对象表达结果。系统 MUST NOT 要求工具通过项目私有 `ToolResult`、`metadata` 约定或自研错误包装协议才能被 runtime 正确消费。

#### Scenario: 工具成功返回结构化结果
- **WHEN** 某个项目工具成功返回结构化数据
- **THEN** 该结果 MUST 能被 EasyHarness 作为合法工具输出消费
- **AND** 调用链 MUST NOT 再依赖项目私有 `preview_text`、`detail_text` 或 `summary` 字段合同

#### Scenario: 工具执行失败
- **WHEN** 某个项目工具抛出异常或输入校验失败
- **THEN** 系统 MUST 通过 EasyHarness 工具失败语义对外暴露失败事件与失败结果
- **AND** 系统 MUST NOT 再通过项目私有错误映射层二次包装后才让 UI 可见

### Requirement: 工具装配层必须是普通对象集合而不是注册表协议
系统装配工具时 MUST 使用普通工具对象集合直接传入 EasyHarness agent。项目 MUST NOT 保留一个长期存在的项目私有工具注册表协议作为必经层。

#### Scenario: 组合默认工具与业务工具
- **WHEN** 系统需要同时装配官方 fileglide 工具和业务工具
- **THEN** 系统 MUST 以对象列表形式组合这些工具
- **AND** 组合过程 MUST NOT 依赖项目私有注册表提供名称解析或 provider bridge
