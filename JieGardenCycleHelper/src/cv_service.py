import cv2
import numpy as np

from cnocr import CnOcr
from public_object import log


ocr = CnOcr()


def imread_unicode(path, flags=cv2.IMREAD_COLOR):
    """兼容中文路径的 cv2.imread 封装"""
    with open(path, 'rb') as f:
        buf = np.frombuffer(f.read(), np.uint8)
    img = cv2.imdecode(buf, flags)
    if img is None:
        raise FileNotFoundError(f"无法读取图片：{path}")
    return img


def match_template(screen_img_path, template_img_path, threshold=0.8):
    """
    :param screen_img_path: 屏幕截图路径
    :param template_img_path: 模板图片路径
    :param threshold: 匹配阈值
    """
    # 读取图片
    screen = imread_unicode(screen_img_path)
    template = imread_unicode(template_img_path)

    # 灰度化
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # 匹配
    res = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    log(f"尝试匹配图片：{template_img_path}")

    if max_val >= threshold:
        center = max_loc[0] + template.shape[1] // 2, max_loc[1] + template.shape[0] // 2
        roi = screen[max_loc[1]: max_loc[1] + template.shape[0], max_loc[0]: max_loc[0] + template.shape[1]]
        log(f"匹配到：{center}, 匹配值为：{max_val}")
        return center, roi, max_val
    else:
        log(f"未匹配到有效区域, 匹配值为：{max_val}")
        return None, None, max_val


def ocr_image(img):

    # cv2.imshow("ROI", img)
    # cv2.waitKey(0)  # 按任意键关闭
    # cv2.destroyAllWindows()

    digits = ocr.ocr_for_single_line(img)

    log(f"ocr_image：{digits}")
    return digits['text']
