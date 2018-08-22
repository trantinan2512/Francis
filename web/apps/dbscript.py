import requests
from bs4 import BeautifulSoup
import csv
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_config')
django.setup()
try:
    from apps.items.models import *
    from apps.jobs.models import *
    from apps.gachas.models import *
except ModuleNotFoundError:
    from web.apps.items.models import *
    from web.apps.jobs.models import *
    from web.apps.gachas.models import *


JOBS = [
    'Dark Knight',
    'Bowmaster',
    'Bishop',
    'Night Lord',
    'Corsair',
    'All',
    'None'
]

ITEM_TYPES = [
    'Weapon',
    'Armor',
    'Accessory',
    'Use',
    'Cash'
]

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

    ('Earrings', 'Accessory'),
    ('Pendant', 'Accessory'),
    ('Ring', 'Accessory'),
    ('Badge', 'Accessory'),
    ('Medal', 'Accessory'),
    ('Title', 'Accessory'),

]

ITEM_RANKS = [
    ('Normal', 5, 0.0),
    ('Rare', 10, 0.0),
    ('Epic', 15, 0.0),
    ('Unique', 20, 0.05),
    ('Legendary', 25, 0.05),
    ('Mythic', 30, 0.05),
]

ITEM_STATS = [
    'PHY ATK',
    'MAG ATK',
    'PHY DEF',
    'MAG DEF',
    'Max HP',
    'Max MP',
]


def dbscript():

    # create Class objects if not exist
    for c in JOBS:
        obj = Job.objects.filter(job=c)
        if not obj:
            job = Job.objects.create(job=c)
            print('Job created:', job)

    # create ItemType objects if not exist
    for t in ITEM_TYPES:
        obj = ItemType.objects.filter(type=t)
        if not obj:
            item_type = ItemType.objects.create(type=t)
            print('ItemType created:', item_type)

    # create ItemSubType objects if not exist
    for st, t in ITEM_SUB_TYPES:
        type = ItemType.objects.get(type=t)
        sub_type = ItemSubType.objects.filter(sub_type=st, type=type)
        if not sub_type:
            its = ItemSubType.objects.create(sub_type=st, type=type)
            print('ItemSubType created:', its)

    # create ItemRank objects if not exist
    for rank, max_star_level, emblem_rate in ITEM_RANKS:
        obj = ItemRank.objects.filter(rank=rank)
        if not obj:
            ir = ItemRank.objects.create(rank=rank, max_star=max_star_level, max_level=max_star_level, emblem_rate=emblem_rate)
            print('ItemRank created:', ir)

    # create ItemStat objects if not exist
    for o in ITEM_STATS:
        obj = ItemStat.objects.filter(stat=o)
        if not obj:
            item_stat = ItemStat.objects.create(stat=o)
            print('ItemStat created:', item_stat)


def get_content_by_url(url):

    r = requests.get(url)

    if r.status_code == 200:
        return r.content
    else:
        return None


def item_db():
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
                        data.update({'sub_type': 'Spear', 'main_stat': ['PHY ATK', ]})
                    elif data['job'] == 'Bowmaster':
                        data.update({'sub_type': 'Bow', 'main_stat': ['PHY ATK', ]})
                    elif data['job'] == 'Night Lord':
                        data.update({'sub_type': 'Claw', 'main_stat': ['PHY ATK', ]})
                    elif data['job'] == 'Bishop':
                        data.update({'sub_type': 'Wand', 'main_stat': ['MAG ATK', ]})
                    elif data['job'] == 'Corsair':
                        data.update({'sub_type': 'Gun', 'main_stat': ['MAG ATK', ]})
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

            if index == 32:
                step_job += 32
            elif index > 32 and index == 20 + step_job:
                step_job += 20

        # pprint(datas)

        for data in datas:
            print(data)
            job = Job.objects.get(job=data['job'])
            type = ItemType.objects.get(type=data['type'])
            sub_type = ItemSubType.objects.get(sub_type=data['sub_type'])
            item = Item.objects.filter(name=data['name'], job=job, type=type, sub_type=sub_type)
            if not item:
                item_obj = Item.objects.create(name=data['name'], job=job, type=type, sub_type=sub_type)
                for stat in data['main_stat']:
                    try:
                        stat_obj = ItemStat.objects.get(stat=stat)
                        item_obj.stats.add(stat_obj)
                    except ItemStat.DoesNotExist:
                        print(stat)


WEAPONS = ['Spear', 'Bow', 'Wand', 'Claw', 'Gun']
ARMORS = ['Hat', 'Outfit', 'Gloves', 'Shoes']
ACCESSORIES = ['Belt', 'Cape', 'Shoulder']
JOBS = ['Dark Knight', 'Bowmaster', 'Bishop', 'Night Lord', 'Corsair', ]
JOB_BRANCHES = ['Warrior', 'Bowman', 'Thief', 'Mage', 'Pirate', 'All']


def stat_range():
    sub_types = WEAPONS + ARMORS + ACCESSORIES
    with open('apps/msm_equipdata.csv', newline='') as csvfile:
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
                    if job == 'DarkKnight':
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

    for data in datas:

        rank = ItemRank.objects.get(rank=data['rank'])
        sub_type = ItemSubType.objects.get(sub_type=data['sub_type'])
        job = Job.objects.get(job=data['job'])
        if data['rank'] in ['Unique', 'Legendary', 'Mythic']:
            emblem = True
        else:
            emblem = False

        obj = ItemStatRange.objects.filter(
            rank=rank,
            sub_type=sub_type,
            job=job,
            job_specific=data['job_spec']
        )
        if not obj:
            if data['stat'] == 'PHY DEF':
                stat_1 = ItemStat.objects.get(stat='PHY DEF')
                ItemStatRange.objects.create(
                    rank=rank,
                    sub_type=sub_type,
                    job=job,
                    emblem=emblem,
                    stat=stat_1,
                    base=data['base'],
                    min=data['min'],
                    max=data['max'],
                    job_specific=data['job_spec']
                )
                stat_2 = ItemStat.objects.get(stat='MAG DEF')
                ItemStatRange.objects.create(
                    rank=rank,
                    sub_type=sub_type,
                    job=job,
                    emblem=emblem,
                    stat=stat_2,
                    base=data['base'],
                    min=data['min'],
                    max=data['max'],
                    job_specific=data['job_spec']
                )

            else:
                stat = ItemStat.objects.get(stat=data['stat'])
                ItemStatRange.objects.create(
                    rank=rank,
                    sub_type=sub_type,
                    job=job,
                    emblem=emblem,
                    stat=stat,
                    base=data['base'],
                    min=data['min'],
                    max=data['max'],
                    job_specific=data['job_spec']
                )


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

        for job, rank, item_name, rate in datas:
            if job == 'Bow Master':
                job = 'Bowmaster'
            j = Job.objects.get(job=job)
            r = ItemRank.objects.get(rank=rank)
            i = Item.objects.get(name=item_name)
            obj = TreasureBoxGacha.objects.filter(job=j, rank=r, item=i, rate=rate)
            if not obj:
                TreasureBoxGacha.objects.create(job=j, rank=r, item=i, rate=rate)
