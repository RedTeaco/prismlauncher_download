from pywinauto import Desktop

def extract_blocked_mods_text():
    """连接到 PrismLauncher，并读取其弹窗内的所有文本"""
    try:
        # 连接到 PrismLauncher 进程（进程名通常为 PrismLauncher.exe）
        app = Desktop(backend="uia").window(title_re=".*Prism Launcher.*")
        
        print("正在等待 PrismLauncher 弹窗出现...")
        
        # 尝试定位标题包含“找到被屏蔽的模組”或“找到被屏蔽的模組”的窗口
        # 由于标题可能因语言而异，这里使用正则模糊匹配
        dialog = app.child_window(title_re=".*被屏蔽.*|.*blocked.*|.*missing.*", control_type="Window")
        
        if not dialog.exists():
            print("未找到目标弹窗。请确保 PrismLauncher 的“找到被屏蔽的模組”窗口已打开。")
            return None
            
        # 获取弹窗内所有控件的文本
        # descendants() 会遍历所有子控件；texts() 会返回每个控件的文本列表
        all_texts = []
        for ctrl in dialog.descendants():
            # 获取控件本身的文本
            if ctrl.texts():
                all_texts.extend(ctrl.texts())
            # 获取控件的 Name 属性（通常包含主要文本）
            if ctrl.element_info.name:
                all_texts.append(ctrl.element_info.name)
                
        # 去重并过滤空字符串
        cleaned_texts = [t.strip() for t in all_texts if t and t.strip()]
        # 保留唯一项，但保持顺序
        unique_texts = list(dict.fromkeys(cleaned_texts))
        
        return "\n".join(unique_texts)
        
    except Exception as e:
        print(f"提取过程中发生错误: {e}")
        return None

if __name__ == "__main__":
    extracted_text = extract_blocked_mods_text()
    if extracted_text:
        print("\n--- 提取到的弹窗文本 ---")
        print(extracted_text)
        print("------------------------\n")