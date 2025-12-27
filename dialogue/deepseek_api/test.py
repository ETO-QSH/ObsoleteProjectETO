
from datetime import datetime
from openai import OpenAI
import json

api_key = "sk-*****"
user_info = "2373204754"
user_state = "已认证"
service_key = "WUT"

def read_json_file(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data


client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

Search_Json = {
    "Type": "[课程安排|考试安排|成绩查询], 根据用户需求可以多选, 以列表形式",
    "Time": "{当前时间}, 按照'%Y-%m-%d %H:%M:%S'格式的时间",
    "Update": "{数据更新需要[true|false]}, 默认不更新"
}

Service = {
    "WUT": "为已认证用户提供简单的个人信息查询服务，以及基础知识的问答，"
           "回答应该简短并且礼貌，执行查询服务时，从用户的信息中理解用户的需求"
           "整理为以下Json格式: {}".format(str(Search_Json)),
           "而后我会请求文件，你再依照内容进行回复"
    "BOT": "陪用户闲聊，依照用户需求进行互动，回答应该简短并且礼貌",
    "ETO": "尽可能帮助用户解决问题，做到详细清晰"
}

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system",
         "content": f"""当前时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                        你的身份: 由 'Dr.ETO' 搭建的 'deepseek v3' 语言模型接口
                        交流语言: 默认中文，如果用户有特殊要求，可以依照需求
                        你的工作: {Service[service_key]}
                        用户状态: {user_state}
                        用户信息: {user_info}"""},
        {"role": "user", "content": "Hello"},
    ],
    max_tokens=1024,
    temperature=0.7,
    stream=False
)

print(response.choices[0].message.content)
'''

import re
import base64
import urllib3
import requests
from bs4 import BeautifulSoup
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

urllib3.disable_warnings()
session = requests.Session()
login_page_url = "https://zhlgd.whut.edu.cn/tpass/login?service=https%3A%2F%2Fjwxt.whut.edu.cn%2Fjwapp%2Fsys%2Fhomeapp%2Findex.do%3FforceCas%3D1"
rsa_url = "https://zhlgd.whut.edu.cn/tpass/rsa?skipWechat=true"

response = session.get(login_page_url, verify=False)
soup = BeautifulSoup(response.text, 'html.parser')
rsa_response = session.post(rsa_url, verify=False)

body = {
    "public_key": rsa_response.json()['publicKey'],
    "lt": soup.find('input', {'id': 'lt'})['value'],
    "execution": soup.find('input', {'name': 'execution'})['value'],
    "_eventId": soup.find('input', {'name': '_eventId'})['value'],
}

headers = {
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

username = "1024005786"
password = "*****"

publicKey = f"""-----BEGIN PUBLIC KEY-----\n{body["public_key"]}\n-----END PUBLIC KEY-----"""
public_key = RSA.import_key(publicKey)
cipher = PKCS1_v1_5.new(public_key)

encrypted_username = cipher.encrypt(username.encode('utf-8'))
encrypted_password = cipher.encrypt(password.encode('utf-8'))
encryptedUsername = base64.b64encode(encrypted_username).decode('utf-8')
encryptedPassword = base64.b64encode(encrypted_password).decode('utf-8')

e_1 = cipher.encrypt('2'.encode('utf-8'))
E_1 = base64.b64encode(e_1).decode('utf-8')

data = {
    "rsa": "",
    "ul": encryptedUsername,
    "pl": encryptedPassword,
    "lt": body["lt"],
    "execution": body["execution"],
    "_eventId": body["_eventId"]
}

response = session.post(login_page_url, data=data, headers=headers, verify=False, allow_redirects=True)
match = re.search(r"location\.href\s*=\s*['\"](.*?)['\"]", response.text)

CP_URL = "https://jwxt.whut.edu.cn/jwapp/sys/cjcx/modules/cjcx/xscjcx.do"
session.cookies.update({"_WEU": E_1})
kbs = session.get(CP_URL, headers=headers, verify=False, allow_redirects=True)

print(len(kbs.json()["datas"]["xscjcx"]["rows"]))

a = {
    "password": "",
    "last_time": "",
    "service": {
        "(service_id)": {
            "last_time": "",
            "dialogues":
                [
                    {
                        "ask": "",
                        "ans": "",
                        "time": "",
                        "duration": ""
                    },
                    {
                        "ask": "",
                        "ans": "",
                        "time": "",
                        "duration": ""
                    }
                ]
        },
        "(service_id)": {
            "last_time": "",
            "dialogues":
                [
                    {
                        "ask": "",
                        "ans": "",
                        "time": "",
                        "duration": ""
                    },
                    {
                        "ask": "",
                        "ans": "",
                        "time": "",
                        "duration": ""
                    }
                ]
        }
    }
}
'''