
import cv2
import time
import ctypes
import win32ui
import win32api
import win32gui
import win32con
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim

imageX = cv2.imread('cropped_image_run.jpg')
imageY = cv2.imread('cropped_image_one.jpg')

def PosMatrix(screenshot):
    hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
    green_rgb = np.array([234, 240, 212], dtype=np.uint8)
    green_hsv = cv2.cvtColor(np.array([[green_rgb]]), cv2.COLOR_RGB2HSV)[0][0]
    tolerance = 0
    lower_green = np.array([green_hsv[0] - tolerance, green_hsv[1] - tolerance, green_hsv[2] - tolerance])
    upper_green = np.array([green_hsv[0] + tolerance, green_hsv[1] + tolerance, green_hsv[2] + tolerance])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    kernel = np.ones((5, 5), np.uint8)
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
    _, green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    List = []
    for contour in green_contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 5 and h > 5:
            center_x = x + w // 2
            center_y = y + h // 2
            List.append((center_x, center_y))
    abc = []
    abc_x, abc_y = set(), set()
    for i in List:
        index = len(List)
        for k in range(0, index):
            flag = True
            for o in range(9):
                if i[0] - 4 + o in abc_x:
                    flag = False
            if flag == True:
                abc_x.add(i[0])
        for k in range(0, index):
            flag = True
            for o in range(9):
                if i[1] - 4 + o in abc_y:
                    flag = False
            if flag == True:
                abc_y.add(i[1])
    kkk = []
    abc_x, abc_y = sorted(list(abc_x)), sorted(list(abc_y))
    for q, y in enumerate(abc_y):
        abc.append([])
        for p, x in enumerate(abc_x):
            found = False
            for point in List:
                if x - 3 <= point[0] <= x + 3 and y - 3 <= point[1] <= y + 3:
                    found = True
                    break
            if found:
                abc[q].append(0)
            else:
                abc[q].append(1)
                kkk.append((x, y))
    return abc, kkk

def capture_screenshot(hWnd, n):
    global left, top, right, bot
    #left, top, right, bot = win32gui.GetWindowRect(hWnd)
    left, top, right, bot = 471, 0, 975, 923
    width = int((right - left) * 1.5)
    height = int((bot - top) * 1.5)
    client_left, client_top, client_right, client_bot = win32gui.GetClientRect(hWnd)
    client_width = client_right - client_left
    client_height = client_bot - client_top
    border_width = width - client_width
    border_height = height - client_height
    hWndDC = win32gui.GetWindowDC(hWnd)
    mfcDC = win32ui.CreateDCFromHandle(hWndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    image = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
    resized_image = image.resize((int(width * 0.5), int(height * 0.5)))  # 将图像缩小为50%的分辨率
    #resized_image = resized_image.crop((0, 0, 378, 692))
    resized_image.save("pic\\screenshot_{}.jpg".format(n))
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hWnd, hWndDC)
    return 'pic\\screenshot_{}.jpg'.format(n)

def mouse_click(x, y):
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    scaled_x = int(x * 65536 / width + 1)
    scaled_y = int(y * 65536 / height + 1)
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, scaled_x, scaled_y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, scaled_x, scaled_y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, scaled_x, scaled_y, 0, 0)

n, check, click = 1, [], []

x1, y1 = 120, 415  # 左上角坐标
x2, y2 = 250, 490  # 右下角坐标

x3, y3 = 120, 465  # 左上角坐标
x4, y4 = 250, 540  # 右下角坐标

while True:
    big_screenshot = cv2.imread(capture_screenshot(3607852, n))
    screenshot = cv2.resize(big_screenshot, (int(big_screenshot.shape[1] * 0.5), int(big_screenshot.shape[0] * 0.5)))
    flag = PosMatrix(screenshot)
    if ssim(big_screenshot[y1:y2, x1:x2], imageY, multichannel=True) > 0.6 or ssim(big_screenshot[y3:y4, x3:x4], imageX, multichannel=True) > 0.6:
        time.sleep(0.5)
        #click.append(click.pop(0))
        click.insert(0, (0, 0))
        click.append((0, 0))
        for i in click:
            mouse_click(int(left * 1.5 + i[0] * 4), int(top * 1.5 + i[1] * 4))
            mouse_click(int(left * 1.5 + i[0] * 4), int(top * 1.5 + i[1] * 4))
            print(left, top, right, bot, i)
            print('mouse_click', (int(left * 1.5 + i[0] * 4), int(top * 1.5 + i[1] * 4)))
            time.sleep(0.5)
        n, check, click = 0, [], []
    print('len(flag[1])', len(flag[1]))
    if len(flag[1]) == 1:
        if len(check) == 0:
            check.append(flag[0])
            click.append(flag[1][0])
            n += 1
        elif flag[0] != check[-1]:
            check.append(flag[0])
            click.append(flag[1][0])
            n += 1
    time.sleep(0.5)
    print('n', n)
    print('click', click)
    print('-'*30)
