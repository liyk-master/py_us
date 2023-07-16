import re
import asyncio
import time
import httpx
import os
import pathlib
import aiofiles

HEADER = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 Edg/94.0.992.50"
}
TEMP_DIR = "./download"
os.makedirs(TEMP_DIR, exist_ok=True)

client = httpx.AsyncClient(headers=HEADER, follow_redirects=True)


class BuildIndex:
    pattern = r'"(https?://[^"]+\.m3u8)"'
    m3u8_filename = 'index.m3u8'
    enc_key_filename = 'enc.key'

    index_queue = asyncio.Queue()

    def __init__(
        self,
        client: httpx.AsyncClient,
        urls: list | tuple,
        workers: int,
    ) -> None:

        self.client = client
        self.urls = set(urls)
        self.workers = workers
        self.todo = asyncio.Queue()

    async def worker(self):
        while True:
            try:
                await self.process_one()
            except asyncio.CancelledError:
                return

    async def crawl(self, url):
        return await self.client.get(url)

    async def parse(self, resp: httpx.Response):

        result = re.search(self.pattern, resp.text)
        if result:
            m3u8_url = result.group(1)
            enc_key_url = m3u8_url.replace(self.m3u8_filename, self.enc_key_filename)
            file_dir = resp.url.path.rsplit("/", 1)[-1]
            return (file_dir, m3u8_url, enc_key_url)
        return None

    @classmethod
    async def update_index_queue(cls, data):
        await cls.index_queue.put(data)

    async def process_one(self):
        url = await self.todo.get()
        try:
            resp = await self.crawl(url)
            if (result := await self.parse(resp)) is not None:
                file_dir, m3u8_url, enc_key_url = result
                m3u8_resp = await self.crawl(m3u8_url)
                enc_key_resp = await self.crawl(enc_key_url)

                file_dir_path = pathlib.Path(TEMP_DIR, file_dir)
                await self.save(file_dir_path, self.m3u8_filename, m3u8_resp.content)
                await self.save(file_dir_path, self.enc_key_filename, enc_key_resp.content)
                await self.update_index_queue(file_dir)

        except Exception as exc:
            print(f"buildindex err!:{exc.args}")

        finally:
            self.todo.task_done()

    async def save(self, save_path: str | pathlib.Path, save_name: str,  data: bytes):
        os.makedirs(save_path, exist_ok=True)
        async with aiofiles.open(pathlib.Path(save_path, save_name), 'wb') as f:
            await f.write(data)

    async def run(self):
        for url in self.urls:
            await self.todo.put(url)

        workers = [asyncio.create_task(self.worker())
                   for _ in range(self.workers)]

        await self.todo.join()

        for worker in workers:
            worker.cancel()


class Download:
    pattern = r'^https?://[^\s]+\.ts$'
    m3u8_filename = 'index.m3u8'
    enc_key_filename = 'enc.key'

    def __init__(
        self,
        client: httpx.AsyncClient,
        task_dir_queue: asyncio.Queue,
        workers: int,
    ) -> None:

        self.client = client
        self.workers = workers
        self.task_lis_queue = task_dir_queue
        self.ts_queue = asyncio.Queue()

    async def update_ts_queue(self, datas):
        for data in datas:
            await self.ts_queue.put(data)

    async def worker(self, name):
        print(f"worker {name}")
        while True:
            try:
                await self.download()
            except asyncio.CancelledError:
                return

    async def read_m3u8(self, path: str | pathlib.Path):
        async with aiofiles.open(pathlib.Path(path, self.m3u8_filename), 'r', encoding="utf-8") as f:
            return await f.read()

    async def crawl(self, url):
        return await self.client.get(url)

    async def parse(self, m3u8_text: str) -> list:
        return re.findall(self.pattern, m3u8_text, re.MULTILINE)

    async def init_ts_queue(self):
        while True:
            file_dir = await self.task_lis_queue.get()
            try:
                path = pathlib.Path(TEMP_DIR, file_dir)
                m3u8_data = await self.read_m3u8(path)
                ts_urls = await self.parse(m3u8_data)
                await self.update_ts_queue([(u, path) for u in ts_urls])
            except asyncio.CancelledError:
                return
            except Exception as exc:
                print(f"download exc:{exc.args}")
            finally:
                self.task_lis_queue.task_done()

    async def download(self):
        url, path_dir = await self.ts_queue.get()
        try:

            resp = await self.crawl(url)
            await self.save(path_dir, resp)
        except:
            pass
        finally:
            self.ts_queue.task_done()

    async def save(self, dir_path: str | pathlib.Path, resp: httpx.Response):
        save_path = pathlib.Path(dir_path, resp.url.path.rsplit("/")[-1])
        async with aiofiles.open(save_path, 'wb') as f:
            await f.write(resp.content)

    async def run(self):
        workers = [asyncio.create_task(self.worker(f"worker-{i}"))
                   for i in range(self.workers)] + [
                       asyncio.create_task(self.init_ts_queue())
        ]
        await asyncio.sleep(3)
        await self.task_lis_queue.join()
        await self.ts_queue.join()

        for worker in workers:
            worker.cancel()


async def main(client: httpx.AsyncClient, urls: list | tuple, workers_num=30):
    buildindex = BuildIndex(client, urls, workers=workers_num)
    download = Download(client, buildindex.index_queue, workers=workers_num)
    return await asyncio.create_task(asyncio.wait([download.run(), buildindex.run()]))

if __name__ == '__main__':
    t1 = time.time()
    client = httpx.AsyncClient(headers=HEADER, follow_redirects=True)
    task = main(client, urls=["http://www.meiju996.com/play/3197-0-4.html"], workers_num=50)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(task)
    t2 = time.time()
    print(t2 - t1)
