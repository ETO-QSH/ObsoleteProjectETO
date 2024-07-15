
import win32gui

def hide_window(window_title):
    hwnd = win32gui.FindWindow(None, window_title)
    win32gui.ShowWindow(hwnd, 0)  # 0 表示隐藏窗口
    #win32gui.ShowWindow(hwnd, 1)  # 1 表示显示窗口

window_title = "MuMu模拟器12"  # 替换为你要隐藏的窗口的标题
hide_window(window_title)
