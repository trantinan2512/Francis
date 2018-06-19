import asyncio
import json
# import os
# import requests
from gspread.exceptions import APIError
import facebook
import twitter
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
        self.api = twitter.Api(
            consumer_key=config.TWITTER_CONSUMER_KEY,
            consumer_secret=config.TWITTER_CONSUMER_SECRET,
            access_token_key=config.TWITTER_ACCESS_TOKEN,
            access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET,
            tweet_mode='extended')

        self.db = db.initialize_db()

    async def fetch_maplem_latest_tweet(self):

        await self.bot.wait_until_ready()

        # use this for development and production
        channel = ch.get_channel(id='455635507561627648')

        while not self.bot.is_closed:

            # fetch MapleM twitter stuff
            await self.send_latest_status(self.api, 816396540017152000, channel)

    async def fetch_maple_latest_tweet(self):

        await self.bot.wait_until_ready()

        # use this for development and production
        channel = ch.get_channel(id='455634325086404608')

        # keep executing the codes until bot is closed
        while not self.bot.is_closed:

            await self.send_latest_status(self.api, 34667202, channel)

    # send status to given channel
    async def send_latest_status(self, api, user_id, channel, delay=60):
        """Send the latest status of given user_id, to the channel
        """
        if config.DEBUG:
            delay = 10

        # fetch the user_id twitter info
        latest_status = api.GetUserTimeline(user_id=user_id, include_rts=False, exclude_replies=True)[0]

        # build the URL and save u_id and status_id for later use
        u_screen_name = latest_status.user.screen_name
        u_id = latest_status.user.id_str
        status_id = latest_status.id_str
        status_url = f'https://twitter.com/{u_screen_name}/status/{status_id}'

        try:
            # get twitter_gmsm db
            if u_id == '816396540017152000':
                db = self.db.worksheet('twitter_gmsm')
            # get twitter_gms db
            elif u_id == '34667202':
                db = self.db.worksheet('twitter_gms')
        except APIError:
            print('API ERROR')
            quit()

        posted_ids = db.col_values(1)

        if status_id in posted_ids:
            print(f'*** Twitter Fetch for {u_screen_name}: NO NEW POSTS ***')

        else:
            now = datetime.now()
            vn_tz = now.replace(tzinfo=timezone('Asia/Ho_Chi_Minh'))
            timestamp_date = vn_tz.strftime('%d/%m/%Y')
            timestamp_time = vn_tz.strftime('%H:%M:%S')

            db.insert_row([status_id, timestamp_date, timestamp_time], index=2)

            # send the message to channel
            await self.bot.send_message(channel, status_url)
            print(f'*** Twitter Fetch for {u_screen_name}: FETCHED STATUS {status_url} ***')

        await asyncio.sleep(delay)


class Facebook:
    """A cog for Facebook related tasks"""

    def __init__(self, bot):
        self.bot = bot

    async def fb(self):

        await self.bot.wait_until_ready()

        if config.DEBUG is True:
            # bot-test channel
            channel = discord.Object(id='454890599410302977')
        else:
            # twitter-facebook-gms channel
            channel = discord.Object(id='455634325086404608')

        access_token = config.FACEBOOK_ACCESS_TOKEN
        # Francis Discordpy
        user = '1195053647303141'

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

                        await self.bot.send_message_as_embed(channel, embed=embed)

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

                    await self.bot.send_message_as_embed(channel, embed=embed)

            await asyncio.sleep(40)
