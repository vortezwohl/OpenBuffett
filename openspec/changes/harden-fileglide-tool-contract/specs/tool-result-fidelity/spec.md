## ADDED Requirements

### Requirement: Runtime SHALL return actionable tool body content to the model
当工具成功执行时，runtime MUST 将可操作正文回给模型，而不是仅返回工具名、路径名或其他仅供预览的摘要文本。

#### Scenario: Directory listing returns entries instead of tool name
- **WHEN** 模型调用 `path.list` 或 `file.list` 且工具成功返回目录项
- **THEN** 模型接收到的工具结果 MUST 包含可用于下一步决策的目录项正文
- **THEN** 结果 MUST NOT 退化为仅有 `path.list`、`file.list` 或类似占位摘要

#### Scenario: Text read returns readable content instead of only path summary
- **WHEN** 模型调用 `text.read` 成功读取文本文件
- **THEN** 模型接收到的工具结果 MUST 包含读取到的文本内容或稳定的正文摘要
- **THEN** 结果 MUST NOT 仅包含文件路径而缺失正文

### Requirement: Runtime SHALL preserve a separate UI preview channel
runtime MUST 允许 UI/timeline 使用简短预览与折叠详情，但这一预览通道 MUST 与模型侧正文通道分离。

#### Scenario: Timeline preview remains concise while model sees detail
- **WHEN** 一个工具结果较长且 UI 需要折叠展示
- **THEN** timeline MAY 使用简短预览和折叠详情
- **THEN** 模型侧工具结果 MUST 仍然保留足够的正文语义供后续推理使用

### Requirement: Runtime SHALL keep failure bodies diagnostically useful to the model
当工具失败时，runtime MUST 回给模型能够支持下一步纠错的失败正文，而不是只保留通用异常标题或空结果。

#### Scenario: Model can infer a retry from failure body
- **WHEN** 只读 fileglide 工具因契约误用、作用域违规、目标不存在或权限受限而失败
- **THEN** 模型接收到的失败正文 MUST 指明失败类别或修正方向
- **THEN** 失败正文 MUST 比单纯的工具名或空文本更具诊断性
