from datetime import datetime

import discord
import tweepy
from discord.ext import tasks, commands
from pytz import timezone

import config
from utils import db, channel as ch

TWITTER_USERS = {
    816396540017152000: {'sheet': 'twitter_gmsm', 'channel_ids': [455635507561627648, ], 'name': 'GMSM'},
    34667202: {'sheet': 'twitter_gms', 'channel_ids': [455634325086404608, ], 'name': 'GMS'},
    940045596575989765: {'sheet': 'twitter_hi3', 'channel_ids': [563996767302057984, ], 'name': 'HI3rd'},
    # global genshin twitter
    1072404907230060544: {'sheet': 'twitter_genshin', 'channel_ids': [754672596821344298, ], 'name': 'Genshin'},
    # japanese genshin twitter
    1070960596357509121: {'sheet': 'twitter_genshin', 'channel_ids': [758899411517833236, ], 'name': 'Genshin'},
}


class TweetFetcher(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET)
        auth.set_access_token(config.TWITTER_ACCESS_TOKEN, config.TWITTER_ACCESS_TOKEN_SECRET)

        self.api = tweepy.API(auth, wait_on_rate_limit=True)

        self.db = db.initialize_db()

        self._listener.start()

    def cog_unload(self):
        self._listener.cancel()

    @tasks.loop(seconds=60.0)
    async def _listener(self):

        for twitter_id, info in TWITTER_USERS.items():
            channel_ids = info['channel_ids']
            await self.send_latest_status(twitter_id, channel_ids)

    @_listener.before_loop
    async def _before_listening(self):
        print('[Tweet Fetchers] Waiting for ready state...')

        await self.bot.wait_until_ready()

        print('[Tweet Fetchers] Ready and running!')

    # send status to given channel
    async def send_latest_status(self, user_id, channel_ids: list):
        """
        Send the latest status of given user_id, to the channel
        """

        # fetch the user_id twitter info
        tweet_count = 5
        try:
            latest_tweets = self.api.user_timeline(user_id, count=tweet_count)
        except tweepy.TweepError:
            return

        sheet, posted_ids = self.get_posted_ids(user_id)
        if not sheet or not posted_ids:
            return

        for tweet in latest_tweets:

            # build these things for later use
            u_screen_name = tweet.user.screen_name
            status_id = tweet.id_str

            # not retweet, not reply
            if not tweet.text.startswith('RT @') and not tweet.in_reply_to_user_id:
                proceed = True
            # reply to self
            elif user_id == tweet.in_reply_to_user_id:
                proceed = True
            else:
                proceed = False

            if proceed is False:
                continue

            if status_id in posted_ids:
                continue

            now = datetime.now()
            vn_tz = now.replace(tzinfo=timezone('Asia/Ho_Chi_Minh'))
            timestamp_date = vn_tz.strftime('%d/%m/%Y')
            timestamp_time = vn_tz.strftime('%H:%M:%S')

            sheet.insert_row([status_id, timestamp_date, timestamp_time], index=2)

            # build the URL and save u_id and status_id for later use
            status_url = f'https://twitter.com/{u_screen_name}/status/{status_id}'

            # send the message to channel
            for channel_id in channel_ids:
                channel = ch.get_channel(bot=self.bot, id=channel_id)
                if not channel:
                    continue
                message = await channel.send(status_url)
                # try to auto-publish the message
                try:
                    await message.publish()
                except discord.Forbidden:
                    pass

            print(f'Twitter Fetch: [{u_screen_name}] [Fetched: {status_url}]')

            # updates the sheet and posted_ids
            sheet, posted_ids = self.get_posted_ids(user_id)
            if not sheet or not posted_ids:
                return

    def get_posted_ids(self, user_id):
        try:
            sheet = self.db.worksheet(TWITTER_USERS[user_id]['sheet'])
            return sheet, sheet.col_values(1)
        except Exception:
            try:
                self.db = db.initialize_db()
            except Exception:
                pass
            return None, None


def setup(bot):
    bot.add_cog(TweetFetcher(bot))
