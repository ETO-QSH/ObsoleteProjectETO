import re
import json
import base64
import aiohttp
import asyncio
import urllib3
import requests
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from deepseek_api.converter import courses_courses_data, convert_exams_data, convert_grades_data, convert_evaluates_data

urllib3.disable_warnings()
session = requests.Session()

# 登录页面URL
LOGIN_URL = "https://zhlgd.whut.edu.cn/tpass/login?service=https%3A%2F%2Fjwxt.whut.edu.cn%2Fjwapp%2Fsys%2Fhomeapp%2Findex.do%3FforceCas%3D1"
# RSA公钥URL
RSA_URL = "https://zhlgd.whut.edu.cn/tpass/rsa?skipWechat=true"
# 学期代码URL
XNX_URL = "https://jwxt.whut.edu.cn/jwapp/sys/homeapp/api/home/currentUser.do"
# 课程信息API
KB_URL = "https://jwxt.whut.edu.cn/jwapp/sys/homeapp/api/home/student/courses.do"
# 考试信息API
KS_URL = "https://jwxt.whut.edu.cn/jwapp/sys/homeapp/api/home/student/exams.do"
# 成绩信息API
CJ_URL = "https://jwxt.whut.edu.cn/jwapp/sys/homeapp/api/home/student/scores.do"
# 总评信息API
ZP_URL = "https://jwxt.whut.edu.cn/jwapp/sys/cjcx/modules/cjcx/xscjcx.do"

def get_user_file(username):
    user_dir = Path("database") / username
    user_dir.mkdir(exist_ok=True)
    return user_dir / "dialogues.json"

async def save_login_data(username, password, auth_success):
    user_file = get_user_file(username)
    existing_data = {}
    if user_file.exists():
        with open(user_file, "r", encoding="utf-8") as f:
            existing_data = json.load(f)

    # 合并旧数据
    merged_data = {
        "authenticate": auth_success,
        "password": password if auth_success else None,
        "last_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "service": existing_data.get("service", {})
    }

    with open(user_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)

# 定义异步函数来获取数据
async def fetch_data(name, url, session, headers, params, cookies, username):
    try:
        async with session.get(url, headers=headers, params=params, cookies=cookies, ssl=False) as response:
            res = await response.json()
            if name == "KB":
                courses_courses_data(username, res)
            elif name == "KS":
                convert_exams_data(username, res)
            elif name == "CJ":
                convert_grades_data(username, res)
            elif name == "ZP":
                convert_evaluates_data(username, res)
            return res
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

async def login_and_fetch(username, password):
    try:
        # 步骤1：获取登录页面
        response = session.get(LOGIN_URL, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 步骤2：获取RSA公钥
        rsa_response = session.post(RSA_URL, verify=False)
        public_key = rsa_response.json()['publicKey']

        # 步骤3：加密用户名和密码
        public_key_pem = f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"
        public_key = RSA.import_key(public_key_pem)
        cipher = PKCS1_v1_5.new(public_key)

        encrypted_username = cipher.encrypt(username.encode('utf-8'))
        encrypted_password = cipher.encrypt(password.encode('utf-8'))
        encrypted_username = base64.b64encode(encrypted_username).decode('utf-8')
        encrypted_password = base64.b64encode(encrypted_password).decode('utf-8')

        # 步骤4：提取登录表单参数
        lt = soup.find('input', {'id': 'lt'})['value']
        execution = soup.find('input', {'name': 'execution'})['value']
        _eventId = soup.find('input', {'name': '_eventId'})['value']

        # 步骤5：构建登录请求数据
        login_data = {
            "rsa": "",
            "ul": encrypted_username,
            "pl": encrypted_password,
            "lt": lt,
            "execution": execution,
            "_eventId": _eventId
        }

        # 步骤6：设置请求头
        headers = {
            'Referer': LOGIN_URL,
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'origin': 'https://zhlgd.whut.edu.cn',
            'content-type': 'application/x-www-form-urlencoded',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'priority': 'u=0, i'
        }

        # 步骤7：提交登录请求
        response = session.post(LOGIN_URL, data=login_data, headers=headers, verify=False, allow_redirects=True)

        # 步骤8：解析登录响应，获取重定向URL
        if match := re.search(r"location\.href\s*=\s*['\"](.*?)['\"]", response.text):
            redirect_url = match.group(1)
            headers['Referer'] = f'https://jwxt.whut.edu.cn{redirect_url}'

            # 步骤9：获取学期代码
            xnxq_response = session.get(XNX_URL, headers=headers, verify=False)
            xnxq_json = xnxq_response.json()
            xnxqdm = xnxq_json['datas']['welcomeInfo']['xnxqdm']

            # 获取登录后的cookies
            cookies = session.cookies.get_dict()
            basepage = (headers, {'termCode': xnxqdm}, cookies, username)

            # 步骤10：并行获取四个表的数据
            async with aiohttp.ClientSession() as aio_session:
                tasks = [
                    fetch_data("KB", KB_URL, aio_session, *basepage),
                    fetch_data("KS", KS_URL, aio_session, *basepage),
                    fetch_data("CJ", CJ_URL, aio_session, *basepage),
                    fetch_data("ZP", ZP_URL, aio_session, *basepage)
                ]
                results = await asyncio.gather(*tasks)

            # print(zip(("课程数据:", "考试数据:", "成绩数据:", "总评数据:"), results))
            await save_login_data(username, password, True)
            return {"status": "success", "data": results}
        else:
            print("登录失败，未获取到重定向URL")
            await save_login_data(username, password, False)
            return {"status": "error", "message": "登录失败"}

    except Exception as e:
        print(f"Error: {e}")
        await save_login_data(username, password, False)
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    username = "1024005786"
    password = "*****"
    asyncio.run(login_and_fetch(username, password))
