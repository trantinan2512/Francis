import asyncio
import json
import os

import twitter
import discord
from discord.ext import commands

from pprint import pprint
import config

# francis/cogs/here -> francis/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Twitter:
    """A cog for Link management commands"""

    def __init__(self, bot, util):
        self.bot = bot
        self.util = util

    async def fetch_maplem_latest_tweet(self):
        await self.bot.wait_until_ready()

        channel = discord.Object(id='454890599410302977')
        api = twitter.api.Api(
            consumer_key=config.TWITTER_CONSUMER_KEY,
            consumer_secret=config.TWITTER_CONSUMER_SECRET,
            access_token_key=config.TWITTER_ACCESS_TOKEN,
            access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET,
            tweet_mode='extended')

        while not self.bot.is_closed:

            MapleM = api.GetUser(user_id=816396540017152000)
            # pprint(api.GetUserTimeline(user_id=816396540017152000))
            # print(MapleM.status)
            # print(MapleM.status.full_text)
            data = {
                "MapleM": {
                    'full_text': MapleM.status.full_text,
                    'id': MapleM.status.id_str,
                    'url': MapleM.status.media[0].expanded_url
                }
            }

            TWITTER_CACHE_DIR = BASE_DIR + '/cache/twitter_cache.json'

            with open(TWITTER_CACHE_DIR, 'r') as infile:

                twitter_cache = json.load(infile)
                maplem = twitter_cache.get('MapleM')

                if maplem is not None and maplem.get('id'):
                    cached_maplem_id = maplem.get('id')

                    if cached_maplem_id == data['MapleM']['id']:
                        pass

                    else:
                        with open(TWITTER_CACHE_DIR, 'w') as outfile:
                            twitter_cache['MapleM'] = data['MapleM']
                            json.dump(twitter_cache, outfile)

                        await self.bot.send_message(channel, data['MapleM']['url'])

                else:
                    twitter_cache.update(data)
                    with open(TWITTER_CACHE_DIR, 'w') as outfile:
                        json.dump(twitter_cache, outfile)

                    await self.bot.send_message(channel, data['MapleM']['url'])

            await asyncio.sleep(5)

    async def fetch_maple_latest_tweet(self):
        await self.bot.wait_until_ready()

        channel = discord.Object(id='454890599410302977')
        api = twitter.api.Api(
            consumer_key=config.TWITTER_CONSUMER_KEY,
            consumer_secret=config.TWITTER_CONSUMER_SECRET,
            access_token_key=config.TWITTER_ACCESS_TOKEN,
            access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET,
            tweet_mode='extended')

        while not self.bot.is_closed:

            Maple = api.GetUser(user_id=34667202)
            # pprint(api.GetUserTimeline(user_id=816396540017152000))
            # print(MapleM.status)
            # print(MapleM.status.full_text)
            data = {
                "Maple": {
                    'full_text': Maple.status.full_text,
                    'id': Maple.status.id_str,
                    'url': Maple.status.media[0].expanded_url
                }
            }

            TWITTER_CACHE_DIR = BASE_DIR + '/cache/twitter_cache.json'

            with open(TWITTER_CACHE_DIR, 'r') as infile:

                twitter_cache = json.load(infile)
                maple = twitter_cache.get('Maple')

                if maple is not None and maple.get('id'):
                    cached_maple_id = maple.get('id')

                    if cached_maple_id == data['Maple']['id']:
                        pass

                    else:
                        with open(TWITTER_CACHE_DIR, 'w') as outfile:
                            twitter_cache['Maple'] = data['Maple']
                            json.dump(twitter_cache, outfile)

                        await self.bot.send_message(channel, data['Maple']['url'])

                else:
                    twitter_cache.update(data)
                    with open(TWITTER_CACHE_DIR, 'w') as outfile:
                        json.dump(twitter_cache, outfile)

                    await self.bot.send_message(channel, data['Maple']['url'])

            await asyncio.sleep(5)
