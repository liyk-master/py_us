import asyncio
import subprocess, re
import aiofiles, aiohttp
from pathlib import Path
from bs4 import BeautifulSoup
import demjson3, urllib, json, execjs, os, time

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


async def download_video_segment(session, num, video_url, save_file):
    save_path = f"{save_file}{num}_{video_url.rsplit('/', 1)[-1]}"
    try:
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
        async with session.get(video_url, headers=headers) as response:
            if response.status == 200:
                async with aiofiles.open(save_path, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        await file.write(chunk)


async def get_iframe_content(iframe_src):
    async with aiohttp.ClientSession() as session:
        async with session.get(iframe_src) as response:
            if response.status == 200:
                return await response.text()
            else:
                return None


async def download_m3u8_and_key_file(message, save_file):
    pattern = r'"(https?://[^"]+\.m3u8)"'
    url = message.get('detail').get('href')
    num = re.sub(r"\D", "", message.get('detail').get('title'))
    title = message.get('title')
    season = message.get('season')
    detail_title = message.get('detail').get('title')
    async with aiohttp.ClientSession() as session:
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
                                    task = download_video_segment(session, num, video_url, save_file)
                                    tasks.append(task)

                                await asyncio.gather(*tasks)
                                print("视频下载完毕")
                                folder_path = f"{save_file}电视剧\\韩剧\\{title}\\{season}\\"
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


async def main():
    start = time.perf_counter()
    save_file = "G:\\"
    data = [
        {'title': '丧尸宇宙', 'detail': {'title': '第01集', 'href': 'https://www.333ys.tv/vodplay/102927-3-1.html'},
         'season': 'Season 1'},
        {'title': '丧尸宇宙', 'detail': {'title': '第02集', 'href': 'https://www.333ys.tv/vodplay/102927-3-2.html'},
         'season': 'Season 1'}
    ]
    for v in data:
        file_name = f"{save_file}电视剧\\韩剧\\{v.get('title')}\\{v.get('season')}\\{v.get('detail').get('title')}.mp4"
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
