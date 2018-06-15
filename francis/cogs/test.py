import requests
from bs4 import BeautifulSoup
import re


def get_news_gms_site():

    url = 'http://maplestory.nexon.net/news/'

    r = requests.get(url)

    if r.status_code == 200:
        return r.content
    else:
        return None


content = get_news_gms_site()

if content is not None:
    html = BeautifulSoup(content, 'html.parser')

    link = html.select_one('.news-container .news-item .text h3 a')
    desc = html.select_one('.news-container .news-item .text p')
    photo = html.select_one('.news-container .news-item .photo')

    print(link, desc, photo)

    news_id_re = re.compile('(/news/)(\d+)(/)')
    news_search = news_id_re.search(link['href'])
    news_id = news_search.group(2)

    d = {
        'id': news_search.group(2),
        'title': link.get_text(),
        'description': desc.get_text(),
        'link': f'http://maplestory.nexon.net{link["href"]}',
        'photo_url': photo['style'].lstrip('background-image:url(').rstrip(')')
    }

    print(d)
