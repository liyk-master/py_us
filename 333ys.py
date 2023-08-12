import asyncio
import subprocess, re
import aiofiles, aiohttp
from pathlib import Path
from bs4 import BeautifulSoup
import demjson3, urllib, json, execjs, os, time, requests

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 Edg/94.0.992.50"
}


async def download_file(session, url, save_path):
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
    season = message.get('season')
    detail_title = message.get('detail').get('title')
    # 创建一个信号量，指定最大并发数
    sem = asyncio.Semaphore(8)
    # 设置超时时间为 2 分钟
    timeout = aiohttp.ClientTimeout(total=120)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers=headers) as response:
            text = await response.text()
            pattern = r'"url":"(.*?)","url_next"'
            result = re.search(pattern, text)
            if result:
                url_content = result.group(1)
                title_encode = urllib.parse.quote(title)
                url = f"https://player.qifuda.com/?url={url_content}&jump=&title={title_encode}&thumb=&id=102927&nid={num}"
                async with session.get(url, headers=headers) as response:
                    # 获取到请求参数
                    text = await response.text()
                    # 使用正则表达式提取config对象内容
                    pattern = r"var config = ({[^}]*})"
                    match = re.search(pattern, text)
                    if match:
                        config_json = match.group(1)
                        config = demjson3.decode(
                            config_json)
                        # 请求出加密后的m3u8地址
                        async with session.post("https://player.qifuda.com/xinapi.php", headers=headers, data={
                            "url": config['url'],
                            "vkey": config['vkey'],
                            "token": config['token'],
                            "sign": "bKvCXSsVjPyTNr9R",
                        }) as response:
                            if response.status == 200:
                                resHtml = await response.text()
                                data = json.loads(resHtml)  # 获取json格式的数据)
                                async with aiofiles.open('player.qifuda.com_js_decode.js') as f:  # 读取js文件的内容
                                    js_code = await f.read()
                                context = execjs.compile(js_code)  # 编译和加载JS字符串
                                m3u8_url = context.call("getVideoInfo", data['url'])  # 调用JS函数，传入参数
                                print('m3u8_url', m3u8_url)  # 打印结果
                                # 下载m3u8
                                m3u8_save_path = f"{save_file}{num}.m3u8"
                                await download_file(session, m3u8_url, m3u8_save_path)
                                print("m3u8下载完毕")

                                async with aiofiles.open(m3u8_save_path, 'r') as file:
                                    m3u8_content = await file.read()
                                # 提取视频链接
                                video_urls = re.findall(r'^https?://[^\s]+\.ts$', m3u8_content, re.MULTILINE)
                                # 创建新的m3u8文件
                                base_url = video_urls[0][:video_urls[0].rindex('/') + 1]
                                replaced_content = m3u8_content.replace(base_url, f"{save_file}{num}_")
                                update_m3u8 = f"{save_file}{num}_local.m3u8"
                                async with aiofiles.open(update_m3u8, 'w') as file:
                                    await file.write(replaced_content)
                                # 创建并发任务
                                tasks = []
                                for i, video_url in enumerate(video_urls):
                                    task = download_video_segment(session, num, video_url, save_file, sem)
                                    tasks.append(task)

                                await asyncio.gather(*tasks)
                                print("视频下载完毕")
                                folder_path = f"{save_file}韩剧\\{title}\\{season}\\"
                                ouput_path = f'"{folder_path}{detail_title}.mp4"'
                                try:
                                    Path(folder_path).mkdir(parents=True, exist_ok=False)
                                    print("文件夹创建成功！")
                                    command = f'ffmpeg -allowed_extensions ALL -protocol_whitelist "file,http,crypto,tcp" -i {update_m3u8} -c copy {ouput_path}'
                                except FileExistsError:
                                    command = f'ffmpeg -allowed_extensions ALL -protocol_whitelist "file,http,crypto,tcp" -i {update_m3u8} -c copy {ouput_path}'
                                except Exception as e:
                                    print("文件夹创建失败:", e)

                                # 执行命令行命令
                                subprocess.run(command, shell=True, stdout=subprocess.DEVNULL)
                            else:
                                print("xinapi 获取失败")
                    else:
                        print("Config object not found")


