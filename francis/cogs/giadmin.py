# from pprint import pprint
# import json

import discord
from discord.ext import commands

import config


class GenshinAdmin(commands.Cog):
    """A cog for GenshinAdmin-only commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='genshincr', hidden=True)
    @commands.is_owner()
    async def _get_or_create_genshin_character_roles(self, context):
        characters = [
            {
                "name": "Amber",
                "element": "p",
                "rank": 4,
                "weapon_type": "bo"
            },
            {
                "name": "Barbara",
                "element": "h",
                "rank": 4,
                "weapon_type": "ca"
            },
            {
                "name": "Beidou",
                "element": "e",
                "rank": 4,
                "weapon_type": "cl"
            },
            {
                "name": "Bennett",
                "element": "p",
                "rank": 4,
                "weapon_type": "sw"
            },
            {
                "name": "Chongyun",
                "element": "c",
                "rank": 4,
                "weapon_type": "cl"
            },
            {
                "name": "Diluc",
                "element": "p",
                "rank": 5,
                "weapon_type": "cl"
            },
            {
                "name": "Fischl",
                "element": "e",
                "rank": 4,
                "weapon_type": "bo"
            },
            {
                "name": "Jean",
                "element": "a",
                "rank": 5,
                "weapon_type": "sw"
            },
            {
                "name": "Kaeya",
                "element": "c",
                "rank": 4,
                "weapon_type": "sw"
            },
            {
                "name": "Keqing",
                "element": "e",
                "rank": 5,
                "weapon_type": "sw"
            },
            {
                "name": "Klee",
                "element": "p",
                "rank": 5,
                "weapon_type": "ca"
            },
            {
                "name": "Lisa",
                "element": "e",
                "rank": 4,
                "weapon_type": "ca"
            },
            {
                "name": "Mona",
                "element": "h",
                "rank": 5,
                "weapon_type": "ca"
            },
            {
                "name": "Ningguang",
                "element": "g",
                "rank": 4,
                "weapon_type": "ca"
            },
            {
                "name": "Noelle",
                "element": "g",
                "rank": 4,
                "weapon_type": "cl"
            },
            {
                "name": "Qiqi",
                "element": "c",
                "rank": 5,
                "weapon_type": "sw"
            },
            {
                "name": "Razor",
                "element": "e",
                "rank": 4,
                "weapon_type": "cl"
            },
            {
                "name": "Sucrose",
                "element": "a",
                "rank": 4,
                "weapon_type": "ca"
            },
            {
                "name": "Traveler",
                "element": "a",
                "rank": 5,
                "weapon_type": "sw"
            },
            {
                "name": "Venti",
                "element": "a",
                "rank": 5,
                "weapon_type": "bo"
            },
            {
                "name": "Xiangling",
                "element": "p",
                "rank": 4,
                "weapon_type": "po"
            },
            {
                "name": "Xiao",
                "element": "a",
                "rank": 5,
                "weapon_type": "po"
            },
            {
                "name": "Xingqiu",
                "element": "h",
                "rank": 4,
                "weapon_type": "sw"
            },
            # 1.1
            {
                "name": "Tartaglia",
                "element": "h",
                "rank": 4,
                "weapon_type": "sw"
            },
            {
                "name": "Zhongli",
                "element": "g",
                "rank": 4,
                "weapon_type": "sw"
            },
            {
                "name": "Diona",
                "element": "c",
                "rank": 4,
                "weapon_type": "sw"
            },
            {
                "name": "Xinyan",
                "element": "p",
                "rank": 4,
                "weapon_type": "sw"
            }
        ]
        colors = {
            'a': 0x64AD84,
            'p': 0xB21F1F,
            'c': 0x80ACD3,
            'd': 0x82B132,
            'e': 0x6D51B8,
            'g': 0xECCD5A,
            'h': 0x228EBA
        }
        for character in characters:
            # ignore traveler
            if character['name'] == 'Traveler':
                continue
            # ignore created
            if any(character['name'] == role.name for role in context.guild.roles):
                continue
            new_role = await context.guild.create_role(
                name=character['name'],
                color=discord.Color(value=colors[character['element']])
            )
            print(f'Created {new_role.name} role in {context.guild.name}')

    @commands.command(name='genshinroleids', hidden=True)
    @commands.is_owner()
    async def _generate_genshin_character_role_ids(self, context):
        names = ['Amber',
                 'Aether - Anemo',
                 'Aether - Geo',
                 'Barbara',
                 'Beidou',
                 'Bennett',
                 'Chongyun',
                 'Diluc',
                 'Fischl',
                 'Jean',
                 'Kaeya',
                 'Keqing',
                 'Klee',
                 'Lisa',
                 'Lumine - Anemo',
                 'Lumine - Geo',
                 'Mona',
                 'Ningguang',
                 'Noelle',
                 'Qiqi',
                 'Razor',
                 'Sucrose',
                 'Venti',
                 'Xiangling',
                 'Xiao',
                 'Xingqiu',
                 # 1.1
                 'Tartaglia',
                 'Zhongli',
                 'Diona',
                 'Xinyan',
                 # 1.2
                 'Ayaka',
                 'Albedo',
                 'Ganyu',
                 # 1.3
                 'Hu Tao',
                 # 1.4
                 'Rosaria',
                 # 1.5
                 'Yanfei',
                 'Eula',
                 ]
        names.sort()
        roles = []
        for name in names:
            role = discord.utils.get(context.guild.roles, name=name)
            if not role:
                continue
            roles.append(role.id)
        await context.send(','.join(str(role_id) for role_id in roles))
        await context.say_as_embed('\n'.join(f'<@&{role_id}>' for role_id in roles))

    @commands.command(name='genshinemojiids', hidden=True)
    @commands.is_owner()
    async def _generate_genshin_character_emoji_ids(self, context):
        emojis_data = []
        emojis = '```\n'
        for emoji in context.guild.emojis:
            emojis_data.append({'name': emoji.name, 'id': emoji.id})
        emojis += '```'

        emojis_data.sort(key=lambda x: x['name'])
        await context.send(','.join(str(emoji['id']) for emoji in emojis_data))

    @commands.command(name='genshinsendemojis', hidden=True)
    @commands.is_owner()
    async def _send_chunk_emojis_and_react(self, context):
        emoji_ids = config.PONPON_ROLE_REACT_EMOJI_IDS
        for chunk in chunks(emoji_ids, 10):
            message = await context.send(' '.join(f'<:something:{emoji_id}>' for emoji_id in chunk))
            for emoji_id in chunk:
                emoji = context.bot.get_emoji(id=emoji_id)
                await message.add_reaction(emoji)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def setup(bot):
    bot.add_cog(GenshinAdmin(bot))
