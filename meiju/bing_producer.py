import json

import pika
import requests
from bs4 import BeautifulSoup
import aiohttp, asyncio
import US_GPT_XC_Movie as us

# 定义一些常量和配置
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 Edg/94.0.992.50"
}
uri = 'http://www.meiju996.com'
delay_time = 30 # 延时队列的延时时间
queue_name = 'delay_queue' # 延时队列的名称
normal_queue = 'normal_queue' # 普通队列的名称

# 定义一个异步函数，用来获取页面的详情列表
async def fetch_html(session, url):
    try:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            ulBs4 = soup.find("ul", class_='stui-content__playlist column8 clearfix')
            detail_list = []
            if ulBs4:
                a_list = ulBs4.find_all('a')
                for a in a_list:
                    title = a.get('title')
                    href = uri + a.get('href')
                    detail_list.append({
                        "title": title,
                        "href": href
                    })
        return detail_list
    except Exception as e:
        print(f"Error in fetch_html: {e}")
        return []

# 定义一个异步函数，用来处理数据列表，并发送消息到延时队列
async def get_herf(data_list, channel):
    async with aiohttp.ClientSession(
            headers=headers
    ) as session:
        tasks = []
        for item in data_list:
            url = item['href']
            task = asyncio.create_task(fetch_html(session, url))
            tasks.append(task)
        detail_list = await asyncio.gather(*tasks)  # 使用 await 等待所有异步任务完成
        for i,v in enumerate(data_list):
            v['detail'] = detail_list[i]
            for va in v['detail']:
                message = {
                    'title': v['title'],
                    'detail': va,
                }
                message = json.dumps(message)
                print("message：",message)
                produce_message(channel, queue_name, message)
                await asyncio.sleep(delay_time)

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
        for i,v in enumerate(data_list):
            if i == 1:
                v['detail'] = detail_list[i]
                for va in v['detail']:
                    message = {
                        'title': v['title'],
                        'detail': va,
                    }
                    # message = json.dumps(message)
                    print("message：",message)
                    data.append(message)
        us.download_meiju_videos(data)

# 定义一个同步函数，用来获取主页的数据列表
def get_meiju():
    try:
        rep = requests.get(uri, headers=headers)
        soup = BeautifulSoup(rep.text, 'html.parser')
        ulBs4 = soup.find('ul', class_='stui-vodlist clearfix')
        data_list = []
        if ulBs4:
            a_list = ulBs4.find_all('a', class_='stui-vodlist__thumb lazyload')
            if a_list:
                for a in a_list:
                    title = a.get('title')
                    href = uri + a.get('href')
                    data = {
                        "title": title,
                        "href": href
                    }
                    data_list.append(data)
        return data_list
    except Exception as e:
        print(f"Error in get_meiju: {e}")
        return []

# 定义一个同步函数，用来创建延时队列
def create_delay_queue(channel, queue_name, delay_time):
    channel.queue_declare(queue=queue_name, arguments={
        'x-message-ttl': delay_time * 1000,  # 将延时时间转换为毫秒
        'x-dead-letter-exchange': '',  # 延时队列中的消息过期后发送到默认交换机
        'x-dead-letter-routing-key': normal_queue  # 延时队列中的消息过期后发送到普通队列
    })

# 定义一个同步函数，用来发送消息到指定队列
def produce_message(channel, queue_name, message):
    try:
        channel.basic_publish(exchange='',
                              routing_key=queue_name,
                              body=message)
        print(f" [x] Sent '{message}'")
    except Exception as e:
        print(f"Error in produce_message: {e}")

# 定义一个同步函数，用来创建连接和通道
def create_connection_and_channel():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        # 创建延时队列，延时时间为10秒
        create_delay_queue(channel, queue_name, delay_time)
        return connection, channel
    except Exception as e:
        print(f"Error in create_connection_and_channel: {e}")
        return None, None

# 定义一个同步函数，用来关闭连接
def close_connection(connection):
    try:
        connection.close()
    except Exception as e:
        print(f"Error in close_connection: {e}")


# 定义主函数
def main():
    # 创建连接和通道
    # connection, channel = create_connection_and_channel()
    # if connection and channel:
    #     # 获取主页的数据列表
    #     data_list = get_meiju()
    #     # 处理数据列表，并发送消息到延时队列
    #     asyncio.run(get_herf(data_list, channel))
    #     # 关闭连接
    #     close_connection(connection)
    data_list = get_meiju()
    asyncio.run(get_herf1(data_list))
    print(data_list)

if __name__ == '__main__':
    main()