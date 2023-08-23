import os
from pathlib import Path
import subprocess
save_file = "G:\\"
# 遍历文件夹中的所有文件和子文件夹
for root, dirs, files in os.walk(save_file):
    for file in files:
        file_path = os.path.join(root, file)
        file_ext = os.path.splitext(file_path)[1]

        # 检查文件扩展名，删除符合条件的文件
        if file_ext in ['.key', '.ts', '.m3u8']:
        # if file_ext in ['.key', '.m3u8']:
            os.remove(file_path)
# folder_path = r"G:\\战士\\Season 3\\"
# update_m3u8 = "G:\\1_local.m3u8"
# detail_title = '第1集'
# folder_path = os.path.join(folder_path, detail_title + '.mp4')
# ouput_path = f'"{folder_path}"'
# try:
#     Path(folder_path).mkdir(parents=True, exist_ok=False)
#     print("文件夹创建成功！")
#     command = f'ffmpeg -allowed_extensions ALL -protocol_whitelist "file,http,crypto,tcp" -i {update_m3u8} -c copy {test}'
# except FileExistsError:
#     command = f'ffmpeg -allowed_extensions ALL -protocol_whitelist "file,http,crypto,tcp" -i {update_m3u8} -c copy {test}'
# except Exception as e:
#     print("文件夹创建失败:", e)
#
# # 执行命令行命令
# subprocess.run(command, shell=True, stdout=subprocess.DEVNULL)