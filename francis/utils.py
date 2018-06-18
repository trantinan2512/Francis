import discord
import json
from dateparser import parse
from datetime import datetime
from var import *
from config import DEBUG, GAPI_AUTH_DICT, BASE_DIR

import gspread
from oauth2client.service_account import ServiceAccountCredentials


class Utility:
    def __init__(self, bot):
        self.bot = bot

    async def say_as_embed(self, message=None, title=None, embed=None, color='info'):
        """Make the bot say as an Embed.
        Passing an 'embed' will send it instead.
        Shortcut for color kwarg: 'info' (default), 'warning', 'error', 'success'
        """

        if color == 'info':
            color = discord.Color.teal()
        elif color == 'warning':
            color = discord.Color.gold()
        elif color == 'error':
            color = discord.Color.red()
        elif color == 'success':
            color = discord.Color.green()

        if embed is None:
            embed = discord.Embed(
                title=title,
                description=message,
                colour=color)
            await self.bot.say(embed=embed)
        else:
            await self.bot.say(embed=embed)

    async def send_message_as_embed(self, channel, message=None, title=None, embed=None, color='info'):
        """Send a message to a specified channel as an Embed.
        Passing an 'embed' will send it instead, and ignore things in 'message' kwarg.
        Shortcut for color kwarg: 'info' (default), 'warning', 'error', 'success'
        """

        if color == 'info':
            color = discord.Color.teal()
        elif color == 'warning':
            color = discord.Color.gold()
        elif color == 'error':
            color = discord.Color.red()
        elif color == 'success':
            color = discord.Color.green()

        if embed is None:
            embed = discord.Embed(
                title=title,
                description=message,
                colour=color)
            await self.bot.send_message(channel, embed=embed)
        else:
            await self.bot.send_message(channel, embed=embed)

    async def process_role(self, role):
        """Process the role given by the user.
        Return None if no roles detected"""

        # strip the leading @ in case someone fucks up
        role = role.lstrip('@')

        tmp_cap = list()

        for w in role.split(' '):
            if w.lower() in ['fp', 'il']:
                tmp_cap.append(w.upper())
            else:
                tmp_cap.append(w.capitalize())

        capped_role = ' '.join(tmp_cap)

        if role in AUTOASIGN_ROLES:
            return role

        elif capped_role in AUTOASIGN_ROLES:
            return capped_role

        elif role.upper() in AUTOASIGN_ROLES:
            return role.upper()

        elif role.startswith('all'):
            # returns a tuple
            return 'all', role.lstrip('all').strip()

        else:
            return None

    def get_channel(self, server=None, id='454890599410302977'):
        """Return the given channel Object if in Production,
        # bot-test channel if in Development
        """
        if server is not None:
            if DEBUG is True:
                channel = server.get_channel('454890599410302977')
            else:
                channel = server.get_channel(id=id)
        else:
            if DEBUG is True:
                # bot-test channel
                channel = discord.Object(id='454890599410302977')
            else:
                # id-given channel
                channel = discord.Object(id=id)
        return channel

    def initialize_db(self, key=None):
        """Initialize and return the DB
        (optional) key: the key of google spreadsheet. Defaults to Francis DB's key
        """
        if key is None:
            # Francis DB
            key = '1hpF3TVCHIMXXXdeVtHdPgQOCOq1NfqYp71uJ4suQViI'

        # Google Drive API related stuff
        scopes = ['https://spreadsheets.google.com/feeds',
                  'https://www.googleapis.com/auth/drive']

        credentials = ServiceAccountCredentials.from_json_keyfile_dict(GAPI_AUTH_DICT, scopes)
        client = gspread.authorize(credentials)

        db = client.open_by_key(key)

        return db

    def check_delay(self, timestamp, delay):
        """Return True if 'timestamp' has passed an amount of 'delay' or higher, False otherwise.
        And the time passed in rounded to 0.x
        - timestamp: 'str' type that can be parsed
        - delay: 'int' type, in seconds"""
        try:
            timestamp = parse(timestamp)
            now = datetime.now()
            time_passed = (now - timestamp).total_seconds()
            return (time_passed > delay), round((delay - time_passed), 1)
        # parsing timestamp returns None
        except TypeError:
            return None, None
