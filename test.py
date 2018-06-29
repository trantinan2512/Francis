import json
import requests
from bs4 import BeautifulSoup
import re
import dateparser
from pytz import timezone
from datetime import timedelta, datetime
from config import BASE_DIR
import config
import tweepy
from pprint import pprint
from utils.db import initialize_db


def get_content_by_url(url):

    r = requests.get(url)

    if r.status_code == 200:
        return r.content
    else:
        return None


def testing(arg1, *args):
    print(arg1)
    print(args[0])


def test_func():
    tl = ['a' , 'b']
    text = 'a sdlfkj wenrwb'
    print(any(i in text for i in tl))


def test_web_crawl():

    content = get_content_by_url('http://maplestory.nexon.net/news/all/6')
    if content is not None:
        html = BeautifulSoup(content, 'html.parser')

        links = html.select('.news-container .news-item .text h3 a')

        for link in links:
            sc_title_re = re.compile('(scheduled|unscheduled)(.+)(maintenance|patch|update)', re.IGNORECASE)
            sc_search = sc_title_re.search(link.get_text())

            if sc_search is not None:
                print(sc_search.group(3))
                # print(link['href'])
                sc_post_url = f'http://maplestory.nexon.net{link["href"]}'

                sc_post_content = get_content_by_url(sc_post_url)

                html = BeautifulSoup(sc_post_content, 'html.parser')

                # all these below is to get the server check duration
                spans = html.select('.article-content p span')
                duration_re = re.compile('approx\w*\s*(\d+\.?\d*).*hour', re.IGNORECASE)
                sc_duration = None
                for span in spans:
                    duration_search = duration_re.search(span.get_text())
                    if duration_search is not None:
                        sc_duration = float(duration_search.group(1))

                # get the string that contains UTC -7
                strongs = html.select('.article-content p span strong')
                utc_re = re.compile('\s*\(UTC\s*-*–*\s*7\)\s*', re.IGNORECASE)
                dt_split = re.compile('\:\s+')
                tz_re = re.compile('p(d|s)t', re.IGNORECASE)
                for strong in strongs:

                    if tz_re.search(strong.get_text()) is not None and '/' not in strong.get_text():
                        date, duration = dt_split.split(strong.get_text())

                        date = utc_re.sub('', date)

                        tfrom, tto = re.split('\s-|–\s*', duration)

                        datetime_from = dateparser.parse(
                            f'{date} {tfrom}',
                            settings={
                                'TIMEZONE': 'America/Los_Angeles',
                                'TO_TIMEZONE': 'Asia/Ho_Chi_Minh'
                            })
                        datetime_to = dateparser.parse(
                            f'{date} {tto}',
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
                            sc_duration_int = int(sc_duration)
                            if (sc_duration - sc_duration_int) != 0:
                                sc_duration_str = str(sc_duration)
                            else:
                                sc_duration_str = str(sc_duration_int)
                            print(f'Bảo trì {sc_duration_str} tiếng.\nTừ:  {frm}\nĐến: {to}')
                        else:
                            quit()


if __name__ == "__main__":
    test_func()
