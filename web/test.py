import json
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
from bs4 import BeautifulSoup
import re
import dateparser
from pytz import timezone
from datetime import timedelta, datetime
# from config import BASE_DIR
# import config
import tweepy
from pprint import pprint
# from utils.db import initialize_db
from pprint import pprint
import csv
from apps.items.models import Item


def get_content_by_url(url):

    r = requests.get(url)

    if r.status_code == 200:
        return r.content
    else:
        return None


def testing(arg1, *args):
    print(arg1)
    print(args[0])


ITEM_SUB_TYPES = [

    ('Spear', 'Weapon'),
    ('Bow', 'Weapon'),
    ('Wand', 'Weapon'),
    ('Claw', 'Weapon'),
    ('Gun', 'Weapon'),

    ('Hat', 'Armor'),
    ('Outfit', 'Armor'),
    ('Gloves', 'Armor'),
    ('Shoes', 'Armor'),
    ('Belt', 'Armor'),
    ('Cape', 'Armor'),
    ('Shoulder', 'Armor'),

]


def test_func():
    items = Item.objects.all()
    print(items)


def gacha_rate():
    url = 'http://m.nexon.com/terms/353'
    content = get_content_by_url(url)

    if content is not None:
        html = BeautifulSoup(content, 'html.parser')

        # tds = html.select('td')
        table_rows = html.select('table:nth-of-type(2) tr')
        datas = []

        for row_no, row in enumerate(table_rows):
            if row_no == 0:
                continue
            else:
                data = []
                for col_no, d in enumerate(row.find_all('td'), start=1):
                    td = d.get_text().strip()
                    if '%' in td:
                        td = td.replace('%', '')
                        td_fl = float(td) / 100
                        data.append(td_fl)
                    else:
                        data.append(td)
            if data not in datas:
                datas.append(data)

        # pprint(datas)
        # print(len(datas))
        for job, rank, item_name, rate in datas:
            print(job, rank, item_name, rate)


WEAPONS = ['Spear', 'Bow', 'Wand', 'Claw', 'Gun']
ARMORS = ['Hat', 'Outfit', 'Gloves', 'Shoes']
ACCESSORIES = ['Belt', 'Cape', 'Shoulder']
JOBS = ['Dark Knight', 'Bowmaster', 'Bishop', 'Night Lord', 'Corsair', ]
JOB_BRANCHES = ['Warrior', 'Bowman', 'Thief', 'Mage', 'Pirate', 'All']


