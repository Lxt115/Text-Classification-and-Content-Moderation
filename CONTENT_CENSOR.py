# coding=utf-8

import json
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode
import ssl

# 防止https证书校验不正确
ssl._create_default_https_context = ssl._create_unverified_context

API_KEY = 'zba769OKi3De2UBRdzHI5VVG'
SECRET_KEY = 'E4wWk9WIHByjTW3IbLREbnFHPBf3fVMZ'
TEXT_CENSOR = "https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined"
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'

# 获取token
def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print(err)
    result_str = result_str.decode()
    result = json.loads(result_str)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not 'brain_all_scope' in result['scope'].split(' '):
            print('please ensure has check the  ability')
            exit()
        return result['access_token']
    else:
        print('please overwrite the correct API_KEY and SECRET_KEY')
        exit()


# 调用远程服务
def request(url, data):
    req = Request(url, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()
        result_str = result_str.decode()
        return result_str
    except URLError as err:
        print(err)


if __name__ == '__main__':
    basic_path = 'D:\Desktop\内容安全\code\豆瓣影评\\'
    # 获取access token
    token = fetch_token()
    # print(token)
    # 拼接文本审核url
    text_url = TEXT_CENSOR + "?access_token=" + token
    for i in range(1, 38):
        with open(basic_path + str(i) + ".txt", "r", encoding='utf-8-sig') as f:  # 打开文件
            text = f.read()  # 读取文件
            print("-----------审核第%d条文本内容中----------" % i)
            print(text)
            result = request(text_url, urlencode({'text': text}))
            print(result+'\n')
