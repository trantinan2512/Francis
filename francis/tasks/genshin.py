import json
import re
from datetime import datetime

import bs4
import discord
from pytz import timezone

from .webspiders import WebSpider


class GenshinCrawler():
    def __init__(self, bot):
        self.bot = bot

        self.news_spider = WebSpider(self.bot, 'site_genshin')

        self.site_url = 'https://genshin.mihoyo.com/content/yuanshen/getContentList?pageSize=5&pageNum=1&channelId=10'
        self.content_url = 'https://genshin.mihoyo.com/content/yuanshen/getContent?contentId='
        self.webpage_url = 'https://genshin.mihoyo.com/en/news/detail/'
        self.newline_re = re.compile('\n{2,}')

    async def do_crawl(self):
        await self.parse_data()

    async def parse_data(self):
        checking_data = self.news_spider.form_checking_data()
        site_datas = self.fetch_news_data()

        if not site_datas or checking_data is None:
            return

        for data in site_datas:

            title = data['title']
            intro = data['intro']
            content_id = data['contentId']

            if (content_id, title) in checking_data:
                continue

            # fetch content data
            content_data = self.fetch_news_content_data(content_id)
            if not content_data:
                continue

            image_url = ''
            for ext in data['ext']:
                if ext['arrtName'] == 'banner':
                    if not ext['value']:
                        continue
                    if 'url' not in ext['value'][0]:
                        continue
                    image_url = ext['value'][0]['url']

            channel_ids = data['channelId']
            _type = ''
            _color = discord.Color.dark_teal()
            if '11' in channel_ids:
                _type = 'Info'
                _color = discord.Color.dark_blue()
            elif '12' in channel_ids:
                _type = 'Update'
                _color = discord.Color.dark_magenta()
            elif '13' in channel_ids:
                _type = 'Event'
                _color = discord.Color.dark_purple()

            intro = f'*{intro}*\n-----\n' if intro else ''

            content_html = content_data['content']
            content_text = bs4.BeautifulSoup(content_html, 'html.parser').get_text()
            content_text = content_text.replace(u'\xa0', '')
            content_text = self.newline_re.sub('\n\n', content_text)

            embed_desc = intro
            post_url = f'{self.webpage_url}{content_id}'
            for line in content_text.split('\n'):
                if len(embed_desc + f'{line}\n') > 1900:
                    embed_desc += f'...\n***[Read more]({post_url})***'
                    break
                embed_desc += f'{line}\n'

            embed = discord.Embed(
                title=title,
                description=embed_desc,
                timestamp=datetime.utcnow(),
                url=post_url,
                color=_color,
            )

            if _type:
                embed.set_footer(text=_type)

            if image_url:
                embed.set_image(url=image_url)

            posting_channel = self.bot.get_channel(id=754706712358944799)
            await posting_channel.send(embed=embed)

            now = datetime.now()
            vn_tz = now.astimezone(timezone('Asia/Ho_Chi_Minh'))
            fetched_data = {
                'id': content_id,
                'fetch_date': vn_tz.strftime('%d/%m/%Y'),
                'fetch_time': vn_tz.strftime('%H:%M:%S'),
                'title': title,
                'description': embed_desc,
                'image': image_url
            }
            # save to drive and print the result title
            self.news_spider.sheet.insert_row([value for value in fetched_data.values()], index=2)

            checking_data = self.news_spider.form_checking_data()

    def fetch_news_data(self):
        data_text = self.news_spider.get_content_by_url(self.site_url)
        if not data_text:
            return
        try:
            data = json.loads(data_text)
            return data['data']['list']
        except json.JSONDecodeError:
            return

    def fetch_news_content_data(self, content_id):
        data_text = self.news_spider.get_content_by_url(self.content_url + content_id)
        if not data_text:
            return
        try:
            data = json.loads(data_text)
            return data['data']
        except json.JSONDecodeError:
            return
