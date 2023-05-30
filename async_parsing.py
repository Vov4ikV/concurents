import aiohttp
import asyncio
from aiofile import AIOFile
from bs4 import BeautifulSoup
import time
import os

URL = 'https://en.wikipedia.org/wiki/Blasphemy_law_in_Egypt'
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'}

# функция для получения странички из википедии
async def get_html():
    # создаем сессию
    async with aiohttp.ClientSession() as session:
        # в сессии выполняем get-запрос
        async with session.get(URL, headers=HEADERS) as response:
            return await response.text()

# функция для получения всех ссылок на страничке
async def get_links(html):
    # получаем объект BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    # ищем все ссылки в нем
    raw_links = soup.find_all('a', href=True)
    # выбираем все ссылки, начинающиеся с /wiki/
    links = list(filter(lambda x: x['href'].startswith('/wiki/'), raw_links))
    # дополняем относительную ссылку адресом сайта
    urls = list(map(lambda x: 'https://en.wikipedia.org' + x['href'], links))

    return urls

# функция записи в файл
async def aio_file_write(filename, text):
    async with AIOFile(filename, 'w') as file:
        await file.write(text)
        await file.fsync()

# функция скачивания странички
async def download_page(link):
    async with aiohttp.ClientSession() as session:
        async with session.get(link, headers=HEADERS) as response:
            a = await response.text('utf-8')
            path = os.getcwd()
            filename = link.rstrip("/").split("/")[-1]
            full_path = os.path.join(path, 'Downloads',filename)
            await aio_file_write(full_path, a)
            print(f'Downloaded file {link}')

# функция воркер (управляет задачами из очереди)
async def worker(q):
    while True:
        # достаем очередной элемент (ссылку) из очереди
        item = await q.get()
        # скачиваем ее
        await download_page(item)
        # ожидаем завершения
        q.task_done()


async def main():
    # создаем очередь
    q = asyncio.Queue()
    # получаем страничку и ссылки
    html = await get_html()
    urls = await get_links(html)

    # заполняем очередь ссылками
    for url in urls:
        q.put_nowait(url)

    # создаем задачи воркеру
    tasks = []
    # указываем количество воркеров
    for i in range(30):
        # каждая задача - работа воркера с элементов очереди
        task = asyncio.create_task(worker(q))
        # задачу добавляем в список задач
        tasks.append(task)

    # ожидаем завершения очереди
    await q.join()
    # ожидаем завершения задач
    for task in tasks:
        task.cancel()

    # Функция gather() модуля asyncio одновременно запускает объекты awaitable,
    # переданные в функцию как последовательность
    await asyncio.gather(*tasks, return_exceptions=True)

time_start = time.time()
asyncio.run(main())
time_end = time.time()
print(time_end-time_start)