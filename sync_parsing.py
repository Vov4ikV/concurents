import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import time

ua = UserAgent()
RANDOM_URL = 'https://en.wikipedia.org/wiki/Special:Random'
HEADERS = {'User-Agent': ua.random}

def get_links():
    with requests.session() as s:
        #resp = s.get(RANDOM_URL, headers=HEADERS)
        #url = resp.url
        url = 'https://en.wikipedia.org/wiki/Blasphemy_law_in_Egypt'
        html = s.get(url, headers=HEADERS).text
        soup = BeautifulSoup(html, 'html.parser')

    raw_links = soup.find_all('a', href=True)
    links = list(filter(lambda x: x['href'].startswith('/wiki/'), raw_links))
    urls = list(map(lambda x: 'https://en.wikipedia.org' + x['href'], links))

    return urls

def load_pages(urls):
    with requests.session() as s:
        for link in urls:
            resp = s.get(link, headers=HEADERS)
            with open(f'Downloads/{link[link.rfind("/")+1:]}', 'wb') as file:
                file.write(resp.content)
                print(f'Download file {link}')


urls = get_links()

t_start = time.time()
load_pages(urls)
t_end = time.time()

print(t_end-t_start)
