import os
import time
from datetime import datetime, timedelta

from adb_service import take_screenshot, adb_tap
from cv_service import match_template, ocr_image
from public_object import adb_path, screenshot_dir, picture_dir, ocr_pic, log, log_file, sleep_time


def match_and_tap(template):
    first_click = None
    while True:
        if screenshot := take_screenshot(adb_path, screenshot_dir):
            if center := match_template(screenshot, os.path.join(picture_dir, template))[0]:
                x, y = adb_tap(adb_path, *center)
                if first_click and (first_click[0] - x) ** 2 + (first_click[1] - y) ** 2 > 500:
                    break
                first_click = x, y
            elif first_click:
                time.sleep(sleep_time)
                break
        time.sleep(sleep_time)


def match_and_orc(template, rec):
    if screenshot := take_screenshot(adb_path, screenshot_dir):
        if res := match_template(screenshot, os.path.join(picture_dir, template), 0.60):
            center, roi, _ = res
            return ocr_image(roi[rec[1]: rec[3], rec[0]: rec[2]])
    return None


def match_only(template):
    if screenshot := take_screenshot(adb_path, screenshot_dir):
        if match_template(screenshot, os.path.join(picture_dir, template))[0]:
            return True
    return False


def safe_exit(code):
    [os.remove(os.path.join(screenshot_dir, f)) for f in os.listdir(screenshot_dir) if
     os.path.isfile(os.path.join(screenshot_dir, f))]
    log("屏幕截图已清理，程序退出运行")
    log_file.close()
    exit(code)


def delete_old_screenshots(folder_path=screenshot_dir, minutes=1):
    now = datetime.now()
    cutoff = now - timedelta(minutes=minutes)

    for filename in os.listdir(folder_path):
        if not filename.startswith("screen_") or not filename.endswith(".png"):
            continue

        try:
            timestamp_str = filename[7:-4]
            file_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S_%f")
        except ValueError:
            continue

        if file_time < cutoff:
            file_path = os.path.join(folder_path, filename)
            try:
                os.remove(file_path)
                print(f"已删除：{filename}")
            except Exception as e:
                print(f"删除失败：{filename}，原因：{e}")


def do_circle(live_state, policy):
    time.sleep(sleep_time)

    if not match_only(ocr_pic['退出']):
        log("未检测到标志物，出于安全考虑拒绝操作")
        return 0

    if match_only(ocr_pic['钱盒']):
        live_state.candle = int(match_and_orc(*ocr_pic['剩余烛火']))
        live_state.prize_count = int(match_and_orc(*ocr_pic['收藏品']))
        log(f"识别到剩余烛火：{live_state.candle}, 识别到收藏品数量：{live_state.prize_count}")

    live_state.originium = int(match_and_orc(*ocr_pic['源石锭']))
    live_state.tickets = int(match_and_orc(*ocr_pic['票券']))
    log(f"识别到源石锭：{live_state.originium}, 识别到票券：{live_state.tickets}")

    choice, sub_choice = policy(live_state)
    log(f"选择分支：{choice} - {sub_choice}")

    if choice == '茧成绢':
        if match_only(ocr_pic['钱盒']):
            match_and_tap(ocr_pic['钱盒'])

        match_and_tap(ocr_pic['重新投钱'])
        match_and_tap(ocr_pic['投钱确认'])
        match_and_tap(ocr_pic['投钱结束确认'])

        res = '投钱'

    else:
        if match_only(ocr_pic['收起']):
            match_and_tap(ocr_pic['收起'])

        match_and_tap(ocr_pic['小常乐'])
        match_and_tap(ocr_pic['前往出发'])

        while True:
            if match_only(ocr_pic['黍']):
                head = '黍'
                break
            if match_only(ocr_pic['年']):
                head = '年'
                break
            if match_only(ocr_pic['令']):
                head = '令'
                break
            time.sleep(sleep_time)

        if head != '令':
            log(f"常乐-{head}，不符合要求")
            return 1

        match_and_tap(ocr_pic['欣然应许'])
        match_and_tap(ocr_pic['确定这么做'])

        match_and_tap(ocr_pic[choice])
        match_and_tap(ocr_pic['确定这么做'])
        match_and_tap(ocr_pic['投钱结束确认'])

        if choice != '厉如锋':
            while True:
                if match_only(ocr_pic['收下']):
                    match_and_tap(ocr_pic['收下'])
                    match_and_tap(ocr_pic['确定这么做'])
                    match_and_tap(ocr_pic['事件结束确认'])
                    res = '成功'
                    break
                if match_only(ocr_pic['离开']):
                    match_and_tap(ocr_pic['离开'])
                    match_and_tap(ocr_pic['确定这么做'])
                    match_and_tap(ocr_pic['事件结束确认'])
                    res = '失败'
                    break
                if match_only(ocr_pic['还是算了']):
                    if int(match_and_orc(*ocr_pic['源石锭'])) >= live_state.standard:
                        match_and_tap(ocr_pic['来就来'])
                        match_and_tap(ocr_pic['确定这么做'])
                    else:
                        match_and_tap(ocr_pic['还是算了'])
                        match_and_tap(ocr_pic['确定这么做'])
                        match_and_tap(ocr_pic['事件结束确认'])
                    res = '再来'
                    break
        else:
            match_and_tap(ocr_pic[sub_choice])
            match_and_tap(ocr_pic['确定这么做'])
            match_and_tap(ocr_pic['事件结束确认'])

            res = sub_choice

        time.sleep(sleep_time)
    log(f"完成一次循环 - {res}")
