import urllib.request
import re

basic_path = 'D:\Desktop\内容安全\code\豆瓣影评\\'
file_num = 0
for i in range(2):
    print("获取第" + str(i + 1) + "页")
    url = "https://movie.douban.com/subject/1781126/reviews?start=" + str(i * 20)  # 确定要爬取的入口链接
    # 模拟成浏览器并爬取对应的网页 谷歌浏览器
    headers = {'User-Agent',
               'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
    opener = urllib.request.build_opener()
    opener.addheaders = [headers]
    data = opener.open(url).read().decode('utf8')
    time_pattern = re.compile('<span content=".*?" class=".*?">(.*?)</span>', re.S)
    time = re.findall(time_pattern, data)
    id_pattern = re.compile('<h2><a href="https://movie.douban.com/review/(.*?)/', re.S)
    id = re.findall(id_pattern, data)
    for j in range(len(id)):
        html = 'https://movie.douban.com/j/review/' + str(id[j]) + '/full'
        data = opener.open(html).read().decode('utf8')
        html = data
        content_pattern = re.compile('data-original(.*?)main-author', re.S)
        content = re.findall(content_pattern, html)
        text_pattern = re.compile('[\u4e00-\u9fa5|，、“”‘’：！~@#￥【】*（）——+。；？]+', re.S)
        text = re.findall(text_pattern, content[0])
        text = ''.join(text)
        name_pattern = re.compile('data-author=.*?"(.*?)"', re.S)
        name = re.findall(name_pattern, html)
        file_num += 1
        filename = str(file_num) + '.txt'
        with open(basic_path + filename, 'a', encoding='utf-8-sig') as f:
            f.write(str(text) + '\n')
            f.close()
