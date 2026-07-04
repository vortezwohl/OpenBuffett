## 1. 固定 ansi-dark 主题

- [x] 1.1 在 `src/tui/app.py` 中为 `AgentWorkbenchApp` 显式固定 `ansi-dark` 为应用主题默认值，确保直接实例化和入口启动都一致
- [x] 1.2 在 `src/tui/app.py` 中收口主题切换入口，移除 `Theme` system command，并让 `action_change_theme`、`search_themes`、`action_toggle_dark` 不再改变主题

## 2. 修复横向 resize 稳定性

- [x] 2.1 调整 `src/tui/app.py` 的主界面 CSS 和容器约束，让状态栏、timeline、queue tray、输入区在窄宽度下按当前可用宽度收缩
- [x] 2.2 为 `src/tui/app.py` 增加终端尺寸变化后的显式刷新路径，确保宽度变化后本地渲染内容和边框都会按新尺寸重新绘制
- [x] 2.3 为主界面关键带边框区域补齐一致的暗色表面绘制策略，消除缩宽后旧边框残影依赖透明背景的问题

## 3. 测试与验证

- [x] 3.1 更新 `test/test_tui_app.py`，验证应用启动后主题固定为 `ansi-dark`，且 system commands 中不再暴露 `Theme`
- [x] 3.2 更新 `test/test_tui_app.py`，验证触发主题切换相关 action 后主题仍保持为 `ansi-dark`
- [x] 3.3 更新 `test/test_tui_app.py`，使用 `Pilot.resize_terminal(...)` 验证终端横向缩窄和恢复后关键区域会随宽度重排且消息仍可见
- [x] 3.4 运行聚焦的 TUI 测试，确认主题锁定和横向 resize 回归场景通过验证
