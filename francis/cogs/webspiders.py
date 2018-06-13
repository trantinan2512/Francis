import asyncio
import json

import requests
from bs4 import BeautifulSoup

import discord

import config


class WebSpider:
    def __init__(self, bot, util):
        self.bot = bot
        self.util = util

    async def get_news_gms_site(self):

        url = 'http://maplestory.nexon.net/news/'

        r = requests.get(url)

        if r.status_code == 200:
            return r.content
        else:
            return None

    async def parse(self):

        await self.bot.wait_until_ready()

        # cập-nhật-mới-gms channel
        channel = self.get_channel(id='453565620915535872')

        while not self.bot.is_closed:

            content = await self.get_news_gms_site()

            if content is not None:
                html = BeautifulSoup(content, 'html.parser')

                links = html.select('.news-container .news-item .text h3 a')
                descriptions = html.select('.news-container .news-item .text p')
                photos = html.select('.news-container .news-item .photo')

                post_titles = []
                post_descs = []
                post_hrefs = []
                post_photo_urls = []

                for link in links:
                    post_titles.append(link.get_text())
                    post_hrefs.append(link['href'])

                for desc in descriptions:

                    if not desc.has_attr('class'):
                        post_descs.append(desc.get_text())

                for photo in photos:
                    photo_url = photo['style'].lstrip('background-image:url(').rstrip(')')
                    post_photo_urls.append(photo_url)

                post_datas = []
                for item in zip(post_titles, post_descs, post_hrefs, post_photo_urls):
                    d = {
                        'title': item[0],
                        'description': item[1],
                        'link': f'http://maplestory.nexon.net{item[2]}',
                        'photo_url': item[3]
                    }
                    post_datas.append(d)

                news_cache_file = config.BASE_DIR + '/cache/news_gms_cache.json'
                with open(news_cache_file, 'r') as infile:
                    file_data = json.load(infile)
                    # pass if no new data found
                    if file_data == post_datas:
                        print('*** NO NEW DATA COLLECTED ***')
                    # rewrite the file with new data
                    else:
                        with open(news_cache_file, 'w') as outfile:
                            json.dump(post_datas, outfile)

                        latest_post = post_datas[0]
                        embed = discord.Embed(
                            title=latest_post['title'],
                            url=latest_post['link'],
                            description=latest_post['description'],
                            color=discord.Color.teal())
                        embed.set_image(url=latest_post['photo_url'])

                        await self.util.send_message_as_embed(channel=channel, embed=embed)

            await asyncio.sleep(30)

    def get_channel(self, id):
        """Return the given channel Object if in Production,
        #bot-test channel if in Development
        """
        if config.DEBUG is True:
            # bot-test channel
            channel = discord.Object(id='454890599410302977')
        else:
            # id-given channel
            channel = discord.Object(id=id)
        return channel