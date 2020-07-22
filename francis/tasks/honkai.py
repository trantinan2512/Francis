from datetime import datetime

import discord
from bs4 import BeautifulSoup
from discord.ext import tasks, commands

from .webspiders import WebSpider


class HonkaiTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.supplies_spider = WebSpider(self.bot, 'gamepedia_hi3_supplies')
        self.events_spider = WebSpider(self.bot, 'gamepedia_hi3_events')

        self.site = 'https://honkaiimpact3.gamepedia.com'

        self.supplies_url = f'{self.site}/Supply/Supplies'
        self.events_url = f'{self.site}/Events'

        self.supplies_ignored_tabs = ['2018', '2019', '2020']

        self.parse_supplies_data.start()
        self.parse_events_data.start()

        # self.supplies_channel_id = 587165325464829953
        # self.events_channel_id = 559210580146126848

    def cog_unload(self):
        self.parse_supplies_data.cancel()
        self.parse_events_data.cancel()

    @tasks.loop(seconds=60.0)
    async def parse_supplies_data(self):
        await self.parse_data(
            spider=self.supplies_spider,
            fetcher=self.fetch_supplies_data,
            posting_channel=self.bot.get_channel(id=587165325464829953)
        )

    @tasks.loop(seconds=60.0)
    async def parse_events_data(self):
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
                }
                if 'src' in a.img:
                    image = a.img['src']
                    data.update({'image': image})
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
                }
                if 'src' in a.img:
                    image = a.img['src']
                    data.update({'image': image})

                datas.append(data)

        return datas

    @parse_supplies_data.before_loop
    async def before_parse(self):
        print('[HI3rd Gamepedia Site Spider] Waiting for ready state...')

        await self.bot.wait_until_ready()

        print('[Hi3rd Gamepedia Site Spider] Ready and running!')


def setup(bot):
    bot.add_cog(HonkaiTasks(bot))
