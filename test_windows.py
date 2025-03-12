from pywinauto import Desktop


windows = Desktop(backend='uia').windows()
print(windows)


target_title = "XM-walmart101189-注册成功 - SunBrowser"
target_window = None

for w in windows:
    if target_title.lower() in w.window_text().lower():
        target_window = w
        break
    
if target_window:
    target_window.maximize()
    print(f"窗口 '{target_title}' 已最大化")
else:
    print(f"未找到标题包含 '{target_title}' 的窗口")