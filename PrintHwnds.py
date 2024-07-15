import win32gui


def enum_windows_callback(hwnd, hwnds):
    if win32gui.IsWindowVisible(hwnd):
        window_title = win32gui.GetWindowText(hwnd)
        hwnds.append((hwnd, window_title))


hwnds = []
win32gui.EnumWindows(enum_windows_callback, hwnds)

for hwnd, window_title in hwnds:
    print("窗口句柄：", hwnd)
    print("窗口标题：", window_title)
    print("---")
