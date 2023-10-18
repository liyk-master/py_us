import requests
from urllib.parse import quote
import os

url = 'http://localhost:5244/api/auth/login'
d = {'Username': 'liyk', 'Password': 'jdmliyk1'}
r = requests.post(url, data=d)

import json

data = json.loads(r.text)
token = data.get('data').get('token')

url2 = "http://localhost:5244/api/fs/form"
file_path = 'F:\\迅雷下载\\video\\Movie\\樱花动漫\\日本动漫\\庙不可言\\Season 1'


def upload_file(url, remote_upload_file, file_path, token):
    total_size = os.path.getsize(file_path)
    headers = {
        "Authorization": token,
        "Content-Length": str(total_size),
        "file-path": quote("/阿里云盘/Movie/动漫/" + remote_upload_file, 'utf-8'),
    }
    files = {
        'file': (os.path.basename(file_path), open(file_path, 'rb'))
    }
    response = requests.put(url, headers=headers, files=files)
    print('Status Code:', response.status_code)
    print('Response:', response.text)


for root, dirs, files in os.walk(file_path):
    for file in files:
        file_path = os.path.join(root, file)
        if file_path.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm')):
            print(f"Uploading {file_path}")
            remote_upload_file = file_path.split('\\')[-3] + '/' + file_path.split('\\')[-2] + '/' + file_path.split('\\')[-1]
            upload_file(url2, remote_upload_file, file_path, token)
