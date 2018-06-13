import asyncio
import json
# import os
# import requests

import facebook
import twitter
import discord
# from discord.ext import commands

from pprint import pprint
import config


class Twitter:
    """A cog for Twitter related tasks"""

    def __init__(self, bot, util):
        self.bot = bot
        self.util = util
        self.api = twitter.Api(
            consumer_key=config.TWITTER_CONSUMER_KEY,
            consumer_secret=config.TWITTER_CONSUMER_SECRET,
            access_token_key=config.TWITTER_ACCESS_TOKEN,
            access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET,
            tweet_mode='extended')

    async def fetch_maplem_latest_tweet(self):

        await self.bot.wait_until_ready()

        # use this for development and production
        channel = self.get_channel(id='455635507561627648')

        while not self.bot.is_closed:

            # fetch MapleM twitter stuff
            await self.send_latest_status(self.api, 816396540017152000, channel)

    async def fetch_maple_latest_tweet(self):

        await self.bot.wait_until_ready()

        # use this for development and production
        channel = self.get_channel(id='455634325086404608')

        # keep executing the codes until bot is closed
        while not self.bot.is_closed:

            await self.send_latest_status(self.api, 34667202, channel)

    # send status to given channel
    async def send_latest_status(self, api, user_id, channel, delay=60):
        """Send the latest status of given user_id, to the channel
        """
        # fetch the user_id twitter info
        latest_status = api.GetUserTimeline(user_id=user_id, include_rts=False, exclude_replies=True)[0]

        # build the URL and save u_id and status_id for later use
        u_screen_name = latest_status.user.screen_name
        u_id = latest_status.user.id_str
        status_id = latest_status.id_str
        status_url = f'https://twitter.com/{u_screen_name}/status/{status_id}'

        TWITTER_CACHE_DIR = config.BASE_DIR + '/cache/twitter_cache.json'

        # open json cache file to read
        with open(TWITTER_CACHE_DIR, 'r') as infile:

            twitter_cache = json.load(infile)

            # get from cache based on u_id
            cache = twitter_cache.get(u_id)
            if cache is not None and cache.get('ids'):

                cached_maple_ids = cache['ids']
                # the status id is already in cached_ids (posted), pass
                if status_id in cached_maple_ids:
                    print('*** TWITTER FETCH: NO NEW POSTS ***')

                else:
                    # open file to write, prepend the id to the right place
                    with open(TWITTER_CACHE_DIR, 'w') as outfile:
                        twitter_cache[u_id]['ids'].insert(0, status_id)
                        json.dump(twitter_cache, outfile)
                    # send the message to channel
                    await self.bot.send_message(channel, status_url)

            # no user_id found
            else:
                # setup the data and update the cached_data, write it to file
                data = {u_id: {'ids': [status_id, ], 'screen_name': u_screen_name}}
                twitter_cache.update(data)
                with open(TWITTER_CACHE_DIR, 'w') as outfile:
                    json.dump(twitter_cache, outfile)
                # send the message to channel
                await self.bot.send_message(channel, status_url)

        await asyncio.sleep(delay)

    def get_channel(self, id):
        """Return the given channel Object if in Production,
        #bot-test channel if in Development
        """
        if config.DEBUG is True:
            # bot-test channel
            channel = discord.Object(id='454890599410302977')
        else:
            # id-given channel
            channel = discord.Object(id=id)
        return channel


class Facebook:
    """A cog for Facebook related tasks"""

    def __init__(self, bot, util):
        self.bot = bot
        self.util = util

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

                        await self.util.send_message_as_embed(channel, embed=embed)

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

                    await self.util.send_message_as_embed(channel, embed=embed)

            await asyncio.sleep(40)
