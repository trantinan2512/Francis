import requests
from bs4 import BeautifulSoup
import csv
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.config.settings')
django.setup()

from web.apps.items.models import *
from web.apps.jobs.models import *
from web.apps.gachas.models import *


JOBS_BASE = [
    'Dark Knight', 'Bowmaster', 'Bishop', 'Night Lord', 'Corsair',
    'Dawn Warrior', 'Wind Archer', 'Blaze Wizard', 'Night Walker', 'Thunder Breaker',
    'All', 'None'
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
    ('2hSword', 'Weapon'),
    ('Staff', 'Weapon'),
    ('Knuckler', 'Weapon'),

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

    # create Job objects if not exist
    for c in JOBS_BASE:
        obj, created = Job.objects.get_or_create(job=c)
        if created:
            print('Job created:', obj.job)

    # create ItemType objects if not exist
    for t in ITEM_TYPES:
        obj, created = ItemType.objects.get_or_create(type=t)
        if created:
            print('ItemType created:', obj.type)

    # create ItemSubType objects if not exist
    for st, t in ITEM_SUB_TYPES:
        type, created = ItemType.objects.get_or_create(type=t)
        sub_type, created = ItemSubType.objects.get_or_create(sub_type=st, type=type)
        if created:
            print('ItemSubType created:', sub_type.sub_type)

    # create ItemRank objects if not exist
    for rank, max_star_level, emblem_rate in ITEM_RANKS:
        obj, created = ItemRank.objects.get_or_create(rank=rank, defaults={
            'max_star': max_star_level,
            'max_level': max_star_level,
            'emblem_rate': emblem_rate
        })
        if created:
            print('ItemRank created:', obj.rank)

    # create ItemStat objects if not exist
    for o in ITEM_STATS:
        obj, created = ItemStat.objects.get_or_create(stat=o)
        if created:
            print('ItemStat created:', obj.stat)


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
                    elif data['job'] == 'Dawn Warrior':
                        data.update({'sub_type': '2hSword', 'main_stat': ['PHY ATK', ]})
                    elif data['job'] == 'Wind Archer':
                        data.update({'sub_type': 'Bow', 'main_stat': ['MAG ATK', ]})
                    elif data['job'] == 'Blaze Wizard':
                        data.update({'sub_type': 'Staff', 'main_stat': ['MAG ATK', ]})
                    elif data['job'] == 'Night Walker':
                        data.update({'sub_type': 'Claw', 'main_stat': ['PHY ATK', ]})
                    elif data['job'] == 'Thunder Breaker':
                        data.update({'sub_type': 'Knuckler', 'main_stat': ['PHY ATK', ]})
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
            job = Job.objects.get(job=data['job'])
            type = ItemType.objects.get(type=data['type'])
            sub_type = ItemSubType.objects.get(sub_type=data['sub_type'])
            item_obj, created = Item.objects.get_or_create(name=data['name'], job=job, type=type, sub_type=sub_type)
            if created:
                for stat in data['main_stat']:
                    try:
                        stat_obj = ItemStat.objects.get(stat=stat)
                        item_obj.stats.add(stat_obj)
                    except ItemStat.DoesNotExist:
                        print(stat)
                print('Item created:', item_obj.name)


WEAPONS = ['Spear', 'Bow', 'Wand', 'Claw', 'Gun', '2hSword', 'Staff', 'Knuckler']
ARMORS = ['Hat', 'Outfit', 'Gloves', 'Shoes']
ACCESSORIES = ['Belt', 'Cape', 'Shoulder']
JOBS = ['Dark Knight', 'Bowmaster', 'Bishop', 'Night Lord', 'Corsair',
        'Dawn Warrior', 'Wind Archer', 'Blaze Wizard', 'Night Walker', 'Thunder Breaker']
JOB_BRANCHES = ['Warrior', 'Bowman', 'Thief', 'Mage', 'Pirate', 'All']


def stat_range():
    sub_types = WEAPONS + ARMORS + ACCESSORIES
    with open('msm_equipdata.csv', newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        datas = []
        for row in csv_reader:
            if row['sub_type'] == 'THSword':
                row['sub_type'] = '2hSword'

            if row['sub_type'] in sub_types:

                row_data = {
                    'sub_type': row['sub_type'],
                    'rank': row['rank'],
                }

                if row['type'] == 'Weapon':
                    job = row['job']
                    if job == 'DarkKnight':
                        row_data.update({'job': ['Dark Knight'], 'job_spec': True})
                    elif job == 'Thief':
                        row_data.update({'job': ['Night Lord', 'Night Walker'], 'job_spec': True})
                    elif job == 'Captain':
                        row_data.update({'job': ['Corsair'], 'job_spec': True})
                    elif job == 'Bishop':
                        row_data.update({'job': ['Bishop'], 'job_spec': True})
                    elif job == 'Bowman':
                        row_data.update({'job': ['Bowmaster', 'Wind Archer'], 'job_spec': True})
                    elif job == 'SoulMaster':
                        row_data.update({'job': ['Dawn Warrior'], 'job_spec': True})
                    elif job == 'FlameWizard':
                        row_data.update({'job': ['Blaze Wizard'], 'job_spec': True})
                    elif job == 'Striker':
                        row_data.update({'job': ['Thunder Breaker'], 'job_spec': True})
                    else:
                        print('New class:', job)
                        continue
                elif row['sub_type'] in ARMORS:
                    if row['cls'] == 'Warrior':
                        row_data.update({'job': ['Dark Knight', 'Dawn Warrior'], 'job_spec': False})
                    elif row['cls'] == 'Bowman':
                        row_data.update({'job': ['Bowmaster', 'Wind Archer'], 'job_spec': False})
                    elif row['cls'] == 'Thief':
                        row_data.update({'job': ['Night Lord', 'Night Walker'], 'job_spec': False})
                    elif row['cls'] == 'Mage':
                        row_data.update({'job': ['Bishop', 'Blaze Wizard'], 'job_spec': False})
                    elif row['cls'] == 'Pirate':
                        row_data.update({'job': ['Corsair', 'Thunder Breaker'], 'job_spec': False})

                elif row['sub_type'] in ACCESSORIES:
                    row_data.update({'job': ['All'], 'job_spec': False})

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
        jobs = Job.objects.filter(job__in=data['job'])
        if data['rank'] in ['Unique', 'Legendary', 'Mythic']:
            emblem = True
        else:
            emblem = False

        for job in jobs:
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
                    print('ItemStatRange created with stat "PHY DEF" and "MAG DEF"')

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
                    print(f'ItemStatRange created with stat "{stat.stat}"')


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
            i = Item.objects.filter(name=item_name)[0]
            obj, created = TreasureBoxGacha.objects.get_or_create(job=j, rank=r, item=i, rate=rate)
            if created:
                print(f'TreasureBoxGacha: {obj} created.')


def clear_db():
    Job.objects.all().delete()
    ItemType.objects.all().delete()
    ItemRank.objects.all().delete()
    ItemStat.objects.all().delete()
    Item.objects.all().delete()
    ItemStatRange.objects.all().delete()
    TreasureBoxGacha.objects.all().delete()


if __name__ == '__main__':
    try:
        arg = sys.argv[1]
        if arg == 'dbscript':
            dbscript()
        elif arg == 'item_db':
            item_db()
        elif arg == 'stat_range':
            stat_range()
        elif arg == 'gacha_rate':
            gacha_rate()
        elif arg == 'clear':
            clear_db()
        elif arg == 'all':
            dbscript()
            item_db()
            stat_range()
            gacha_rate()
        else:
            print('Specify whether "dbscript", "stat_range", "gacha_rate", or "item_db", or "all" to do it all. Use "clear" to clear item database.')  # noqa E501
    except IndexError:
        print('Specify whether "dbscript", "stat_range", "gacha_rate", or "item_db", or "all" to do it all. Use "clear" to clear item database.')  # noqa E501
