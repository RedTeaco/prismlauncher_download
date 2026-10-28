"""从 PrismLauncher 弹窗提取文本（仅 Windows）。"""
from __future__ import annotations


def extract_blocked_mods_text() -> str | None:
    """连接到 PrismLauncher，读取其弹窗内所有文本。"""
    try:
        from pywinauto import Desktop
    except ImportError as e:  # 非 Windows 或未安装
        raise RuntimeError(
            "pywinauto 不可用（仅支持 Windows）。请在 Windows 上运行 "
            "`uv sync` 后重试。"
        ) from e

    try:
        app = Desktop(backend="uia").window(
            title_re=".*Prism Launcher.*"
        )
        print("正在等待 PrismLauncher 弹窗出现...")
        dialog = app.child_window(
            title_re=".*被屏蔽.*|.*blocked.*|.*missing.*", # 当前尽在简中测试
            control_type="Window",
        )
        if not dialog.exists():
            print(
                "未找到目标弹窗。请确保“找到被屏蔽的模组”窗口已打开。"
            )
            return None

        all_texts: list[str] = []
        for ctrl in dialog.descendants():
            if ctrl.texts():
                all_texts.extend(ctrl.texts())
            if ctrl.element_info.name:
                all_texts.append(ctrl.element_info.name)

        cleaned = [t.strip() for t in all_texts if t and t.strip()]
        unique = list(dict.fromkeys(cleaned))
        return "\n".join(unique)

    except Exception as e:
        print(f"提取过程中发生错误: {e}")
        return None