import json

import pika
import US_GTP_Moive as us


def callback(ch, method, properties, body):
    # print(f" [x] Received {body}")
    ch.basic_ack(delivery_tag=method.delivery_tag)
    message = json.loads(body)
    print("message：",message)
    # 调用爬虫模块
    us.download_meiju_videos(message)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # 声明普通队列
    channel.queue_declare(queue='normal_queue')

    # 消费消息
    channel.basic_consume(queue='normal_queue',
                          on_message_callback=callback)

    print(' [*] Waiting for messages. To exit, press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    main()
