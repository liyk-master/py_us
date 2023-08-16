import time, os
import asyncio, aiofiles, aiohttp
from bs4 import BeautifulSoup
import requests, re, subprocess
from pathlib import Path
from urllib.parse import urlparse

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 Edg/94.0.992.50"
}


async def download_file(session, url, save_path, headers):
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                async with aiofiles.open(save_path, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        await file.write(chunk)
    except (
            aiohttp.client_exceptions.ServerDisconnectedError, aiohttp.ClientPayloadError,
            asyncio.exceptions.TimeoutError):
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                async with aiofiles.open(save_path, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        await file.write(chunk)


async def download_video_segment(session, num, video_url, save_file, sem):
    save_path = f"{save_file}{num}_{video_url.rsplit('/', 1)[-1]}"
    try:
        async with sem:
            async with session.get(video_url, headers=headers) as response:
                if response.status == 200:
                    async with aiofiles.open(save_path, 'wb') as file:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            await file.write(chunk)
    except (
            aiohttp.client_exceptions.ServerDisconnectedError, aiohttp.ClientPayloadError,
            asyncio.exceptions.TimeoutError):
        async with sem:
            async with session.get(video_url, headers=headers) as response:
                if response.status == 200:
                    async with aiofiles.open(save_path, 'wb') as file:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            await file.write(chunk)


async def download_m3u8_and_key_file(message, save_file):
    url = message.get('detail').get('href')
    num = re.sub(r"\D", "", message.get('detail').get('title'))
    title = message.get('title')
    title = title.strip()
    season = message.get('season')
    detail_title = message.get('detail').get('title')
    # 创建一个信号量，指定最大并发数
    sem = asyncio.Semaphore(8)
    # 设置超时时间为 2 分钟
    timeout = aiohttp.ClientTimeout(total=120)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            # 'Content-Length': '35',
            # 'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': '__51vcke__K63hAtUOftqyOSHq=45b1344e-daef-558a-beb3-4f8a0446166e; __51vuft__K63hAtUOftqyOSHq=1691848532135; qike123=%u80FD%u5E72%u7684%u732B%u4ECA%u5929%u4E5F%u5FE7%u90C101^http%3A//www.yinghuavideo.com/v/5954-1.html_$_%u80FD%u5E72%u7684%u732B%u4ECA%u5929%u4E5F%u5FE7%u90C106^http%3A//www.yinghuavideo.com/v/5954-6.html_$_%u80FD%u5E72%u7684%u732B%u4ECA%u5929%u4E5F%u5FE7%u90C105^http%3A//www.yinghuavideo.com/v/5954-5.html_$_|; __51uvsct__K63hAtUOftqyOSHq=5; __vtins__K63hAtUOftqyOSHq=%7B%22sid%22%3A%20%2283c50d13-3541-56b9-a7b9-dc2139940132%22%2C%20%22vd%22%3A%202%2C%20%22stt%22%3A%204535%2C%20%22dr%22%3A%204535%2C%20%22expires%22%3A%201691909367311%2C%20%22ct%22%3A%201691907567311%7D',
            'Host': 'www.yinghuavideo.com',
            'Pragma': 'no-cache',
            'Referer': 'http://www.yinghuavideo.com/v/5954-6.html',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        async with session.get(url, headers=headers) as response:
            text = await response.text()
            soup = BeautifulSoup(text, 'html.parser')
            divBs4 = soup.find('div', id="playbox")
            if divBs4:
                url_content = divBs4.get('data-vid')
                pattern = r"http.*?\.m3u8"
                match = re.search(pattern, url_content)
                if match:
                    url = match.group()
                else:
                    print("未找到m3u8文件，建议查看")
                    exit()
                # url = url_content.replace("$mp4", "")
                flag = False
                if "cdn" in url_content or "vip" in url_content:
                    flag = True
                    uri = url.replace("index.m3u8", "")
                else:
                    # parsed_url = urlparse(url)
                    # uri = parsed_url.netloc
                    uri = "https://s9.fsvod1.com"
                # url = f"https://tup.yinghuavideo.com/?vid={url_content}"
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Sec-Ch-Ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': 'Windows',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    # 'Content-Type': 'application/x-www-form-urlencoded',
                    # 'Cookie': '__51vcke__K63hAtUOftqyOSHq=45b1344e-daef-558a-beb3-4f8a0446166e; __51vuft__K63hAtUOftqyOSHq=1691848532135; __51uvsct__K63hAtUOftqyOSHq=2; qike123=%u80FD%u5E72%u7684%u732B%u4ECA%u5929%u4E5F%u5FE7%u90C101^http%3A//www.yinghuavideo.com/v/5954-1.html_$_%u80FD%u5E72%u7684%u732B%u4ECA%u5929%u4E5F%u5FE7%u90C106^http%3A//www.yinghuavideo.com/v/5954-6.html_$_|; __vtins__K63hAtUOftqyOSHq=%7B%22sid%22%3A%20%22bf7a2c71-0114-5b31-bece-4652303711c7%22%2C%20%22vd%22%3A%2010%2C%20%22stt%22%3A%203502201%2C%20%22dr%22%3A%206187%2C%20%22expires%22%3A%201691855999999%2C%20%22ct%22%3A%201691855530675%7D',
                    # 'Host': 'www.yinghuavideo.com',
                    'Pragma': 'no-cache',
                    # 'Referer': 'http://www.yinghuavideo.com/v/5954-6.html',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
                }
                async with session.get(url, headers=headers) as response:
                    # 获取到请求参数
                    text = await response.text()
                    pattern = r'^.*\n(.*\.m3u8)$'
                    match = re.search(pattern, text, re.MULTILINE)
                    if match:
                        last_line = match.group(1)
                        m3u8_url = uri + last_line
                        print('m3u8_url', m3u8_url)  # 打印结果
                        parsed_url = urlparse(m3u8_url)
                        path = parsed_url.path
                        filename = os.path.basename(path)
                        uri2 = m3u8_url.replace(filename, "")
                        # 下载m3u8
                        m3u8_save_path = f"{save_file}{num}.m3u8"
                        await download_file(session, m3u8_url, m3u8_save_path, headers)
                        print("m3u8下载完毕")
                        async with aiofiles.open(m3u8_save_path, 'r') as file:
                            m3u8_content = await file.read()
                        pattern = r'^.*\n(.*\.ts)$'
                        video_urls = re.findall(pattern, m3u8_content, re.MULTILINE)
                        print("url", uri)
                        print("video_url：", video_urls[0])
                        if flag:
                            replaced_content = m3u8_content
                            for i, v in enumerate(video_urls):
                                replaced_content = replaced_content.replace(v, f"{save_file}{num}_{v}")
                                video_urls[i] = uri2 + v
                        else:
                            base_url = video_urls[0][:video_urls[0].rindex('/') + 1]
                            replaced_content = m3u8_content.replace(base_url, f"{save_file}{num}_")
                            for i, v in enumerate(video_urls):
                                video_urls[i] = "https://s9.fsvod1.com" + v
                        # 替换m3u8文件
                        async with aiofiles.open(m3u8_save_path, 'w', encoding='utf-8') as file:
                            await file.write(replaced_content)
                        # 创建并发任务
                        tasks = []
                        for i, video_url in enumerate(video_urls):
                            task = download_video_segment(session, num, video_url, save_file, sem)
                            tasks.append(task)

                        await asyncio.gather(*tasks)
                        print("视频下载完毕")
                        folder_path = f"{save_file}动漫-日本\\{title}\\{season}\\"
                        ouput_path = f'"{folder_path}{detail_title}.mp4"'
                        try:
                            Path(folder_path).mkdir(parents=True, exist_ok=False)
                            print("文件夹创建成功！")
                            command = f'ffmpeg -allowed_extensions ALL -protocol_whitelist "file,http,crypto,tcp" -i {m3u8_save_path} -c copy {ouput_path}'
                        except FileExistsError:
                            command = f'ffmpeg -allowed_extensions ALL -protocol_whitelist "file,http,crypto,tcp" -i {m3u8_save_path} -c copy {ouput_path}'
                        except Exception as e:
                            print("文件夹创建失败:", e)

                        # 执行命令行命令
                        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL)
                    else:
                        print("Config object not found")


