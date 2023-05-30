import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import time
from threading import Thread
import queue
import os

ua = UserAgent()
# ссылка на случайную статью
RANDOM_URL = 'https://en.wikipedia.org/wiki/Special:Random'
HEADERS = {'User-Agent': ua.random}
# очередь
q = queue.Queue()

# функция получения ссылок со страницы
def get_links():
    # создаем сессию для запросов
    with requests.session() as s:
        # в ответе на запрос случайной статьи в resp.url будет ссылка на эту статью
        #resp = s.get(RANDOM_URL, headers=HEADERS)
        #url = resp.url
        url = 'https://en.wikipedia.org/wiki/Blasphemy_law_in_Egypt'
        html = s.get(url, headers=HEADERS).text
        # получаем объект BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

    # ищем все ссылки в нем
    raw_links = soup.find_all('a', href=True)
    # выбираем все ссылки, начинающиеся с /wiki/
    links = list(filter(lambda x: x['href'].startswith('/wiki/'), raw_links))
    # дополняем относительную ссылку адресом сайта
    urls = list(map(lambda x: 'https://en.wikipedia.org' + x['href'], links))

    return urls

# функция загрузки странички
def download_page(link: str)-> None:
    # создаем сессию
    with requests.session() as s:
        resp = s.get(link, headers=HEADERS)
        path = os.getcwd()
        filename = link.rstrip("/").split("/")[-1]
        full_path = os.path.join(path, 'Downloads', filename)

        with open(full_path, 'wb') as file:
            file.write(resp.content)
            print(f'Downloaded file {link}')

# функция воркер - берет из очереди ссылку и передает ее в функцию загрузки
def worker():
    while True:
        item = q.get()
        download_page(item)
        q.task_done()


def main():
    # получаем все ссылки
    urls = get_links()
    # добавляем их в очередь
    for url in urls:
        q.put(url)

    # создаем потоки и каждый поток отправляем в воркер
    for i in range(20):
        Thread(target=worker, daemon=True).start()

    # ждем завершения очереди
    q.join()

if __name__ == '__main__':
    t_start = time.time()
    main()
    t_end = time.time()
    print(t_end-t_start)