import asyncio
import json
import re
import requests
from bs4 import BeautifulSoup

from gspread.exceptions import APIError
from datetime import datetime, timedelta
from pytz import timezone
from dateparser import parse
import discord
from utils import db, channel as ch
import config


class WebSpider:
    def __init__(self, bot):
        self.bot = bot
        self.db = db.initialize_db()

    def get_content_by_url(self, url):

        r = requests.get(url)

        if r.status_code == 200:
            return r.content
        else:
            return None


class GMSSiteSpider(WebSpider):
    async def parse(self):

        await self.bot.wait_until_ready()
        if config.DEBUG:
            delay = 10
        else:
            delay = 60

        # cập-nhật-mới-gms channel
        channel = ch.get_channel(id='453565620915535872')
        sc_data = None

        while not self.bot.is_closed:

            content = self.get_content_by_url('http://maplestory.nexon.net/news/')

            if content is not None:
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

                read_db = True

                print('Scanning GMS site for news...')
                for link, desc, photo in zip(links, descs, photos):

                    news_search = news_id_re.search(link['href'])

                    now = datetime.now()
                    vn_tz = now.astimezone(timezone('Asia/Ho_Chi_Minh'))

                    data = {
                        'id': news_search.group(1),
                        'timestamp_date': vn_tz.strftime('%d/%m/%Y'),
                        'timestamp_time': vn_tz.strftime('%H:%M:%S'),
                        'title': link.get_text(),
                        'link': f'http://maplestory.nexon.net{link["href"]}',
                        'desc': desc.get_text(),
                        'img': photo['style'].lstrip('background-image:url(').rstrip(')')
                    }

                    if read_db is True:
                        print('[GMS site] Database read...')
                        try:
                            db = self.db.worksheet('site_gms')

                        except APIError:
                            print('API ERROR')
                            quit()

                        posted_ids = db.col_values(1)[1:]
                        posted_titles = db.col_values(4)[1:]

                    if (data['id'], data['title']) in zip(posted_ids, posted_titles):

                        print(f'Site Fetch: [GMS] [Already posted]')
                        read_db = False

                    else:

                        read_db = True

                        updated_search = updated_re.search(data['title'])

                        if updated_search is not None:

                            updated_type = updated_search.group(1).lower()

                            if updated_type.startswith('complete'):
                                updated_type = '[Hoàn tất] '
                            else:
                                updated_type = '[Update] '
                        else:
                            updated_type = ''

                        # search to get type of the maintenance
                        sc_search = sc_title_re.search(data['title'])

                        if sc_search is not None:
                            sc_catg = sc_search.group(1).lower()
                            sc_type = sc_search.group(3).lower()

                            if sc_catg == 'scheduled' and sc_type == 'maintenance':
                                sc_type = 'Định kỳ'
                            elif sc_catg == 'unscheduled' and sc_type == 'maintenance':
                                sc_type = 'Đột xuất'
                            elif sc_type == 'patch':
                                sc_type = 'Patch Game'
                            elif sc_type == 'update':
                                sc_type = 'Update mới'
                            else:
                                sc_type = 'Bảo trì'

                            # send message as a maintenance post
                            sc_data = self.maintenance_post(data['link'], data['title'])

                            if sc_data is not None:
                                embed = discord.Embed(
                                    title=f'{updated_type}{sc_type} - {sc_data[0]}',
                                    url=data['link'],
                                    description=sc_data[1],
                                    color=discord.Color.teal())
                                embed.set_image(url=data['img'])
                                # send the message to channel
                                await self.bot.send_message_as_embed(channel=channel, embed=embed)
                                # save to drive and print the result title
                                db.insert_row([value for value in data.values()], index=2)
                                print(f'Site Fetch: [GMS] [Fetched {data["title"]}]')

                        # the post is not a server maintenance post
                        else:

                            embed = discord.Embed(
                                title=data['title'],
                                url=data['link'],
                                description=data['desc'],
                                color=discord.Color.teal())
                            embed.set_image(url=data['img'])
                            # send the message to channel
                            await self.bot.send_message_as_embed(channel=channel, embed=embed)
                            # save to drive and print the result title
                            db.insert_row([value for value in data.values()], index=2)
                            print(f'Site Fetch: [GMS] [Fetched {data["title"]}]')
                print('[GMS site] Scan finished.')
            await asyncio.sleep(delay)

    def maintenance_post(self, url, *args):

        sc_post_content = self.get_content_by_url(url)

        html = BeautifulSoup(sc_post_content, 'html.parser')

        # all these below is to get the server check duration
        spans = html.select('.article-content p span')

        duration_re = re.compile('approx\w*\s*(\d+\.?\d*).*hour', re.IGNORECASE)
        sc_duration = None
        for span in spans:
            duration_search = duration_re.search(span.get_text())
            if duration_search is not None:
                sc_duration = float(duration_search.group(1))

        strongs = html.select('.article-content p span strong')
        # regex to get the string that contains UTC -7 related stuff
        utc_re = re.compile('\s*\(UTC\s*-*–*\s*7\)\s*', re.IGNORECASE)
        # regex to get the string that contains either pst or pdt
        tz_re = re.compile('p(d|s)t', re.IGNORECASE)
        # regex to get the TBD string in 'finish' duration
        tbd_re = re.compile('tbd', re.IGNORECASE)
        # regex to get the string that contains ':' with space(s)
        dt_split = re.compile('\:\s+')
        # regex to get the server name in maintenance post title
        server_re = re.compile('(luna|grazed|mybckn|khroa|windia|scania|bera|reboot)', re.IGNORECASE)
        # regex to get the words inside brackets "()"
        bracket_re = re.compile('\s*\(.+\)\s*', re.IGNORECASE)

        for strong in strongs:
            # ignore in case the time display splitted by '/'
            if tz_re.search(strong.get_text()) is not None and all(c not in strong.get_text() for c in ['/', '[']):
                # re split between date and time (duration)
                date, duration = dt_split.split(strong.get_text())

                # re remove UTC -7 stuff if exists
                date = utc_re.sub('', date)

                if len(date) <= 5:
                    for strong in strongs:
                        if all(c not in strong.get_text() for c in ['/', '[']) and parse(strong.get_text()) is not None:
                            date = f'{strong.get_text()} {date}'
                            break

                # split duration to get start and finish
                start, finish = re.split('\s*-|–\s*', duration)
                start = bracket_re.sub('', start)
                finish = bracket_re.sub('', finish)

                # search the server name
                server_search = server_re.search(args[0])

                # just parse the datetime_from as it present no matter what
                datetime_from = parse(
                    f'{date} {start}',
                    settings={
                        'TIMEZONE': 'America/Los_Angeles',
                        'TO_TIMEZONE': 'Asia/Ho_Chi_Minh'
                    })

                # if finish NOT present:
                if tbd_re.search(finish):
                    datetime_to = None

                # finish time NOT present
                else:
                    datetime_to = parse(
                        f'{date} {finish}',
                        settings={
                            'TIMEZONE': 'America/Los_Angeles',
                            'TO_TIMEZONE': 'Asia/Ho_Chi_Minh'
                        })

                # server name present
                if server_search:
                    server_name = server_search.group(1)

                # server name NOT present
                else:
                    server_name = None

                # get the string readable of datetime_to as it's present
                if datetime_to is not None:
                    # manage duration as NX staff fucks it up
                    # returns None if no duration specified
                    if sc_duration is not None:
                        sc_duration_s = sc_duration * 60 * 60  # in seconds
                        duration = (datetime_to - datetime_from).total_seconds()
                        if sc_duration_s == duration:
                            # just pass, nothing to do here
                            print('SAME DURATION')
                        else:
                            # trust datetime_from, and go with sc_duration_s
                            datetime_to = datetime_from + timedelta(seconds=sc_duration_s)
                            print('DURATION NOT THE SAME. NX STAFF FUCKED UP.')

                        # eliminate the remainder of the duration if it's equal to 0
                        sc_duration_int = int(sc_duration)
                        if (sc_duration - sc_duration_int) != 0:
                            sc_duration_str = str(sc_duration)
                        else:
                            sc_duration_str = str(sc_duration_int)
                    else:
                        sc_duration_str = None

                    to = datetime_to.strftime('%I:%M %p %d/%m/%Y')

                # oh of course these things exist all the time
                frm = datetime_from.strftime('%I:%M %p %d/%m/%Y')
                day = datetime_from.strftime('%d/%m/%Y')

                # gather things up and return title and message to the main function
                if datetime_to:
                    if sc_duration_str:
                        if server_name:
                            return (
                                f'Bảo trì World {server_name} ngày {day}',
                                f'```Thời gian: {sc_duration_str} tiếng.\n\nGiờ VN:\n- Từ:  {frm}\n- Đến: {to}```'
                            )
                        else:
                            return (
                                f'Bảo trì ngày {day}',
                                f'```Thời gian: {sc_duration_str} tiếng.\n\nGiờ VN:\n- Từ:  {frm}\n- Đến: {to}```'
                            )
                    else:
                        if server_name:
                            return (
                                f'Bảo trì World {server_name} ngày {day}',
                                f'```Giờ VN:\n- Từ:  {frm}\n- Đến: {to}```'
                            )
                        else:
                            return (
                                f'Bảo trì ngày {day}',
                                f'```Giờ VN:\n- Từ:  {frm}\n- Đến: {to}```'
                            )

                else:
                    if server_name:
                        return (
                            f'Bảo trì World {server_name} ngày {day}',
                            f'```Thời gian hoàn tất: không xác định.\n\nGiờ VN:\n- Từ:  {frm}\n- Đến: không xác định```'
                        )
                    else:
                        return (
                            f'Bảo trì ngày {day}',
                            f'```Thời gian hoàn tất: không xác định.\n\nGiờ VN:\n- Từ:  {frm}\n- Đến: không xác định```'
                        )


