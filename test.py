import json
import requests
from bs4 import BeautifulSoup
import re
import dateparser
from pytz import timezone
from datetime import timedelta, datetime
from config import BASE_DIR
import config
import tweepy
from pprint import pprint
from utils.db import initialize_db


def get_content_by_url(url):

    r = requests.get(url)

    if r.status_code == 200:
        return r.content
    else:
        return None


def testing(arg1, *args):
    print(arg1)
    print(args[0])


def test_func():
    test_web_crawl()


def test_web_crawl():
    posted = False
    url = 'https://m.nexon.com/notice/1?client_id=MTY3MDg3NDAy'
    content = get_content_by_url(url)
    # print(content)
    if content is not None:
        html = BeautifulSoup(content, 'html.parser')

        news_labels = html.select('.list-group-item div .bolt-label')
        news_titles = html.select('.list-group-item .bolt-ellipsis')
        news_ids = html.select('.list-group-item .bolt-no-ellipsis')

        # print(html)
        print(news_labels.get_text())
        # for l in news_labels:


        # for l, t in zip(news_labels, news_titles):
        #     print(l.get_text(), t.get_text())

        # db = initialize_db()
        # site_gmsm = db.worksheet('site_gmsm')
        # site_gmsm_db = site_gmsm.get_all_records()

        # posted_ids = []
        # posted_titles = []
        # for record in site_gmsm_db:
        #     posted_ids.append(record['id'])
        #     posted_titles.append(record['title'])

        # id = 110
        # title = '08.07 Server Maintenance & Patch Note (COMPLETED)'

        # print((id, title) in zip(posted_ids, posted_titles))
        # for item in zip(posted_ids, posted_titles):
        #     print(item)

        # now = datetime.now()
        # vn_tz = now.replace(tzinfo=timezone('Asia/Ho_Chi_Minh'))

        # for label, title, id in zip(news_labels, news_titles, news_ids):
        #     data = {
        #         'id': id['data-id'],
        #         'date': vn_tz.strftime('%d/%m/%Y'),
        #         'time': vn_tz.strftime('%H:%M:%S'),
        #         'label': label.get_text().strip(),
        #         'title': title.get_text().strip()
        #     }


        #     news_url = f'https://m.nexon.com/notice/get/{data["id"]}?client_id=MTY3MDg3NDAy'
        #     news_content = get_content_by_url(news_url)
        #     # news_content_json = json.loads(news_content)
        #     news_html = BeautifulSoup(news_content, 'html.parser')

        #     img_link = 'N/A'
        #     images = news_html.select('img')
        #     for image in images:
        #         if 'cloudfront.net' in image['src']:
        #             img_link = image['src']
        #             break

        #     data_contents = {
        #         'link': news_url,
        #         'contents': news_html.select_one('.cnts').get_text().strip().replace('\n','---'),
        #         'image': img_link
        #     }
        #     data.update(data_contents)
        #     # if data['id'] == '140':
        #     # site_gmsm.insert_row(list(data.values()), index=2)
        #     print('**************')


if __name__ == "__main__":
    test_func()
