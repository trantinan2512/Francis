import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.config.settings')
django.setup()
import json
import requests
from bs4 import BeautifulSoup
import re
import dateparser
from pytz import timezone as tz
from datetime import timedelta, datetime, date
from config import BASE_DIR
import config
import tweepy
from pprint import pprint
from utils.db import initialize_db
from pprint import pprint
import csv
from web.apps.items.models import Item, ItemStatRange
from web.apps.gachas.models import TreasureBoxGacha
from web.apps.users.models import DiscordUser
from random import choices, uniform


def get_content_by_url(url):
    r = requests.get(url)

    if r.status_code == 200:
        return r.content
    else:
        return None


def test_func():
    site = 'https://honkaiimpact3.gamepedia.com'
    url = f'{site}/Supply/Supplies'
    html = get_content_by_url(url)
    bs = BeautifulSoup(html, 'html.parser')
    ignored_tabs = ['2018', '2019']
    tabs = bs.select('.tabbertab')
    for tab in tabs:
        if tab['title'] in ignored_tabs:
            continue
        print(tab['title'])
        for a in tab.select('a')[:3]:
            print(a['href'])
            print(a.img['src'])
            print(a.find_next('b').next_sibling)


if __name__ == "__main__":
    test_func()
