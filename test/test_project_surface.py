"""项目表面积瘦身回归测试。

该文件防止已删除的私有模型、装配包和 helper 层重新回流到主链，
确保底层能力继续交给 EasyHarness。
"""

from __future__ import annotations

from pathlib import Path
import unittest

from easyharness import Agent, ModelConfig

from src.agent import DEFAULT_SYSTEM_PROMPT


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"


class ProjectSurfaceTests(unittest.TestCase):
    """验证 OpenBuffett 只保留当前真实需要的项目边界。"""

    def test_removed_framework_packages_do_not_exist(self) -> None:
        """旧框架包和泛用 util 层不应继续存在。"""

        removed_paths = (
            "src/" + "core",
            "src/" + "service",
            "src/" + "app",
            "src/" + "util",
            "src/" + "model_config.py",
        )
        for relative_path in removed_paths:
            self.assertFalse((PROJECT_ROOT / relative_path).exists(), relative_path)

    def test_text_generation_uses_easyharness_native_agent(self) -> None:
        """纯文本能力应可由 EasyHarness 无工具 Agent 表达。"""

        model = ModelConfig(model="openai/demo", api_key="test-key")
        agent = Agent(
            model=model,
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            tools=[],
            enable_fileglide=False,
        )

        self.assertIsInstance(agent, Agent)

    def test_old_names_are_absent_from_runtime_source(self) -> None:
        """运行时代码不应再出现旧抽象名称。"""

        checked_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in SRC_ROOT.rglob("*.py")
            if "__pycache__" not in path.parts
        )

        old_names = (
            "Text" + "2Text",
            "Model" + "Hub",
            "src." + "app",
            "src." + "util",
            "src." + "core",
        )
        for old_name in old_names:
            self.assertNotIn(old_name, checked_text)


if __name__ == "__main__":
    unittest.main()
