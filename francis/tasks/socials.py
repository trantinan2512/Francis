import asyncio
import json
# import os
# import requests
from gspread.exceptions import APIError
import facebook
import tweepy
import discord
# from discord.ext import commands

from datetime import datetime
from pytz import timezone

from utils import db, channel as ch
# from pprint import pprint
import config


class Twitter:
    """A cog for Twitter related tasks"""

    def __init__(self, bot):
        self.bot = bot
        auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET)
        auth.set_access_token(config.TWITTER_ACCESS_TOKEN, config.TWITTER_ACCESS_TOKEN_SECRET)

        self.api = tweepy.API(auth, wait_on_rate_limit=True)

        self.db = db.initialize_db()

    async def fetch_maplem_latest_tweet(self):

        print('[GMSM Tweet Fetcher] Waiting for ready state...')

        await self.bot.wait_until_ready()

        print('[GMSM Tweet Fetcher] Ready and running!')

        # use this for development and production
        channel = ch.get_channel(bot=self.bot, id=455635507561627648)

        while not self.bot.is_closed():

            # fetch MapleM twitter stuff
            await self.send_latest_status(self.api, 816396540017152000, channel)

    async def fetch_maple_latest_tweet(self):

        print('[GMS Tweet Fetcher] Waiting for ready state...')

        await self.bot.wait_until_ready()

        print('[GMS Tweet Fetcher] Ready and running!')

        # use this for development and production
        channel = ch.get_channel(bot=self.bot, id=455634325086404608)

        # keep executing the codes until bot is closed
        while not self.bot.is_closed():

            await self.send_latest_status(self.api, 34667202, channel)

    async def fetch_maple2_latest_tweet(self):

        print('[GMS2 Tweet Fetcher] Waiting for ready state...')

        await self.bot.wait_until_ready()

        print('[GMS2 Tweet Fetcher] Ready and running!')

        # use this for development and production
        channel = ch.get_channel(bot=self.bot, id=505584446074781697)

        # keep executing the codes until bot is closed
        while not self.bot.is_closed():

            await self.send_latest_status(self.api, 851835989702000640, channel)

    # send status to given channel
    async def send_latest_status(self, api, user_id, channel, delay=60):
        """Send the latest status of given user_id, to the channel
        """

        if config.DEBUG:
            delay = 10

        await asyncio.sleep(delay)

        # fetch the user_id twitter info
        tweet_count = 5
        latest_tweets = api.user_timeline(user_id, count=tweet_count)
        read_db = True
        # print(f'Scanning {tweet_count} tweets from USER_ID: {user_id} ...')
        for tweet in latest_tweets:

            # build these things for later use
            u_screen_name = tweet.user.screen_name
            u_id = tweet.user.id_str
            status_id = tweet.id_str

            # not retweet, not reply
            if not tweet.text.startswith('RT @') and not tweet.in_reply_to_user_id:
                proceed = True
            # reply to self
            elif user_id == tweet.in_reply_to_user_id:
                proceed = True
            else:
                proceed = False

            if proceed is True:
                # build the URL and save u_id and status_id for later use
                status_url = f'https://twitter.com/{u_screen_name}/status/{status_id}'

                if read_db is True:
                    try:
                        # get twitter_gmsm db
                        if u_id == '816396540017152000':
                            db = self.db.worksheet('twitter_gmsm')
                        # get twitter_gms db
                        elif u_id == '34667202':
                            db = self.db.worksheet('twitter_gms')
                        # get twitter_gms db
                        elif u_id == '851835989702000640':
                            db = self.db.worksheet('twitter_gms2')

                    except APIError:
                        print('API ERROR')
                        break

                    posted_ids = db.col_values(1)
                    # print('Database read')

                if status_id in posted_ids:
                    read_db = False
                    # print(f'Twitter Fetch: [{u_screen_name}] [Already posted]')

                else:
                    read_db = True
                    now = datetime.now()
                    vn_tz = now.replace(tzinfo=timezone('Asia/Ho_Chi_Minh'))
                    timestamp_date = vn_tz.strftime('%d/%m/%Y')
                    timestamp_time = vn_tz.strftime('%H:%M:%S')

                    db.insert_row([status_id, timestamp_date, timestamp_time], index=2)

                    # send the message to channel
                    await channel.send(status_url)
                    print(f'Twitter Fetch: [{u_screen_name}] [Fetched: {status_url}]')
            # else:

            #     print(f'Twitter Fetch: [{u_screen_name}] [NOT a tweet or self reply]')
        # print('Tweets scan finished.')


class Facebook:
    """A cog for Facebook related tasks"""

    def __init__(self, bot):
        self.bot = bot

    async def fb(self):

        await self.bot.wait_until_ready()

        if config.DEBUG is True:
            # bot-test channel
            channel = discord.Object(id=454890599410302977)
        else:
            # twitter-facebook-gms channel
            channel = discord.Object(id=455634325086404608)

        access_token = config.FACEBOOK_ACCESS_TOKEN
        # Francis Discordpy
        user = 1195053647303141

        graph = facebook.GraphAPI(access_token)
        profile = graph.get_object(user)

        while not self.bot.is_closed:

            posts = graph.get_connections(profile['id'], 'posts')

            latest_post = posts['data'][0]

            embed = discord.Embed(
                title=profile['name'],
                description=latest_post['message'],
                color=discord.Color.teal())

            FACEBOOK_CACHE_DIR = config.BASE_DIR + '/cache/facebook_cache.json'

            with open(FACEBOOK_CACHE_DIR, 'r') as infile:

                fb_cache = json.load(infile)
                maple = fb_cache.get('Maple')

                if maple is not None and maple.get('ids'):
                    cached_maple_ids = maple['ids']

                    if latest_post['id'] in cached_maple_ids:
                        print('*** FACEBOOK FETCH: NO NEW POSTS ***')

                    else:
                        with open(FACEBOOK_CACHE_DIR, 'w') as outfile:
                            fb_cache['Maple']['ids'].prepend(latest_post['id'])
                            json.dump(fb_cache, outfile)

                        # try to retrieve the picture url and add it as image embed if there is
                        post_pic = graph.get_object(id=latest_post['id'], fields='full_picture')
                        pic_url = post_pic.get('full_picture')
                        if pic_url is not None:
                            embed.set_image(url=post_pic['full_picture'])

                        await self.bot.say_as_embed(channel, embed=embed)

                else:
                    data = {'Maple': {'ids': [latest_post['id'], ]}}
                    fb_cache.update(data)
                    with open(FACEBOOK_CACHE_DIR, 'w') as outfile:
                        json.dump(fb_cache, outfile)

                    # Uhh... repeated to avoid an extra call to the API every 10 sec...
                    post_pic = graph.get_object(id=latest_post['id'], fields='full_picture')
                    pic_url = post_pic.get('full_picture')
                    if pic_url is not None:
                        embed.set_image(url=post_pic['full_picture'])

                    await self.bot.say_as_embed(channel, embed=embed)

            await asyncio.sleep(40)
