import os
import json
import time
import random
import urllib3
import requests
from selenium import webdriver

driver = webdriver.Chrome()
urllib3.disable_warnings()
session = requests.Session()
session.verify = False

if os.path.exists('data.json'):
    with open('data.json', 'r', encoding='utf-8') as file:
        data_list = json.load(file)
else:
    data_list = []


def send_request_and_save_data(url, headers, payload, cookies, save_response=False, file_path='data.json'):
    global data_list

    try:
        response = session.post(url=url, headers=headers, json=payload, cookies=cookies, verify=False)
        response.raise_for_status()

        if save_response:
            data_list.append(response.json())
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data_list, file, ensure_ascii=False, indent=4)
            print(response.json())

    except requests.RequestException as e:
        print(f"请求失败: {e}")

    finally:
        time.sleep(0.1 * random.random() + 0.05)


if __name__ == "__main__":

    try:
        # 打开登录页面
        driver.get("https://ak.hypergryph.com/activity/jinyunyifan/")

        # 等待用户手动登录
        input("请手动登录，完成后按回车键继续...")

        # 获取登录后的 cookies
        cookies = driver.get_cookies()
        print("获取到的 cookies:", cookies)

        # 将 cookies 转换为字典格式
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}

        # 获取 x-role-token 和 x-account-token
        x_role_token = input("获取到的 x-role-token: ")
        x_account_token = input("获取到的 x-account-token: ")

        # 准备请求
        headers = {
            'content-length': '',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            'sec-ch-ua-mobile': '?0',
            'x-role-token': x_role_token,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'x-account-token': x_account_token,
            'origin': 'https://ak.hypergryph.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://ak.hypergryph.com/activity/jinyunyifan',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'priority': 'u=1, i',
        }

        while True:
            payload = {"betAmount": 20}
            cookie_dict['content-length'] = '16'
            send_request_and_save_data(
                url="https://ak.hypergryph.com/activity-server/jinyunyifan/api/core/spin",
                headers=headers, payload=payload, cookies=cookie_dict
            )

            for j in range(4):
                payload = {"reelIndex": j, "checkAchievement": False}
                cookie_dict['content-length'] = '40'
                send_request_and_save_data(
                    url="https://ak.hypergryph.com/activity-server/jinyunyifan/api/core/stop-reel",
                    headers=headers, payload=payload, cookies=cookie_dict, save_response=True if j == 3 else False
                )

    except Exception as e:
        print(e)

    finally:
        driver.quit()
