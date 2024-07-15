
import pygetwindow as gw
from comtypes import CoInitialize
from pycaw.pycaw import AudioUtilities
from comtypes import CLSCTX_ALL
from comtypes import POINTER
from ctypes import cast
from pycaw.pycaw import IAudioEndpointVolume

# 初始化COM线程模型
CoInitialize()

# 获取默认渲染设备
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)

# 将接口对象转换为正确的类型
interface = cast(interface, POINTER(IAudioEndpointVolume))

# 设置音量
volume = 0.0  # 设置音量，范围从0.0到1.0
interface.SetMasterVolumeLevelScalar(volume, None)

# 获取当前全屏窗口
fullscreen_window = gw.getActiveWindow()

# 关闭全屏窗口
fullscreen_window.close()