async def download_videos(message, save_file):
    tasks = []
    task = download_m3u8_and_key_file(message, save_file)
    tasks.append(task)

    await asyncio.gather(*tasks)


# 获取每一集的参数
def get_every_num(uri,season,host,title_name):
    try:
        rep = requests.get(uri, headers=headers)
        soup = BeautifulSoup(rep.text, 'html.parser')
        ulBs4 = soup.find('ul', class_='myui-content__list scrollbar sort-list clearfix')
        data_list = []
        if ulBs4:
            a_list = ulBs4.find_all('a', class_='btn btn-default')
            if a_list:
                for a in a_list:
                    title = a.get_text()
                    Season = f"Season {season}"
                    # 使用正则表达式提取"第几季"
                    # match = re.search(r'第.+?季', title)
                    # if match:
                    #     num_dict = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
                    #                 "十": 10}
                    #     season_string = match.group()
                    #     match = re.search(r'[一二三四五六七八九十]+', season_string)
                    #     num = match.group()
                    #     if len(num) == 1:
                    #         Season = Season + str(num_dict[num])
                    #     if len(num) == 2:
                    #         Season = Season + str(num_dict[num[0]] + num_dict[num[1]])
                    #     # 将"第几季"替换为空，得到新的标题
                    #     title = re.sub(r'第.+?季', '', title)
                    # else:
                    #     Season = Season + "1"
                    href = host + a.get('href')
                    detail = {
                        "title": title,
                        "href": href,
                    }
                    data = {
                        "title": title_name,
                        "detail": detail,
                        "season": Season,
                    }
                    data_list.append(data)
        return data_list
    except Exception as e:
        print(f"Error in get_meiju: {e}")
        return []


async def main():
    start = time.perf_counter()
    save_file = "H:\\"
    # 获取333ys 每一集的地址
    data = get_every_num("https://www.333ys.tv/voddetail/101081.html",1,"https://www.333ys.tv/","绝世网红 (2023)")
    # data = [
    #     {'title': '步步惊心', 'detail': {'title': '第01集', 'href': 'https://www.333ys.tv/vodplay/88081-1-1.html'},
    #      'season': 'Season 1'},
    #     {'title': '步步惊心', 'detail': {'title': '第02集', 'href': 'https://www.333ys.tv/vodplay/88081-1-2.html'},
    #      'season': 'Season 1'},
    #     {'title': '步步惊心', 'detail': {'title': '第03集', 'href': 'https://www.333ys.tv/vodplay/88081-1-3.html'},
    #      'season': 'Season 1'},
    #     {'title': '步步惊心', 'detail': {'title': '第04集', 'href': 'https://www.333ys.tv/vodplay/88081-1-4.html'},
    #      'season': 'Season 1'},
    #     {'title': '步步惊心', 'detail': {'title': '第05集', 'href': 'https://www.333ys.tv/vodplay/88081-1-5.html'},
    #      'season': 'Season 1'},
    #     {'title': '步步惊心', 'detail': {'title': '第06集', 'href': 'https://www.333ys.tv/vodplay/88081-1-6.html'},
    #      'season': 'Season 1'},
    #     {'title': '步步惊心', 'detail': {'title': '第07集', 'href': 'https://www.333ys.tv/vodplay/88081-1-7.html'},
    #      'season': 'Season 1'},
    #     {'title': '步步惊心', 'detail': {'title': '第08集', 'href': 'https://www.333ys.tv/vodplay/88081-1-8.html'},
    #      'season': 'Season 1'},
    # ]
    for v in data:
        file_name = f"{save_file}韩剧\\{v.get('title')}\\{v.get('season')}\\{v.get('detail').get('title')}.mp4"
        if os.path.exists(file_name):
            print("视频存在")
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