def get_every_num(uri, class_name):
    try:
        rep = requests.get(uri, headers=headers)
        rep.encoding = "utf-8"
        soup = BeautifulSoup(rep.text, 'html.parser')
        divBs4 = soup.find('div', class_=class_name)
        ulBs4 = divBs4.find('ul')
        data_list = []
        if ulBs4:
            li_list = ulBs4.find_all('li')
            if li_list:
                for i, li in enumerate(li_list):
                    a = li.find('a')
                    title = a.find('img').get('alt')
                    Season = "Season "
                    # 使用正则表达式提取"第几季"
                    match = re.search(r'第.+?季', title)
                    if match:
                        num_dict = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
                                    "十": 10}
                        season_string = match.group()
                        match = re.search(r'[一二三四五六七八九十]+', season_string)
                        num = match.group()
                        if len(num) == 1:
                            Season = Season + str(num_dict[num])
                        if len(num) == 2:
                            Season = Season + str(num_dict[num[0]] + num_dict[num[1]])
                        # 将"第几季"替换为空，得到新的标题
                        title = re.sub(r'第.+?季', '', title)
                    else:
                        Season = Season + "1"
                    href = "http://www.yinghuavideo.com" + a.get('href')
                    data = {
                        "title": title,
                        "href": href,
                        "season": Season,
                    }
                    data_list.append(data)
        return data_list
    except Exception as e:
        print(f"Error in: {e}")
        return []


