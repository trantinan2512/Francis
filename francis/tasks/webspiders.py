import asyncio
# import json
import re
from datetime import datetime

import discord
import requests
from bs4 import BeautifulSoup
from gspread.exceptions import APIError
from pytz import timezone

import config
from utils import db as googledrive, channel as ch


class WebSpider:
    def __init__(self, bot, drive_sheet_name):
        self.bot = bot
        self.db = googledrive.initialize_db()
        self.sheet_name = drive_sheet_name
        self.sheet = self.db.worksheet(self.sheet_name)
        self.delay = config.SPIDER_DELAY

    @classmethod
    def get_content_by_url(cls, url):

        try:
            r = requests.get(url)
        except Exception:
            return None

        if r.status_code == 200:
            return r.content
        else:
            return None

    def form_checking_data(self):
        try:
            records = self.sheet.get_all_records()
        except APIError:
            try:
                self.db = googledrive.initialize_db()
                self.sheet = self.db.worksheet(self.sheet_name)
                records = self.sheet.get_all_records()
            except APIError:
                return None

        checking_data = [(str(record['id']), record['title']) for record in records]

        return checking_data

    def fetch_data(self):
        pass

    @property
    def fetch_dt(self):
        now = datetime.now()
        vn_tz = now.astimezone(timezone('Asia/Ho_Chi_Minh'))
        return vn_tz


class GMSMSiteSpider(WebSpider):
    def __init__(self, bot, drive_sheet_name):
        super().__init__(bot, drive_sheet_name)
        # cập-nhật-mới-gms-m channel
        self.channel = None
        self.site_fetches = 10
        self.url = 'https://m.nexon.com/notice/1?client_id=MTY3MDg3NDAy'

    def fetch_data(self):
        content = self.get_content_by_url(self.url)

        if content is None:
            return None
        html = BeautifulSoup(content, 'html.parser')

        bolt_labels = html.select('.list-group-item.pointer .bolt-label')
        news_labels = []
        for label in bolt_labels:
            if label.get_text() != 'N':
                news_labels.append(label)
        news_titles = html.select('.list-group-item.pointer .bolt-ellipsis')
        news_ids = html.select('.list-group-item.pointer .bolt-no-ellipsis')

        now = datetime.now()
        vn_tz = now.astimezone(timezone('Asia/Ho_Chi_Minh'))

        datas = []
        site_fetches = self.site_fetches
        for label, title, id in zip(news_labels, news_titles, news_ids):
            data = {
                'id': str(id['data-id']),
                'date': vn_tz.strftime('%d/%m/%Y'),
                'time': vn_tz.strftime('%H:%M:%S'),
                'label': label.get_text().strip(),
                'title': title.get_text().strip()
            }

            news_url = f'https://m.nexon.com/notice/get/{data["id"]}?client_id=MTY3MDg3NDAy'
            news_content = self.get_content_by_url(news_url)
            news_html = BeautifulSoup(news_content, 'html.parser')

            img_link = 'N/A'
            images = news_html.select('img')
            for image in images:
                if 'cloudfront.net' in image['src']:
                    img_link = image['src']
                    break

            # set image based on the availability of image in data
            is_event = data['label'].lower().startswith('e')
            if img_link == 'N/A':
                img_link = 'https://i.imgur.com/x4RoIPr.jpg' if is_event else 'https://i.imgur.com/DH5rVQd.jpg'

            label_vn = 'Sự kiện' if is_event else 'Thông báo'

            data_contents = {
                'link': news_url,
                'contents': news_html.select_one('.cnts').get_text().strip().replace('\n', '---'),
                'image': img_link,
                'label_vn': label_vn
            }
            data.update(data_contents)
            datas.append(data)

            site_fetches -= 1
            if site_fetches <= 0:
                break
        return datas

    async def parse(self):

        print('[GMSM Site Spider] Waiting for ready state...')

        await self.bot.wait_until_ready()

        print('[GMSM Site Spider] Ready and running!')
        self.channel = ch.get_channel(bot=self.bot, id=453565659637481472)

        while not self.bot.is_closed():

            # await asyncio.sleep(self.delay)
            checking_data = self.form_checking_data()
            site_datas = self.fetch_data()

            if not site_datas or not checking_data:
                await asyncio.sleep(self.delay)
                continue

            for data in site_datas:

                if (data['id'], data['title']) in checking_data:
                    continue

                embed = discord.Embed(
                    title=f"{data['label_vn']} - {data['title']}",
                    url=data['link'],
                    description=f"Cập nhật vào: {data['time']} {data['date']}",
                    color=discord.Color.teal())
                try:
                    # send the message to channel
                    await self.bot.say_as_embed(channel=self.channel, embed=embed)
                    # save to drive and print the result title
                    self.sheet.insert_row(list(data.values()), index=2)
                except Exception:
                    return

                print(f'Site Fetch: [GMSM] [Fetched {data["title"]}]')
                # updates the checking data
                checking_data = self.form_checking_data()

            await asyncio.sleep(self.delay)