def item_range():
    sub_types = WEAPONS + ARMORS + ACCESSORIES
    with open('web/apps/msm_equipdata.csv', newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        datas = []
        for row in csv_reader:

            if row['sub_type'] in sub_types:

                row_data = {
                    'sub_type': row['sub_type'],
                    'rank': row['rank'],
                }

                if row['type'] == 'Weapon':
                    job = row['job']
                    if job == 'Darkknight':
                        row_data.update({'job': 'Dark Knight', 'job_spec': True})
                    elif job == 'Thief':
                        row_data.update({'job': 'Night Lord', 'job_spec': True})
                    elif job == 'Captain':
                        row_data.update({'job': 'Corsair', 'job_spec': True})
                    elif job == 'Bishop':
                        row_data.update({'job': 'Bishop', 'job_spec': True})
                    elif job == 'Bowman':
                        row_data.update({'job': 'Bowmaster', 'job_spec': True})
                    else:
                        print('New class:', job)
                        continue
                elif row['sub_type'] in ARMORS:
                    if row['cls'] == 'Warrior':
                        row_data.update({'job': 'Dark Knight', 'job_spec': False})
                    elif row['cls'] == 'Bowman':
                        row_data.update({'job': 'Bowmaster', 'job_spec': False})
                    elif row['cls'] == 'Thief':
                        row_data.update({'job': 'Night Lord', 'job_spec': False})
                    elif row['cls'] == 'Mage':
                        row_data.update({'job': 'Bishop', 'job_spec': False})
                    elif row['cls'] == 'Pirate':
                        row_data.update({'job': 'Corsair', 'job_spec': False})

                elif row['sub_type'] in ACCESSORIES:
                    row_data.update({'job': 'All', 'job_spec': False})

                if row['base_atk'] != '0':
                    extras = {
                        'stat': 'PHY ATK',
                        'base': float(row['base_atk'].replace(',', '')),
                        'min': float(row['min_atk'].replace(',', '')),
                        'max': float(row['max_atk'].replace(',', '')),
                    }
                elif row['base_matk'] != '0':
                    extras = {
                        'stat': 'MAG ATK',
                        'base': float(row['base_matk'].replace(',', '')),
                        'min': float(row['min_matk'].replace(',', '')),
                        'max': float(row['max_matk'].replace(',', '')),
                    }
                elif row['base_def'] != '0':
                    extras = {
                        'stat': 'PHY DEF',
                        'base': float(row['base_def'].replace(',', '')),
                        'min': float(row['min_def'].replace(',', '')),
                        'max': float(row['max_def'].replace(',', '')),
                    }
                row_data.update(extras)

                if row_data not in datas:
                    datas.append(row_data)

    pprint(datas)
    print(len(datas))


def get_data_from_term():
    url = 'http://m.nexon.com/terms/353'
    content = get_content_by_url(url)

    if content is not None:
        html = BeautifulSoup(content, 'html.parser')

        # tds = html.select('td')
        table_rows = html.select('table:nth-of-type(2) tr')
        datas = []
        step_job = 0

        for row_no, row in enumerate(table_rows):
            if row_no == 0:
                continue

            if 1 + step_job <= row_no <= 32 + step_job:

                if 1 + step_job <= row_no <= 4 + step_job:
                    row_data = {'type': 'Weapon'}
                elif row_no <= 20 + step_job:
                    row_data = {'type': 'Armor'}
                else:
                    row_data = {'type': 'Accessory'}

                for col_no, data in enumerate(row.find_all('td'), start=1):
                    if col_no == 1 and row_data['type'] == 'Accessory':
                        row_data.update({'job': 'All'})
                    elif col_no == 1:
                        job = 'Bowmaster' if data.get_text().strip() == 'Bow Master' else data.get_text().strip()
                        row_data.update({'job': job})

                    if col_no == 3:
                        row_data.update({'name': data.get_text().strip()})

                if row_data not in datas:
                    datas.append(row_data)
            if row_no == 32 + step_job:
                step_job += 32 * 4

        step_job = 0
        for index, data in enumerate(datas, start=1):

            if 1 + step_job <= index <= 4 + step_job:
                if data['type'] == 'Weapon':
                    if data['job'] == 'Dark Knight':
                        data.update({'sub_type': 'Spear', 'main_stat': 'PHY ATK'})
                    elif data['job'] == 'Bowmaster':
                        data.update({'sub_type': 'Bow', 'main_stat': 'PHY ATK'})
                    elif data['job'] == 'Night Lord':
                        data.update({'sub_type': 'Claw', 'main_stat': 'PHY ATK'})
                    elif data['job'] == 'Bishop':
                        data.update({'sub_type': 'Wand', 'main_stat': 'MAG ATK'})
                    elif data['job'] == 'Corsair':
                        data.update({'sub_type': 'Gun', 'main_stat': 'PHY ATK'})
            elif index <= 8 + step_job:
                data.update({'sub_type': 'Outfit', 'main_stat': ['PHY DEF', 'MAG DEF', 'Max HP']})
            elif index <= 12 + step_job:
                data.update({'sub_type': 'Hat', 'main_stat': ['PHY DEF', 'MAG DEF', 'Max HP']})
            elif index <= 16 + step_job:
                data.update({'sub_type': 'Gloves', 'main_stat': ['PHY DEF', 'MAG DEF', 'Max HP']})
            elif index <= 20 + step_job:
                data.update({'sub_type': 'Shoes', 'main_stat': ['PHY DEF', 'MAG DEF', 'Max HP']})
            elif index <= 24 + step_job:
                data.update({'sub_type': 'Belt', 'main_stat': ['PHY DEF', 'MAG DEF', 'Max MP']})
            elif index <= 28 + step_job:
                data.update({'sub_type': 'Cape', 'main_stat': ['PHY DEF', 'MAG DEF', 'Max MP']})
            elif index <= 32 + step_job:
                data.update({'sub_type': 'Shoulder', 'main_stat': ['PHY DEF', 'MAG DEF', 'Max MP']})

            print(index, data)

            if index == 32:
                step_job += 32
                print('Jumping to Bowmaster ***************')
            elif index > 32 and index == 20 + step_job:
                step_job += 20
                print('Jumping to next job ***************')

        # pprint(datas)


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