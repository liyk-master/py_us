import os
import re
import asyncio
import aiohttp
import subprocess

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 Edg/94.0.992.50"
}

async def download_file(session, url, save_path):
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                with open(save_path, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)
    except aiohttp.client_exceptions.ServerDisconnectedError:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                with open(save_path, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)

async def download_video_segment(session, num, video_url, save_file):
    save_path = f"{save_file}{num}_{video_url.rsplit('/', 1)[-1]}"
    try:
        async with session.get(video_url, headers=headers) as response:
            if response.status == 200:
                with open(save_path, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)
    except aiohttp.client_exceptions.ServerDisconnectedError:
        async with session.get(video_url, headers=headers) as response:
            if response.status == 200:
                with open(save_path, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)

async def download_m3u8_and_key_file(url, save_file, num):
    pattern = r'"(https?://[^"]+\.m3u8)"'

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
                with open(m3u8_save_path, 'r') as file:
                    m3u8_content = file.read()

                # 提取视频链接
                video_urls = re.findall(r'^https?://[^\s]+\.ts$', m3u8_content, re.MULTILINE)
                # 创建新的m3u8文件
                base_url = video_urls[0][:video_urls[0].rindex('/') + 1]
                replaced_content = m3u8_content.replace(base_url, f"{num}_")
                replaced_content = replaced_content.replace("enc.key", f"{num}.key")
                update_m3u8 = f"{save_file}{num}_local.m3u8"
                with open(update_m3u8, 'w') as file:
                    file.write(replaced_content)

                # 创建并发任务
                tasks = []
                for i, video_url in enumerate(video_urls):
                    task = download_video_segment(session, num, video_url, save_file)
                    tasks.append(task)

                await asyncio.gather(*tasks)

                print("视频下载完毕")
                command = f'ffmpeg -allowed_extensions ALL -protocol_whitelist "file,http,crypto,tcp" -i {update_m3u8} -c copy {save_file}行尸走肉\\{num}.mp4'
                # 执行命令行命令
                subprocess.run(command, shell=True, stdout=subprocess.DEVNULL)

async def main():
    tasks = []
    save_file = "F:\\Video\\"
    for num in range(4, 8):
        url = f"http://www.meiju996.com/play/3197-0-{num}.html"
        tasks.append(download_m3u8_and_key_file(url, save_file, num))

    await asyncio.gather(*tasks)

    # 删除文件
    parent_dir = os.path.dirname(save_file)
    for root, dirs, files in os.walk(parent_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file_path)[1]

            # 检查文件扩展名，删除符合条件的文件
            if file_ext in ['.key', '.ts', '.m3u8']:
                os.remove(file_path)

# 运行主程序
asyncio.run(main())