import asyncio
import json
import re
import requests
from bs4 import BeautifulSoup

from gspread.exceptions import APIError
from datetime import datetime
from pytz import timezone

import discord

import config


class WebSpider:
    def __init__(self, bot, util):
        self.bot = bot
        self.util = util
        self.db = util.initialize_db()

    async def get_news_gms_site(self):

        url = 'http://maplestory.nexon.net/news/'

        r = requests.get(url)

        if r.status_code == 200:
            return r.content
        else:
            return None

    async def parse(self):

        await self.bot.wait_until_ready()
        if config.DEBUG:
            delay = 10
        else:
            delay = 60

        # cập-nhật-mới-gms channel
        channel = self.util.get_channel(id='453565620915535872')

        while not self.bot.is_closed:

            content = await self.get_news_gms_site()

            if content is not None:
                html = BeautifulSoup(content, 'html.parser')

                link = html.select_one('.news-container .news-item .text h3 a')
                desc = html.select_one('.news-container .news-item .text p')
                photo = html.select_one('.news-container .news-item .photo')

                news_id_re = re.compile('(/news/)(\d+)(/)')
                news_search = news_id_re.search(link['href'])

                now = datetime.now()
                vn_tz = now.replace(tzinfo=timezone('Asia/Ho_Chi_Minh'))
                timestamp_date = vn_tz.strftime('%d/%m/%Y')
                timestamp_time = vn_tz.strftime('%H:%M:%S')

                data = {
                    'id': news_search.group(2),
                    'date': timestamp_date,
                    'time': timestamp_time,
                    'title': link.get_text(),
                    'link': f'http://maplestory.nexon.net{link["href"]}',
                    'description': desc.get_text(),
                    'photo_url': photo['style'].lstrip('background-image:url(').rstrip(')')
                }

                try:
                    db = self.db.worksheet('site_gms')

                except APIError:
                    print('API ERROR')
                    quit()

                posted_ids = db.col_values(1)

                if data['id'] in posted_ids:
                    print(f'*** Site Fetch for GMS: NO NEW POSTS ***')

                else:
                    db.insert_row([value for value in data.values()], index=2)

                    embed = discord.Embed(
                        title=data['title'],
                        url=data['link'],
                        description=data['description'],
                        color=discord.Color.teal())
                    embed.set_image(url=data['photo_url'])
                    # send the message to channel
                    await self.util.send_message_as_embed(channel=channel, embed=embed)
                    print(f'*** Site Fetch for GMS: FETCHED NEWS {data["title"]} ***')

            await asyncio.sleep(delay)
