import asyncio
import traceback
# import json
import re
import requests
from bs4 import BeautifulSoup

from gspread.exceptions import APIError
from datetime import datetime, timedelta
from pytz import timezone
from dateparser import parse
import discord
from utils import db as googledrive, channel as ch
import config


class WebSpider:
    def __init__(self, bot, drive_sheet_name):
        self.bot = bot
        self.db = googledrive.initialize_db()
        self.sheet_name = drive_sheet_name
        self.sheet = self.db.worksheet(self.sheet_name)
        self.delay = config.SPIDER_DELAY

    def get_content_by_url(self, url):

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


class GMSSiteSpider(WebSpider):
    def __init__(self, bot, drive_sheet_name):
        super().__init__(bot, drive_sheet_name)
        self.url = 'http://maplestory.nexon.net/news/'
        self.channel = None

    def fetch_data(self):
        content = self.get_content_by_url(self.url)

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

        print('[GMS Site Spider] Waiting for ready state...')

        await self.bot.wait_until_ready()

        print('[GMS Site Spider] Ready and running!')

        # cập-nhật-mới-gms channel
        self.channel = ch.get_channel(bot=self.bot, id=453565620915535872)

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
                await self.bot.say_as_embed(channel=self.channel, embed=embed)
                # save to drive and print the result title
                self.sheet.insert_row([value for value in data.values()], index=2)

                print(f'Site Fetch: [GMS] [Fetched {data["title"]}]')
                checking_data = self.form_checking_data()

            await asyncio.sleep(self.delay)

    def maintenance_post(self, url, *args):

        sc_post_content = self.get_content_by_url(url)

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

                # send the message to channel
                await self.bot.say_as_embed(channel=self.channel, embed=embed)
                # save to drive and print the result title
                self.sheet.insert_row(list(data.values()), index=2)

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

                # send the message to channel
                await self.bot.say_as_embed(channel=self.channel, embed=embed)

                # save to drive and print the result title
                self.sheet.insert_row([value for value in data.values()], index=2)

                print(f'Site Fetch: [GMS2] [Fetched {data["title"]}]')

                # updates the checking data
                checking_data = self.form_checking_data()

            await asyncio.sleep(self.delay)


class HonkaiImpactSpider(WebSpider):
    def __init__(self, bot, drive_sheet_name):
        super().__init__(bot, drive_sheet_name)
        self.channel = None
        self.post_id_regex = re.compile('news/(\d+)\?')
        self.base_url = 'https://honkaiimpact3.mihoyo.com'
        self.url = f'{self.base_url}/global/en-us/news'

    def fetch_data(self):
        content = self.get_content_by_url(self.url)

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
            post_html_content = self.get_content_by_url(f'{post_url}')
            if not post_html_content:
                image = news.select_one('img')['src']
                short_post_text = news.select_one('.news-intro').get_text()
            else:
                html = BeautifulSoup(post_html_content, 'html.parser')
                image = html.select_one('.news-detail__banner img')['src']

                content = html.select_one('.news-detail__article').get_text()

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

    async def parse(self):

        print('[Honkai Impact Global Site Spider] Waiting for ready state...')

        await self.bot.wait_until_ready()

        print('[Honkai Impact Global Site Spider] Ready and running!')

        self.channel = self.bot.get_channel(559210580146126848)

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

                embed_desc = ''
                for line in data['description'].split('\n'):
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

                # send the message to channel
                await self.bot.say_as_embed(channel=self.channel, embed=embed)

                # save to drive and print the result title
                self.sheet.insert_row([value for value in data.values()], index=2)
                print(f'Site Fetch: [HI3] [Fetched {data["title"]}]')

                # updates the checking data
                checking_data = self.form_checking_data()

            await asyncio.sleep(self.delay)