class GMSMSiteSpider(WebSpider):

    async def parse(self):

        await self.bot.wait_until_ready()
        if config.DEBUG:
            delay = 10
        else:
            delay = 60

        # cập-nhật-mới-gms-m channel
        channel = ch.get_channel(id='453565659637481472')

        while not self.bot.is_closed:

            site_fetches = 10

            url = 'https://m.nexon.com/notice/1?client_id=MTY3MDg3NDAy'
            content = self.get_content_by_url(url)

            if content is not None:
                html = BeautifulSoup(content, 'html.parser')

                bolt_labels = html.select('.list-group-item.pointer .bolt-label')
                news_labels = []
                for label in bolt_labels:
                    if label.get_text() != 'N':
                        news_labels.append(label)
                news_titles = html.select('.list-group-item.pointer .bolt-ellipsis')
                news_ids = html.select('.list-group-item.pointer .bolt-no-ellipsis')

                # # regex for finding the news ID
                # news_id_re = re.compile('/news/(\d+)/')
                # # regex to check if post is a maintenance post
                # sc_title_re = re.compile('(scheduled|unscheduled)(.+)(maintenance|patch|update)', re.IGNORECASE)
                # # regex to check if the post is an updated post
                # updated_re = re.compile('\[(update|updated|complete|completed).*', re.IGNORECASE)

                read_db = True

                now = datetime.now()
                vn_tz = now.astimezone(timezone('Asia/Ho_Chi_Minh'))

                print('Scanning GMSM site for news...')
                for label, title, id in zip(news_labels, news_titles, news_ids):

                    data = {
                        'id': id['data-id'],
                        'date': vn_tz.strftime('%d/%m/%Y'),
                        'time': vn_tz.strftime('%H:%M:%S'),
                        'label': label.get_text().strip(),
                        'title': title.get_text().strip()
                    }

                    if read_db is True:
                        print('[GMSM site] Database read...')
                        try:
                            site_gmsm = self.db.worksheet('site_gmsm')

                        except APIError:
                            print('API ERROR')
                            quit()

                        site_gmsm_db = site_gmsm.get_all_records()

                    posted_ids = []
                    posted_titles = []
                    for record in site_gmsm_db:
                        posted_ids.append(record['id'])
                        posted_titles.append(record['title'])

                    if (int(data['id']), data['title']) in zip(posted_ids, posted_titles):

                        print(f'Site Fetch: [GMSM] [Already posted]')
                        read_db = False

                    else:
                        news_url = f'https://m.nexon.com/notice/get/{data["id"]}?client_id=MTY3MDg3NDAy'
                        news_content = self.get_content_by_url(news_url)
                        news_html = BeautifulSoup(news_content, 'html.parser')

                        img_link = 'N/A'
                        images = news_html.select('img')
                        for image in images:
                            if 'cloudfront.net' in image['src']:
                                img_link = image['src']
                                break

                        data_contents = {
                            'link': news_url,
                            'contents': news_html.select_one('.cnts').get_text().strip().replace('\n', '---'),
                            'image': img_link
                        }
                        data.update(data_contents)
                        if data['label'].lower().startswith('e'):
                            label = 'Sự kiện'
                        else:
                            label = 'Thông báo'

                        read_db = True
                        embed = discord.Embed(
                            title=f"{label} - {data['title']}",
                            url=data['link'],
                            description=f"Cập nhật vào: {data['time']} {data['date']}",
                            color=discord.Color.teal())

                        # set image based on the availability of image in data
                        if data['image'] != 'N/A':
                            embed.set_image(url=data['image'])

                        elif data['label'].lower().startswith('e'):
                            embed.set_image(url='https://i.imgur.com/x4RoIPr.jpg')

                        else:
                            embed.set_image(url='https://i.imgur.com/DH5rVQd.jpg')

                        # send the message to channel
                        await self.bot.send_message_as_embed(channel=channel, embed=embed)
                        # save to drive and print the result title
                        site_gmsm.insert_row(list(data.values()), index=2)
                        print(f'Site Fetch: [GMS] [Fetched {data["title"]}]')

                    site_fetches -= 1
                    if site_fetches <= 0:
                        break
                print('[GMS site] Scan finished.')
            await asyncio.sleep(delay)
