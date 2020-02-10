import json
import os
from pprint import pprint

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.config.settings')
django.setup()
import requests
from bs4 import BeautifulSoup
import re


def get_content_by_url(url):
    r = requests.get(url)

    if r.status_code == 200:
        return r.content
    else:
        return None


reg = re.compile('\s*var\s*defaultProduct\s*=\s*({.*})')


def test_func():
    site = 'https://tiki.vn'
    url = f'{site}/p48035297.html'
    html = get_content_by_url(url)
    bs = BeautifulSoup(html, 'html.parser')
    scripts = bs.find_all('script')
    data = parse_product_data(scripts)
    if not data:
        return
    pprint(data['name'])
    all_sellers = [data['current_seller']]
    if 'other_sellers' in data:
        all_sellers += data['other_sellers']
    # pprint(all_sellers)
    new_list = sorted(all_sellers, key=lambda abc: abc['price'])
    pprint(new_list)

def parse_product_data(script_tags):
    for script in script_tags:
        text = script.get_text()
        reg_result = reg.search(text)
        if reg_result:
            try:
                json_data = json.loads(reg_result.group(1))
                return json_data
            except json.JSONDecodeError:
                pass
    return None


test_func()
