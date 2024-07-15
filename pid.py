import requests
URL = "https://pixiv.re/103714224.png"
open("D:/ETO.png", "wb").write(requests.get(URL).content)
