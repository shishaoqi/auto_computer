import ctypes
from ctypes import wintypes

# 定义 HCURSOR 类型（Windows 句柄类型）
HCURSOR = wintypes.HANDLE

# 定义 POINT 结构体
class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG),
                ("y", wintypes.LONG)]

# 定义 CURSOR_INFO 结构体
class CURSOR_INFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD),
                ("flags", wintypes.DWORD),
                ("hCursor", HCURSOR),  # 使用新定义的 HCURSOR 类型
                ("ptScreenPos", POINT)]

# 定义 ICON_INFO 结构体（用于获取光标的详细信息）
class ICON_INFO(ctypes.Structure):
    _fields_ = [("fIcon", wintypes.BOOL),     # 标识是否为图标（True）或光标（False）
                ("xHotspot", wintypes.DWORD), # 热点 x 坐标
                ("yHotspot", wintypes.DWORD), # 热点 y 坐标
                ("hbmMask", wintypes.HBITMAP),# 掩码位图句柄
                ("hbmColor", wintypes.HBITMAP)]  # 颜色位图句柄

# 常量：表示光标正在显示
CURSOR_SHOWING = 0x00000001

# Windows 系统标准光标名称与对应的 ID
cursor_names = {
    "OCR_NORMAL":      32512,  # 标准箭头
    "OCR_IBEAM":       32513,  # 文本光标
    "OCR_WAIT":        32514,  # 等待光标
    "OCR_CROSS":       32515,  # 十字光标
    "OCR_UP":          32516,  # 上箭头
    "OCR_SIZENWSE":    32642,  # 左上-右下斜边调整
    "OCR_SIZENESW":    32643,  # 右上-左下斜边调整
    "OCR_SIZEWE":      32644,  # 水平调整
    "OCR_SIZENS":      32645,  # 垂直调整
    "OCR_SIZEALL":     32646,  # 移动
    "OCR_NO":          32648,  # 禁止
    "OCR_HAND":        32649,  # 手型
    "OCR_APPSTARTING": 32650   # 应用程序启动
}

# 获取 user32 模块
user32 = ctypes.windll.user32

def get_cursor_info():
    """调用 GetCursorInfo 获取当前鼠标信息"""
    ci = CURSOR_INFO()
    ci.cbSize = ctypes.sizeof(CURSOR_INFO)
    if not user32.GetCursorInfo(ctypes.byref(ci)):
        raise ctypes.WinError()
    return ci

def get_icon_info(hIcon):
    """调用 GetIconInfo 获取光标的详细信息"""
    icon_info = ICON_INFO()
    if not user32.GetIconInfo(hIcon, ctypes.byref(icon_info)):
        raise ctypes.WinError()
    return icon_info

def identify_cursor(cursor_handle):
    """
    通过与标准光标句柄比较来识别当前光标形状
    返回标准光标的名称，如 OCR_NORMAL、OCR_IBEAM 等；若无法识别，则返回 'Unknown cursor'
    """
    for name, cursor_id in cursor_names.items():
        # 加载系统标准光标
        hStdCursor = user32.LoadCursorW(0, cursor_id)
        if hStdCursor == cursor_handle:
            return name
    return "Unknown cursor"

def main():
    ci = get_cursor_info()
    if ci.flags & CURSOR_SHOWING:
        print("当前光标正在显示")
        print("光标句柄:", ci.hCursor)
        print("光标屏幕位置: (%d, %d)" % (ci.ptScreenPos.x, ci.ptScreenPos.y))
        # 识别标准光标
        cursor_name = identify_cursor(ci.hCursor)
        print("识别为:", cursor_name)
        
        # 获取更多光标信息
        icon_info = get_icon_info(ci.hCursor)
        print("光标详细信息:")
        print("     热点位置: (%d, %d)" % (icon_info.xHotspot, icon_info.yHotspot))
        print("     hbmColor: %s" % (hex(icon_info.hbmColor) if icon_info.hbmColor else None))
        print("     hbmMask: %s" % (hex(icon_info.hbmMask)))
    else:
        print("当前没有显示光标")

if __name__ == '__main__':
    main()
