import os
import re
import asyncio
import aiohttp
import subprocess
import aiofiles
import time
from pathlib import Path

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 Edg/94.0.992.50"
}


async def get_proxy_list():
    proxy_list = []
    async with aiohttp.ClientSession() as session:
        async with session.get('http://127.0.0.1:5010/all/') as response:
            proxy = await response.json()
            for p in proxy:
                if p.get('https') == False:
                    proxy_list.append(p.get('proxy'))

    return proxy_list


async def download_file(session, url, save_path):
    try:
        # async with session.get(url, headers=headers,proxy=proxy) as response:
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


async def download_m3u8_and_key_file(message, save_file):
    pattern = r'"(https?://[^"]+\.m3u8)"'
    url = message.get('detail').get('href')
    num = re.sub(r"\D", "", message.get('detail').get('title'))
    title = message.get('title')
    detail_title = message.get('detail').get('title')
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            result = re.search(pattern, await response.text())
            if result:
                m3u8_url = result.group(1)
                enc_key = m3u8_url.replace('index.m3u8', 'enc.key')

                # 下载m3u8
                m3u8_save_path = f"{save_file}{num}.m3u8"
                await download_file(session, m3u8_url, m3u8_save_path)

                # 下载密钥文件
                key_save_path = f"{save_file}{num}.key"
                await download_file(session, enc_key, key_save_path)

                print("下载完毕")
                # 读取并修改m3u8文件
                async with aiofiles.open(m3u8_save_path, 'r') as file:
                    m3u8_content = await file.read()

                # 提取视频链接
                video_urls = re.findall(r'^https?://[^\s]+\.ts$', m3u8_content, re.MULTILINE)
                # 创建新的m3u8文件
                base_url = video_urls[0][:video_urls[0].rindex('/') + 1]
                replaced_content = m3u8_content.replace(base_url, f"{save_file}{num}_")
                key_url = f"{save_file}{num}.key"
                key_url = key_url.replace("\\", "\\\\")  # 将单反斜杠替换为双反斜杠
                replaced_content = replaced_content.replace("enc.key", key_url)
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
                folder_path = f"{save_file}{title}\\"
                try:
                    Path(folder_path).mkdir(parents=True, exist_ok=False)
                    print("文件夹创建成功！")
                    command = f'ffmpeg -allowed_extensions ALL -protocol_whitelist "file,http,crypto,tcp" -i {update_m3u8} -c copy {folder_path}{detail_title}.mp4'
                except FileExistsError:
                    command = f'ffmpeg -allowed_extensions ALL -protocol_whitelist "file,http,crypto,tcp" -i {update_m3u8} -c copy {folder_path}{detail_title}.mp4'
                except Exception as e:
                    print("文件夹创建失败:", e)

                # 执行命令行命令
                subprocess.run(command, shell=True, stdout=subprocess.DEVNULL)

# async def main():
#     # 记录程序开始运行的时间
#     start = time.perf_counter()
#     tasks = []
#     save_file = "F:\\alist\\local\\"
#     for num in range(0, 5):
#         url = f"http://www.meiju996.com/play/50091-2-{num}.html"
#         tasks.append(download_m3u8_and_key_file(url, save_file, num))
#
#     await asyncio.gather(*tasks)
#
#     # 删除文件
#     parent_dir = os.path.dirname(save_file)
#     for root, dirs, files in os.walk(parent_dir):
#         for file in files:
#             file_path = os.path.join(root, file)
#             file_ext = os.path.splitext(file_path)[1]
#
#             # 检查文件扩展名，删除符合条件的文件
#             if file_ext in ['.key', '.ts', '.m3u8']:
#                 os.remove(file_path)
#
#     # 记录程序结束运行的时间
#     end = time.perf_counter()
#
#     # 计算程序运行时间
#     elapsed = end - start
#     print(f"程序运行时间为{elapsed}秒")
#
#
# # 运行主程序
# asyncio.run(main())


async def download_videos(message,save_file):
    tasks = []
    task = download_m3u8_and_key_file(message, save_file)
    tasks.append(task)

    await asyncio.gather(*tasks)


def download_meiju_videos(message):
    # 记录程序开始运行的时间
    start = time.perf_counter()

    save_file = "F:\\alist\\local\\"

    asyncio.run(download_videos(message,save_file))

    # 删除文件
    parent_dir = os.path.dirname(save_file)
    for root, dirs, files in os.walk(parent_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file_path)[1]

            # 检查文件扩展名，删除符合条件的文件
            if file_ext in ['.key', '.ts', '.m3u8']:
                os.remove(file_path)

    # 记录程序结束运行的时间
    end = time.perf_counter()

    # 计算程序运行时间
    elapsed = end - start
    print(f"程序运行时间为{elapsed}秒")


# if __name__ == '__main__':
#     download_meiju_videos(message)
