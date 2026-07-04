## 1. 统一 repaint 生命周期

- [x] 1.1 在 `src/tui/app.py` 中抽出 mount 与 resize 共用的完整 repaint 调度 helper，统一负责布局稳定后的 `layout + repaint + _refresh_view(...)`
- [x] 1.2 调整 `src/tui/app.py` 的 `on_resize()`，让它只请求统一 repaint 路径，不再自己维护专属的 `refresh(...)` 与 `_refresh_view(...)` 顺序

## 2. 修复首帧时序

- [x] 2.1 调整 `src/tui/app.py` 的 `on_mount()`，移除过早的首帧 `_refresh_view(...)`，把首次内容写入延后到首轮布局稳定之后
- [x] 2.2 检查 `status-banner`、timeline、queue tray 和输入区的刷新调度，确保首帧与 resize 往返后共享同一视觉结果

## 3. 一致性回归验证

- [x] 3.1 更新 `test/test_tui_app.py`，新增“首次打开稳定结果”和“resize 往返后稳定结果”等价的回归用例
- [x] 3.2 调整当前只验证宽度变化的 resize 测试，使其覆盖关键区域真实渲染一致性，而不是只断言尺寸变化
- [x] 3.3 运行聚焦的 TUI 测试，确认首帧与 resize 往返后的界面结果一致
