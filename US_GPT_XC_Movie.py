import os
import re
import time
import requests
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 Edg/94.0.992.50"
}

def download_file(url, save_path):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
    except (requests.exceptions.RequestException, IOError):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

def download_video_segment(num, video_url, save_file):
    save_path = f"{save_file}{num}_{video_url.rsplit('/', 1)[-1]}"
    try:
        response = requests.get(video_url, headers=headers)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
    except (requests.exceptions.RequestException, IOError):
        response = requests.get(video_url, headers=headers)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

def download_m3u8_and_key_file(message, save_file):
    pattern = r'"(https?://[^"]+\.m3u8)"'
    url = message.get('detail').get('href')
    num = re.sub(r"\D", "", message.get('detail').get('title'))
    title = message.get('title')
    detail_title = message.get('detail').get('title')

    response = requests.get(url, headers=headers)
    result = re.search(pattern, response.text)
    if result:
        m3u8_url = result.group(1)
        enc_key = m3u8_url.replace('index.m3u8', 'enc.key')

        # 下载m3u8
        m3u8_save_path = f"{save_file}{num}.m3u8"
        download_file(m3u8_url, m3u8_save_path)

        # 下载密钥文件
        key_save_path = f"{save_file}{num}.key"
        download_file(enc_key, key_save_path)

        print("下载完毕")
        # 读取并修改m3u8文件
        with open(m3u8_save_path, 'r') as file:
            m3u8_content = file.read()

        # 提取视频链接
        video_urls = re.findall(r'^https?://[^\s]+\.ts$', m3u8_content, re.MULTILINE)
        # 创建新的m3u8文件
        base_url = video_urls[0][:video_urls[0].rindex('/') + 1]
        replaced_content = m3u8_content.replace(base_url, f"{save_file}{num}_")
        key_url = f"{save_file}{num}.key"
        key_url = key_url.replace("\\", "\\\\")  # 将单反斜杠替换为双反斜杠
        replaced_content = replaced_content.replace("enc.key", key_url)
        update_m3u8 = f"{save_file}{num}_local.m3u8"

        with open(update_m3u8, 'w') as file:
            file.write(replaced_content)

        # 创建线程池
        with ThreadPoolExecutor(max_workers=50) as executor:
            # 并发下载视频片段
            for i, video_url in enumerate(video_urls):
                executor.submit(download_video_segment, num, video_url, save_file)

        print("视频下载完毕")
        # folder_path = f"{save_file}{title}\\"
        folder_path = f"{save_file}{title}/"  # linux版本
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

def download_meiju_videos(message):
    start = time.perf_counter()
    # save_file = "F:\\alist\\local\\"
    save_file = "/data/us_drama/"
    for v in message:
        download_m3u8_and_key_file(v, save_file)
        # 删除文件
        parent_dir = os.path.dirname(save_file)
        for root, dirs, files in os.walk(parent_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file_path)[1]

                # 检查文件扩展名，删除符合条件的文件
                if file_ext in ['.key', '.ts', '.m3u8']:
                    os.remove(file_path)

    end = time.perf_counter()
    elapsed = end - start
    print(f"程序运行时间为{elapsed}秒")

# 调用函数
# message = {'title': '行尸走肉：死亡之城', 'detail': {'title': '第1集', 'href': 'http://www.meiju996.com/play/50069-0-0.html'}}
# download_meiju_videos(message)