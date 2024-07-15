import win32gui
import win32con

def is_any_window_fullscreen():
    def enum_windows_callback(hwnd, lParam):
        class_name = win32gui.GetClassName(hwnd)
        if class_name != "CabinetWClass":
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            if style & win32con.WS_MAXIMIZE == win32con.WS_MAXIMIZE:
                raise Exception("Fullscreen window found")

        return True

    try:
        win32gui.EnumWindows(enum_windows_callback, None)
    except Exception:
        return True

    return False

# 调用判断函数
if is_any_window_fullscreen():
    print("有窗口全屏运行")
else:
    print("没有窗口全屏运行")