async def fetch_html(session, url):
    try:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            divBs4 = soup.find('div', class_='movurl')
            ulBs4 = divBs4.find("ul")
            detail_list = []
            if ulBs4:
                a_list = ulBs4.find_all('a')
                for a in a_list:
                    title = a.get_text()
                    href = "http://www.yinghuavideo.com" + a.get('href')
                    detail_list.append({
                        "title": title,
                        "href": href
                    })
        return detail_list
    except Exception as e:
        print("url：",url)
        print(f"Error in fetch_html: {e}")
        return []


async def get_herf1(data_list):
    async with aiohttp.ClientSession(
            headers=headers
    ) as session:
        tasks = []
        for item in data_list:
            url = item['href']
            task = asyncio.create_task(fetch_html(session, url))
            tasks.append(task)
        detail_list = await asyncio.gather(*tasks)  # 使用 await 等待所有异步任务完成
        data = []
        for i, v in enumerate(data_list):
            v['detail'] = detail_list[i]
            for va in v['detail']:
                message = {
                    'title': v['title'],
                    'detail': va,
                    'season': v['season'],
                }
                # message = json.dumps(message)
                data.append(message)
        return data


async def download_videos(message, save_file):
    tasks = []
    task = download_m3u8_and_key_file(message, save_file)
    tasks.append(task)

    await asyncio.gather(*tasks)


async def main():
    start = time.perf_counter()
    # url = "http://www.yinghuavideo.com/ribendongman/"
    url = "http://www.yinghuavideo.com/search/%E6%96%87%E8%B1%AA%E9%87%8E%E7%8A%AC/"
    save_file = "H:\\"
    # 爬取樱花中好看的日本动漫
    data_list = get_every_num(url, 'lpic')  # imgs 好看的 lpic 搜索的
    data = await get_herf1(data_list)
    # data = [
    #     {'title': '丧尸宇宙', 'detail': {'title': '第01集', 'href': 'https://www.333ys.tv/vodplay/102927-3-1.html'},
    #      'season': 'Season 1'},
    #     {'title': '丧尸宇宙', 'detail': {'title': '第02集', 'href': 'https://www.333ys.tv/vodplay/102927-3-2.html'},
    #      'season': 'Season 1'}
    # ]
    for v in data:
        title = (v.get('title')).strip()
        file_name = f"{save_file}动漫-日本\\{title}\\{v.get('season')}\\{v.get('detail').get('title')}.mp4"
        if os.path.exists(file_name):
            print("视频存在")
            continue
        if title == "假面骑士GEATS" or title == "海贼王" or title == "文豪野犬 汪！":
            print("太长跳过")
            continue
        await download_videos(v, save_file)
        await asyncio.sleep(3)
        # 删除文件
        parent_dir = os.path.dirname(save_file)
        for root, dirs, files in os.walk(parent_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file_path)[1]

                # 检查文件扩展名，删除符合条件的文件
                if file_ext in ['.key', '.ts', '.m3u8']:
                    os.remove(file_path)
        print("删除成功")

    # 记录程序结束运行的时间
    end = time.perf_counter()

    # 计算程序运行时间
    elapsed = end - start
    print(f"程序运行时间为{elapsed}秒")


# 使用 asyncio.run() 来运行异步函数
asyncio.run(main())
