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

import config


class WebSpider:
    def __init__(self, bot, util):
        self.bot = bot
        self.util = util
        self.db = util.initialize_db()

    def get_content_by_url(self, url):

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
        sc_data = None

        while not self.bot.is_closed:

            content = self.get_content_by_url('http://maplestory.nexon.net/news/')

            if content is not None:
                html = BeautifulSoup(content, 'html.parser')

                link = html.select_one('.news-container .news-item .text h3 a')
                desc = html.select_one('.news-container .news-item .text p')
                photo = html.select_one('.news-container .news-item .photo')

                news_id_re = re.compile('/news/(\d+)/')
                news_search = news_id_re.search(link['href'])

                now = datetime.now()
                vn_tz = now.replace(tzinfo=timezone('Asia/Ho_Chi_Minh'))

                data = {
                    'id': news_search.group(1),
                    'timestamp_date': vn_tz.strftime('%d/%m/%Y'),
                    'timestamp_time': vn_tz.strftime('%H:%M:%S'),
                    'title': link.get_text(),
                    'link': f'http://maplestory.nexon.net{link["href"]}',
                    'desc': desc.get_text(),
                    'img': photo['style'].lstrip('background-image:url(').rstrip(')')
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

                    # check if post is a maintenance post
                    sc_title_re = re.compile('(scheduled|unscheduled)(.+)(maintenance|patch|update)', re.IGNORECASE)
                    sc_search = sc_title_re.search(data['title'])
                    if sc_search is not None:
                        sc_catg = sc_search.group(1)
                        sc_type = sc_search.group(3)

                        if sc_catg == 'Scheduled' and sc_type == 'Maintenance':
                            sc_type = 'Định kỳ'
                        elif sc_catg == 'Unscheduled' and sc_type == 'Maintenance':
                            sc_type = 'Đột xuất'
                        elif sc_type == 'Patch':
                            sc_type = 'Patch Game'
                        elif sc_type == 'Update':
                            sc_type = 'Update mới'
                        else:
                            sc_type = 'Bảo trì'

                        # send message as a maintenance post
                        sc_data = self.maintenance_post(data['link'])

                        if sc_data is not None:
                            embed = discord.Embed(
                                title=f'[{sc_type}] {sc_data[0]}',
                                url=data['link'],
                                description=sc_data[1],
                                color=discord.Color.teal())
                            embed.set_image(url=data['img'])
                            # send the message to channel
                            await self.util.send_message_as_embed(channel=channel, embed=embed)
                            # save to drive and print the result title
                            db.insert_row([value for value in data.values()], index=2)
                            print(f'*** Site Fetch for GMS: FETCHED NEWS {data["title"]} ***')

                    else:

                        embed = discord.Embed(
                            title=data['title'],
                            url=data['link'],
                            description=data['desc'],
                            color=discord.Color.teal())
                        embed.set_image(url=data['img'])
                        # send the message to channel
                        await self.util.send_message_as_embed(channel=channel, embed=embed)
                        # save to drive and print the result title
                        db.insert_row([value for value in data.values()], index=2)
                        print(f'*** Site Fetch for GMS: FETCHED NEWS {data["title"]} ***')

            await asyncio.sleep(delay)

    def maintenance_post(self, url):

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
        # get the string that contains UTC -7 related stuff
        utc_re = re.compile('\s*\(UTC\s*-*–*\s*7\)\s*', re.IGNORECASE)
        # get the string that contains either pst or pdt
        tz_re = re.compile('p(d|s)t', re.IGNORECASE)
        # get the string that contains ':' with space(s)
        dt_split = re.compile('\:\s+')

        for strong in strongs:
            # ignore in case the time display splitted by '/'
            if tz_re.search(strong.get_text()) is not None and '/' not in strong.get_text():

                # re split between date and time (duration)
                date, duration = dt_split.split(strong.get_text())

                # re remove UTC -7 stuff if exists
                date = utc_re.sub('', date)

                # split duration to get start and finish
                start, finish = re.split('\s-|–\s*', duration)

                datetime_from = parse(
                    f'{date} {start}',
                    settings={
                        'TIMEZONE': 'America/Los_Angeles',
                        'TO_TIMEZONE': 'Asia/Ho_Chi_Minh'
                    })
                datetime_to = parse(
                    f'{date} {finish}',
                    settings={
                        'TIMEZONE': 'America/Los_Angeles',
                        'TO_TIMEZONE': 'Asia/Ho_Chi_Minh'
                    })

                if sc_duration is not None:
                    sc_duration_s = sc_duration * 60 * 60  # in seconds
                    duration = (datetime_to - datetime_from).total_seconds()
                    if sc_duration_s == duration:
                        # just pass, nothing to do here
                        print('SAME DURATION')
                    else:
                        # trust datetime_from, and go with sc_duration_s
                        datetime_to = datetime_from + timedelta(seconds=sc_duration_s)
                        print('DURATION NOT THE SAME')

                    frm = datetime_from.strftime('%I:%M %p %d/%m/%Y')
                    to = datetime_to.strftime('%I:%M %p %d/%m/%Y')
                    day = datetime_from.strftime('%d/%m/%Y')

                    # eliminate the remainder if it's equal to 0
                    sc_duration_int = int(sc_duration)
                    if (sc_duration - sc_duration_int) != 0:
                        sc_duration_str = str(sc_duration)
                    else:
                        sc_duration_str = str(sc_duration_int)

                    return f'Bảo trì ngày {day}', f'```Thời gian: {sc_duration_str} tiếng.\n\nGiờ VN:\n- Từ:  {frm}\n- Đến: {to}```'
