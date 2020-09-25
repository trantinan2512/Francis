import re
from datetime import datetime

import discord
from bs4 import BeautifulSoup
from pytz import timezone

from .webspiders import WebSpider


class HonkaiWikiCrawler():
    def __init__(self, bot):
        self.bot = bot

        self.supplies_spider = WebSpider(self.bot, 'gamepedia_hi3_supplies')
        self.events_spider = WebSpider(self.bot, 'gamepedia_hi3_events')

        self.site = 'https://honkaiimpact3.gamepedia.com'

        self.supplies_url = f'{self.site}/Supply/Supplies'
        self.events_url = f'{self.site}/Events'

        self.supplies_ignored_tabs = ['2018', '2019', '2020']

    async def do_crawl(self):

        # supplies crawler
        await self.parse_data(
            spider=self.supplies_spider,
            fetcher=self.fetch_supplies_data,
            posting_channel=self.bot.get_channel(id=587165325464829953)
        )
        # events crawler
        await self.parse_data(
            spider=self.events_spider,
            fetcher=self.fetch_events_data,
            posting_channel=self.bot.get_channel(id=559210580146126848)
        )

    async def parse_data(self, spider, fetcher, posting_channel):
        checking_data = spider.form_checking_data()
        site_datas = fetcher()

        if not site_datas or checking_data is None:
            return

        for data in site_datas:

            if (data['id'], data['title']) in checking_data:
                continue

            if data['type'] == 'Expansion':
                color = discord.Color.dark_blue()
            elif data['type'] == 'Focused':
                color = discord.Color.dark_magenta()
            elif data['type'] == 'Event':
                color = discord.Color.dark_purple()
            else:
                color = discord.Color.dark_teal()

            title = f"{data['type']} Supplies" if data['type'] in ['Expansion', 'Focused', 'Event'] else ''

            embed = discord.Embed(
                title=title,
                description=
                f"**{data['title']}**\n\n"
                f"Duration:```\n"
                f"• Start: {data['start']}\n"
                f"• End  : {data['end']}"
                f"```",
                timestamp=datetime.utcnow(),
                color=color,
            )

            embed.set_author(
                name='Read Details on HI3rd Gamepedia',
                url=data['url'],
                icon_url='https://i.imgur.com/WED88Fn.png',
            )

            if data['image']:
                embed.set_image(url=data['image'])

            await posting_channel.send(embed=embed)

            # save to drive and print the result title
            spider.sheet.insert_row([value for value in data.values()], index=2)

            checking_data = spider.form_checking_data()

    def fetch_supplies_data(self):
        html = self.supplies_spider.get_content_by_url(self.supplies_url)
        if not html:
            return

        bs = BeautifulSoup(html, 'html.parser')

        tabs = bs.select('.tabbertab')

        datas = []
        for tab in tabs:

            if tab['title'] in self.supplies_ignored_tabs:
                continue

            type = tab['title']

            for a in tab.select('a'):
                url = f"{self.site}{a['href']}"
                title = a['title']
                image = a.img['src'] if a.img else None
                start, end = a.find_next('b').next_sibling.split('~', 1)
                fetch_dt = self.supplies_spider.fetch_dt
                data = {
                    'type': type,
                    'fetch_date': f'{fetch_dt:%d/%m/%Y}',
                    'fetch_time': f'{fetch_dt:%H:%M:%S}',
                    'id': f'{type}{title}{start}',
                    'title': title,
                    'url': url,
                    'start': start,
                    'end': end,
                    'image': image,
                }
                datas.append(data)

        return datas

    def fetch_events_data(self):
        html = self.events_spider.get_content_by_url(self.events_url)
        if not html:
            return

        bs = BeautifulSoup(html, 'html.parser')

        tabs = bs.select('.tabbertab')

        datas = []
        for tab in tabs:

            type = tab['title']

            for a in tab.select('a'):
                url = f"{self.site}{a['href']}"
                title = a['title']
                image = a.img['src'] if a.img else None
                start, end = a.find_next('b').next_sibling.split('~', 1)
                fetch_dt = self.supplies_spider.fetch_dt
                data = {
                    'type': type,
                    'fetch_date': f'{fetch_dt:%d/%m/%Y}',
                    'fetch_time': f'{fetch_dt:%H:%M:%S}',
                    'id': f'{type}{title}{start}',
                    'title': title,
                    'url': url,
                    'start': start,
                    'end': end,
                    'image': image,
                }

                datas.append(data)

        return datas


class HonkaiWebCrawler():
    def __init__(self, bot):
        self.bot = bot
        self.web_spider = WebSpider(self.bot, 'site_hi3')
        self.channel = None
        self.post_id_regex = re.compile('news/(\d+)\?')
        self.newline_re = re.compile('\n{2,}')

        self.base_url = 'https://honkaiimpact3.mihoyo.com'
        self.url = f'{self.base_url}/global/en-us/news'

    async def do_crawl(self):
        await self.parse_data()

    def fetch_data(self):
        content = self.web_spider.get_content_by_url(self.url)

        if content is None:
            return None

        now = datetime.now()
        vn_tz = now.astimezone(timezone('Asia/Ho_Chi_Minh'))

        html = BeautifulSoup(content, 'html.parser')
        news_items = html.select_one('.news-wrap')

        datas = []
        for news in news_items.find_all('a'):
            post_url = news["href"]
            post_id = self.post_id_regex.search(post_url).group(1)
            post_url = f'{self.url}/{post_id}'
            # getting the image inside the post for better quality
            post_html_content = self.web_spider.get_content_by_url(f'{post_url}')
            image = news.select_one('img')['src']
            if post_html_content:
                html = BeautifulSoup(post_html_content, 'html.parser')
                _image = html.select_one('.news-detail__banner img')
                if _image:
                    image = _image['src']
                content = html.select_one('.news-detail__article').get_text()
            else:
                content = ''

            title = news.select_one('.title').get_text().strip()

            data = {
                'id': post_id,
                'fetch_date': vn_tz.strftime('%d/%m/%Y'),
                'fetch_time': vn_tz.strftime('%H:%M:%S'),
                'title': title,
                'link': post_url,
                'description': content,
                'image': image
            }
            datas.append(data)
        return datas

    async def parse_data(self):

        self.channel = self.bot.get_channel(559210580146126848)

        checking_data = self.web_spider.form_checking_data()
        site_datas = self.fetch_data()

        if not site_datas or not checking_data:
            return

        for data in site_datas:

            if (data['id'], data['title']) in checking_data:
                continue

            content_text = data['description']
            content_text = content_text.replace(u'\xa0', '')
            content_text = self.newline_re.sub('\n\n', content_text)
            embed_desc = ''
            for line in content_text.split('\n'):
                if len(embed_desc + f'{line}\n') > 1900:
                    embed_desc += f'...\n***[Read more]({data["link"]})***'
                    break
                embed_desc += f'{line}\n'

            # sending news message to channel
            embed = discord.Embed(
                title=f"{data['title']}",
                url=data['link'],
                description=embed_desc,
                color=discord.Color.teal())
            embed.set_image(url=data['image'])

            try:
                # send the message to channel
                await self.bot.say_as_embed(channel=self.channel, embed=embed)

                # save to drive and print the result title
                self.web_spider.sheet.insert_row([value for value in data.values()], index=2)
            except Exception:
                continue

            print(f'Site Fetch: [HI3] [Fetched {data["title"]}]')
            # updates the checking data
            checking_data = self.web_spider.form_checking_data()
