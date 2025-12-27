import os
import time
import subprocess
from datetime import datetime

from public_object import log


def check_adb_path(adb_path):
    if os.path.isfile(adb_path):
        log(f"adb.exe 检查通过: {adb_path}")
        return True
    else:
        log(f"adb.exe 未找到: {adb_path}")
        return False


def check_adb_device(adb_path):
    result = subprocess.run([adb_path, 'devices'], capture_output=True, text=True)
    lines = result.stdout.strip().splitlines()
    for line in lines[1:]:
        if line.strip() and 'device' in line and 'offline' not in line:
            log("adb服务检测：已连接设备")
            return True
    log("adb服务检测：未检测到已连接的模拟器或设备")
    return False


def take_screenshot(adb_path, screenshot_dir):
    try:
        os.makedirs(screenshot_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        screenshot_path = os.path.join(screenshot_dir, f'screen_{timestamp}.png')

        log("开始截图到模拟器... --> ['/sdcard/screen.png']")
        subprocess.run([adb_path, 'shell', 'screencap', '-p', '/sdcard/screen.png'], check=True)
        log(f"拉取截图到本地: {screenshot_path}")
        subprocess.run([adb_path, 'pull', '/sdcard/screen.png', screenshot_path], check=True)
        log(f"截图已保存到: {screenshot_path}")
        return screenshot_path

    except Exception as e:
        log(f"截图失败：{e}")
        return None


def adb_tap(adb_path, x, y):
    try:
        time.sleep(1)
        log(f"点击操作: tap ({x}, {y})")
        subprocess.run([adb_path, 'shell', 'input', 'tap', str(x), str(y)], check=True)
        return x, y
    except Exception as e:
        log(f"点击操作失败：{e}")
        return None


def adb_swipe(adb_path, x1, y1, x2, y2, duration_ms=300):
    log(f"滑动操作: swipe ({x1}, {y1}) -> ({x2}, {y2}), 持续 {duration_ms} ms")
    subprocess.run([adb_path, 'shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(duration_ms)], check=True)


def adb_input_text(adb_path, text):
    log(f"输入文本: {text}")
    subprocess.run([adb_path, 'shell', 'input', 'text', text], check=True)


def adb_key_event(adb_path, keycode):
    log(f"发送按键事件: keyevent {keycode}")
    subprocess.run([adb_path, 'shell', 'input', 'keyevent', str(keycode)], check=True)

# 示例：点击屏幕中心
# adb_tap(adb_path, 540, 960)

# 示例：滑动
# adb_swipe(adb_path, 500, 1000, 500, 500, duration_ms=500=log_file)

# 示例：输入文本
# adb_input_text(adb_path, "HelloWorld")

# 示例：发送返回键
# adb_key_event(adb_path, 4)  # 4是安卓返回键
