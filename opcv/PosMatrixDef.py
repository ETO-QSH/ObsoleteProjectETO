import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


def PosMatrix(screenshot):
    hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
    green_rgb = np.array([234, 240, 211], dtype=np.uint8)
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
        if w > 30 and h > 30:
            List.append((x, y))
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
                if x - 4 <= point[0] <= x + 4 and y - 4 <= point[1] <= y + 4:
                    found = True
                    break
            if found:
                abc[q].append(0)
            else:
                abc[q].append(1)
                kkk.append((x, y))
    return abc, kkk


imageX = cv2.imread('cropped_image_run.jpg')
imageY = cv2.imread('cropped_image_one.jpg')