class GMS2SiteSpider(WebSpider):
    def __init__(self, bot, drive_sheet_name):
        super().__init__(bot, drive_sheet_name)
        # cập-nhật-mới-gms2 channel
        self.channel = None
        self.url = 'http://maplestory2.nexon.net/en/news'

    def fetch_data(self):
        content = self.get_content_by_url(self.url)

        if content is None:
            return None

        html = BeautifulSoup(content, 'html.parser')

        # regex for finding the news ID
        news_id_re = re.compile('/news/article/(\d+)/')
        now = datetime.now()
        vn_tz = now.astimezone(timezone('Asia/Ho_Chi_Minh'))

        news_items = html.select('.news-item')

        datas = []
        for news in news_items:
            link = news.select_one('.news-item-link')['href']
            image = news.select_one('.news-item-image')['style']
            news_category = news.select_one('.news-category-tag').get_text()
            title = news.select_one('h2').get_text()
            short_post_text = news.select_one('.short-post-text').get_text()

            post_id = news_id_re.search(link).group(1)

            data = {
                'id': str(post_id),
                'fetch_date': vn_tz.strftime('%d/%m/%Y'),
                'fetch_time': vn_tz.strftime('%H:%M:%S'),
                'category': news_category,
                'title': title,
                'link': f'http://maplestory2.nexon.net{link}',
                'description': short_post_text,
                'image': image.lstrip("background-image:url('").rstrip("')")
            }
            datas.append(data)
        return datas

    async def parse(self):

        print('[GMS2 Site Spider] Waiting for ready state...')

        await self.bot.wait_until_ready()

        print('[GMS2 Site Spider] Ready and running!')

        self.channel = ch.get_channel(bot=self.bot, id=505584303154135040)

        while not self.bot.is_closed():

            # await asyncio.sleep(self.delay)

            checking_data = self.form_checking_data()
            site_datas = self.fetch_data()

            if not site_datas or not checking_data:
                await asyncio.sleep(self.delay)
                continue

            for data in site_datas:

                if (data['id'], data['title']) in checking_data:
                    continue

                embed = discord.Embed(
                    title=f"[{data['category']}] {data['title']}",
                    url=data['link'],
                    description=data['description'],
                    color=discord.Color.teal())
                embed.set_image(url=data['image'])

                try:
                    # send the message to channel
                    await self.bot.say_as_embed(channel=self.channel, embed=embed)

                    # save to drive and print the result title
                    self.sheet.insert_row([value for value in data.values()], index=2)
                except Exception:
                    continue

                print(f'Site Fetch: [GMS2] [Fetched {data["title"]}]')

                # updates the checking data
                checking_data = self.form_checking_data()

            await asyncio.sleep(self.delay)
