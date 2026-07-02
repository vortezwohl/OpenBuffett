## 1. 结果回流契约

- [x] 1.1 调整 `src/core/strands_runtime.py` 的工具结果序列化路径，分离模型正文与 UI 预览，避免 `summary` 覆盖模型可操作正文
- [x] 1.2 为 `path.list`、`file.list`、`text.read` 等高频只读工具定义稳定的模型侧正文格式，并保留 timeline 现有预览/折叠能力
- [x] 1.3 更新或补充 runtime 测试，覆盖目录列举与文本读取结果会真实回给模型而不是退化为工具名或路径名

## 2. fileglide 路径契约与错误反馈

- [x] 2.1 在 `src/tool/fileglide_tools.py` 中为只读工具引入 `root`、`start`、`target` 的统一规范化逻辑
- [x] 2.2 支持无歧义绝对路径自动拆分为锚点 root 与相对路径，并为冲突的 `root + 绝对路径` 组合返回明确契约错误
- [x] 2.3 为 scope 违规、目标不存在、权限受限等高频失败补充面向模型的纠错文本，同时保留原始错误供 timeline metadata 与测试使用
- [x] 2.4 补充 fileglide 路径契约测试，覆盖绝对目录列举、绝对文件读取、冲突 root、契约失败与错误建议文本

## 3. 安全探索默认值

- [x] 3.1 调整 `path.list` 与 `file.list` 的默认探索策略为非递归优先，并确保根盘/锚点根目录首次探索不会默认深度递归
- [x] 3.2 校准默认 workbench 的读取路径与系统提示，明确“先列举当前层、再缩小范围、再读取内容”的只读探索闭环
- [x] 3.3 补充默认 workbench 行为测试，覆盖根盘探索、默认非递归和失败后可恢复重试的展示语义

## 4. 验证与收尾

- [x] 4.1 运行最小对照验证，确认 Windows 根盘、workspace 相对路径和绝对路径读取三类只读场景都可稳定收敛
- [x] 4.2 运行 `.venv\\Scripts\\python.exe -m unittest discover -s test -p "test_*.py"`
- [x] 4.3 运行 `.venv\\Scripts\\python.exe -m compileall src test`
