# from pprint import pprint
# import json

import discord
from discord.ext import commands


class GenshinAdmin(commands.Cog):
    """A cog for GenshinAdmin-only commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='genshincr', hidden=True)
    @commands.is_owner()
    async def _get_or_create_genshin_character_roles(self, context):
        characters = [
            {
                "id": 1,
                "name": "Amber",
                "element": "p",
                "rank": 4,
                "weapon_type": "bo"
            },
            {
                "id": 2,
                "name": "Barbara",
                "element": "h",
                "rank": 4,
                "weapon_type": "ca"
            },
            {
                "id": 3,
                "name": "Beidou",
                "element": "e",
                "rank": 4,
                "weapon_type": "cl"
            },
            {
                "id": 4,
                "name": "Bennett",
                "element": "p",
                "rank": 4,
                "weapon_type": "sw"
            },
            {
                "id": 5,
                "name": "Chongyun",
                "element": "c",
                "rank": 4,
                "weapon_type": "cl"
            },
            {
                "id": 6,
                "name": "Diluc",
                "element": "p",
                "rank": 5,
                "weapon_type": "cl"
            },
            {
                "id": 7,
                "name": "Fischl",
                "element": "e",
                "rank": 4,
                "weapon_type": "bo"
            },
            {
                "id": 8,
                "name": "Jean",
                "element": "a",
                "rank": 5,
                "weapon_type": "sw"
            },
            {
                "id": 9,
                "name": "Kaeya",
                "element": "c",
                "rank": 4,
                "weapon_type": "sw"
            },
            {
                "id": 10,
                "name": "Keqing",
                "element": "e",
                "rank": 5,
                "weapon_type": "sw"
            },
            {
                "id": 11,
                "name": "Klee",
                "element": "p",
                "rank": 5,
                "weapon_type": "ca"
            },
            {
                "id": 12,
                "name": "Lisa",
                "element": "e",
                "rank": 4,
                "weapon_type": "ca"
            },
            {
                "id": 13,
                "name": "Mona",
                "element": "h",
                "rank": 5,
                "weapon_type": "ca"
            },
            {
                "id": 14,
                "name": "Ningguang",
                "element": "g",
                "rank": 4,
                "weapon_type": "ca"
            },
            {
                "id": 15,
                "name": "Noelle",
                "element": "g",
                "rank": 4,
                "weapon_type": "cl"
            },
            {
                "id": 16,
                "name": "Qiqi",
                "element": "c",
                "rank": 5,
                "weapon_type": "sw"
            },
            {
                "id": 17,
                "name": "Razor",
                "element": "e",
                "rank": 4,
                "weapon_type": "cl"
            },
            {
                "id": 18,
                "name": "Sucrose",
                "element": "a",
                "rank": 4,
                "weapon_type": "ca"
            },
            {
                "id": 19,
                "name": "Traveler",
                "element": "a",
                "rank": 5,
                "weapon_type": "sw"
            },
            {
                "id": 20,
                "name": "Venti",
                "element": "a",
                "rank": 5,
                "weapon_type": "bo"
            },
            {
                "id": 21,
                "name": "Xiangling",
                "element": "p",
                "rank": 4,
                "weapon_type": "po"
            },
            {
                "id": 22,
                "name": "Xiao",
                "element": "a",
                "rank": 5,
                "weapon_type": "po"
            },
            {
                "id": 23,
                "name": "Xingqiu",
                "element": "h",
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
                 'Ayaka',
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
                 'Xingqiu']
        roles = []
        for role in context.guild.roles:
            if role.name not in names:
                continue
            roles.append(role.id)
        roles.reverse()
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


def setup(bot):
    bot.add_cog(GenshinAdmin(bot))
