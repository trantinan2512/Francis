import re
from datetime import timedelta
from pytz import timezone
from dateparser import parse
import config

import discord
from bs4 import BeautifulSoup
from datetime import datetime
from discord.ext import tasks, commands
from .webspiders import WebSpider


class GlobalMapleStoryTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.spider = WebSpider(self.bot, 'site_gms')

        self.url = 'http://maplestory.nexon.net/news/'

        self.parse_news_datas.start()

        self.news_channel = None
        self.news_channel_id = 453565620915535872 if not config.DEBUG else 454890599410302977

    def cog_unload(self):
        self.parse_news_datas.cancel()

    @tasks.loop(seconds=config.SPIDER_DELAY)
    async def parse_news_datas(self):
        await self.parse()

    @parse_news_datas.before_loop
    async def before_parse(self):
        print('[GMS Site Spider] Waiting for ready state...')

        await self.bot.wait_until_ready()

        self.news_channel = self.bot.get_channel(id=self.news_channel_id)
        if not self.news_channel:
            print(f'Channel with ID [ {self.news_channel_id} ] not found.')
            self.parse_news_datas.cancel()
            return

        print('[GMS Site Spider] Ready and running!')

    def fetch_data(self):
        content = self.spider.get_content_by_url(self.url)

        if content is None:
            return None

        html = BeautifulSoup(content, 'html.parser')

        links = html.select('.news-container .news-item .text h3 a')
        news_texts = html.select('.news-container .news-item .text')
        descs = []
        for text in news_texts:
            descs.append(text.p)
        photos = html.select('.news-container .news-item .photo')

        # regex for finding the news ID
        news_id_re = re.compile('/news/(\d+)/')
        # regex to check if post is a maintenance post
        sc_title_re = re.compile('(scheduled|unscheduled)(.+)(maintenance|patch|update)', re.IGNORECASE)
        # regex to check if the post is an updated post
        updated_re = re.compile('\[(update|updated|complete|completed).*', re.IGNORECASE)

        datas = []
        for link, desc, photo in zip(links, descs, photos):
            news_search = news_id_re.search(link['href'])

            now = datetime.now()
            vn_tz = now.astimezone(timezone('Asia/Ho_Chi_Minh'))

            data = {
                'id': str(news_search.group(1)),
                'timestamp_date': vn_tz.strftime('%d/%m/%Y'),
                'timestamp_time': vn_tz.strftime('%H:%M:%S'),
                'title': link.get_text(),
                'link': f'http://maplestory.nexon.net{link["href"]}',
                'desc': desc.get_text(),
                'img': photo['style'].lstrip('background-image:url(').rstrip(')')
            }

            updated_search = updated_re.search(data['title'])

            if updated_search is not None:

                updated_type = updated_search.group(1).lower()

                if updated_type.startswith('complete'):
                    data['updated_type'] = '[Hoàn tất] '
                else:
                    data['updated_type'] = '[Update] '
            else:
                data['updated_type'] = ''

            # search to get type of the maintenance
            sc_search = sc_title_re.search(data['title'])

            if sc_search is not None:
                sc_catg = sc_search.group(1).lower()
                sc_type = sc_search.group(3).lower()

                if sc_catg == 'scheduled' and sc_type == 'maintenance':
                    data['sc_type'] = 'Định kỳ'
                elif sc_catg == 'unscheduled' and sc_type == 'maintenance':
                    data['sc_type'] = 'Đột xuất'
                elif sc_type == 'patch':
                    data['sc_type'] = 'Patch Game'
                elif sc_type == 'update':
                    data['sc_type'] = 'Update mới'
                else:
                    data['sc_type'] = 'Bảo trì'

            datas.append(data)

        return datas

    async def parse(self):

        checking_data = self.spider.form_checking_data()
        site_datas = self.fetch_data()

        if not site_datas or not checking_data:
            return

        for data in site_datas:

            if (data['id'], data['title']) in checking_data:
                continue

            embed = discord.Embed(
                title=data['title'],
                url=data['link'],
                description=data['desc'],
                color=discord.Color.teal())

            # parse maintenance time before posting
            sc_data = self.maintenance_post(data['link'], data['title'])

            if sc_data is not None:
                embed.title = f'{data["updated_type"]}{data["sc_type"]} - {sc_data[0]}'
                embed.description = sc_data[1]

            embed.set_image(url=data['img'])
            # send the message to channel
            await self.bot.say_as_embed(channel=self.news_channel, embed=embed)
            # save to drive and print the result title
            if not config.DEBUG:
                self.spider.sheet.insert_row([value for value in data.values()], index=2)

            print(f'Site Fetch: [GMS] [Fetched {data["title"]}]')
            checking_data = self.spider.form_checking_data()

    def maintenance_post(self, url, *args):

        # return if maintenance/patch words not in the url
        if all([maint_word not in url for maint_word in ['maintenance', 'patch', 'scheduled']]):
            return

        sc_post_content = self.spider.get_content_by_url(url)

        html = BeautifulSoup(sc_post_content, 'html.parser')

        # all these below is to get the server check duration
        ps = html.select('.article-content p')

        duration_re = re.compile('approx\w*\s*(\d+\.?\d*).*hour', re.IGNORECASE)

        # serving the sc_duration
        sc_duration = None

        for p in ps:
            duration_search = duration_re.search(p.get_text())
            if duration_search is not None:
                sc_duration = float(duration_search.group(1))

        # regex to get the string that contains UTC -7 related stuff
        utc_re = re.compile('\s*\(UTC\s*-*–*\s*(7|8)\)\s*', re.IGNORECASE)
        # regex to get the string that contains either pst or pdt
        tz_re = re.compile('p(d|s)t', re.IGNORECASE)
        # regex to get the TBD string in 'finish' duration
        tbd_re = re.compile('tbd', re.IGNORECASE)
        # regex to get the string that contains ':' with space(s)
        dt_split = re.compile(':\s+')
        # regex to get the server name in maintenance post title
        server_re = re.compile('(luna|elysium|aurora|scania|bera|reboot)', re.IGNORECASE)
        # regex to get the words inside brackets "()"
        bracket_re = re.compile('\s*\(.+\)\s*', re.IGNORECASE)

        for p in ps:
            p_text = p.get_text('\n')
            # ignore in case the time display splitted by '/'
            if tz_re.search(p_text) is None or any(c in p_text for c in ['/', '[']):
                continue

            # new way to split date and duration
            try:
                # get the first 2 lines of the p text
                date, duration = p_text.split('\n')[:2]
                # split between the first colon to get the timezone and duration
                _timezone, duration = duration.split(':', 1)
                # clean duration to just get the finish_time
                duration = duration.split('(')[0]
                # clean the timezone to get the correct timezone name
                _timezone = _timezone.split(' ', 1)[0]
            except (ValueError, IndexError):
                break

            # split duration to get start and finish
            start, finish = re.split('\s*-|–\s*', duration)
            start = bracket_re.sub('', start)
            finish = bracket_re.sub('', finish)

            # just parse the datetime_from as it present no matter what
            datetime_from = parse(
                f'{date} {_timezone} {start}',
                settings={
                    'TIMEZONE': 'America/Los_Angeles',
                    'TO_TIMEZONE': 'Asia/Ho_Chi_Minh'
                })

            # is TBD
            if tbd_re.search(finish):
                datetime_to = None
            # datetime_to can only be found when sc_duration is found AKA not TBD
            else:
                datetime_to = (datetime_from + timedelta(hours=sc_duration)) if sc_duration else None

            # search the server name
            server_search = server_re.search(args[0])
            # server name present
            server_name = server_search.group(1) if server_search else None

            # return if datetime_from not found
            if not datetime_from:
                return None

            # string serving
            day = f'{datetime_from:%d/%m/%Y}'
            frm = f'{datetime_from:%I:%M %p %d/%m/%Y}'
            to = f'{datetime_to:%I:%M %p %d/%m/%Y}' if datetime_to else '-Chưa xác định-'

            if server_name:
                title = f'Bảo trì World {server_name} ngày {day}'
            else:
                title = f'Bảo trì ngày {day}'

            if sc_duration:
                description = f'```Thời gian: {sc_duration} tiếng.\n\nGiờ VN:\n- Từ:  {frm}\n- Đến: {to}```'
            else:
                description = f'```Thời gian hoàn tất: không xác định.\n\nGiờ VN:\n- Từ:  {frm}\n- Đến: {to}```'

            return title, description


def setup(bot):
    bot.add_cog(GlobalMapleStoryTasks(bot))
