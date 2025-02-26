import re
import execjs
import urllib3
import requests
from bs4 import BeautifulSoup

execjs.runtime = execjs.get('Node')

with open('login_whut.js', 'r', encoding='utf-8') as f:
    js_code = f.read()

ctx = execjs.compile(js_code)

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
 'referer': 'https://zhlgd.whut.edu.cn/tpass/login?service=https%3A%2F%2Fjwxt.whut.edu.cn%2Fjwapp%2Fsys%2Fhomeapp%2Findex.do%3FforceCas%3D1',
 'accept-encoding': 'gzip, deflate, br, zstd',
 'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
 'priority': 'u=0, i'
}

username = "******"
password = "******"
publicKey = body["public_key"]

result = ctx.call('login', username, password, publicKey)

data = {
    "rsa": "",
    "ul": result['encryptedUsername'],
    "pl": result['encryptedPassword'],
    "lt": body["lt"],
    "execution": body["execution"],
    "_eventId": body["_eventId"]
}

response = session.post(login_page_url, data=data, headers=headers, verify=False, allow_redirects=True)
match = re.search(r"location\.href\s*=\s*['\"](.*?)['\"]", response.text)

KB = 'https://jwxt.whut.edu.cn/jwapp/sys/homeapp/api/home/student/courses.do'
params = {'termCode': '2024-2025-2'}
Kbs = session.get(KB, params=params, headers=headers, verify=False, allow_redirects=True)

print(Kbs.text)
