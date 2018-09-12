import os
import django
from django.db.models import F
import discord
from discord.ext import commands
import config
from datetime import datetime
from pytz import timezone
from random import choices, uniform
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.config.settings')
django.setup()
from web.apps.items.models import Item, ItemStatRange
from web.apps.gachas.models import TreasureBoxGacha
from web.apps.users.models import DiscordUser, GachaInfo


class Gacha:
    """A cog for gacha commands"""

    def __init__(self, bot):
        self.bot = bot

    def is_treasure_box_channel(context):
        if config.DEBUG:
            return context.message.channel.id == '454890599410302977'
        else:
            return context.message.channel.id == '481712884196573194'

    @commands.command(pass_context=True, aliases=['g', 'gs'])
    @commands.check(is_treasure_box_channel)
    async def gacha(self, context, job=None, rolls=None):
        """MapleStory Mobile Treasure Box Gacha"""

        message = context.message
        author = message.author
        prefix = self.bot.command_prefix
        command_name = context.invoked_with

        discord_user = self.check_user_in_db(author.id, author.name)

        if job is None:

            embed = discord.Embed(
                title=f'Cách quay rương và các lệnh liên quan',
                description=f'• **`{prefix}g`**   **`{prefix}gs`** : hiện hướng dẫn này.\n'
                f'• **`{prefix}g job`** : Quay rương 10+1 lần.\n'
                f'• **`{prefix}gs job`** : Quay rương 1 lần.\n'
                '`job` là tên viết tắt của Job muốn quay rương.\n'
                f'• **`{prefix}glist`** : xem tên viết tắt của các Job có thể quay rương.\n'
                f'• **`{prefix}gdaily`** : nhận 10,000 :gem: (Pha lê) để quay rương hằng ngày (reset vào 00:00 sáng).\n'
                f'• **`{prefix}ginfo`** : xem thông tin rương đồ của mình.',
                color=discord.Color.teal())
            embed.add_field(
                name='Thông tin cần biết',
                value='• Quay rương 10+1 lần sẽ cần **1,000 :gem:**; Quay rương 1 lần sẽ cần **100 :gem:**.\n'
                '• Tỷ lệ ra đồ dựa trên bảng tỷ lệ của Nexon, [xem tại đây](https://m.nexon.com/terms/353)\n'
                '• Chỉ số của item sẽ **ngẫu nhiên** trong khoảng Min - Max của item đó.\n'
                '[**Credits to Lukishi**](https://docs.google.com/spreadsheets/d/1zEix7SJoHMyqKJxxheUtluKLOEmwtfgTJwXENZHsEoY/htmlview)\n'
                '• Các món đồ có nền (Emblem) không đủ dữ kiện, nên sẽ tạm tính chỉ số Min - Max **bằng 130%** so với item không có nền\n'
                '• Tỷ lệ ra nền chưa xác định, nên sẽ tạm cho là **10%**.')
            embed.add_field(
                name='Ví dụ',
                value=f'• Quay rương 10+1 cho Dark Knight: **`{prefix}g dk`**\n'
                f'• Quay rương 1 cho Bishop: **`{prefix}gs bs`**\n'
                f'Có thể dùng tên job viết liền (không dấu cách) để quay rương:\n**`{prefix}g darkknight`**',)
            await self.bot.say_as_embed(embed=embed)

        else:
            if command_name == 'g':
                rolls = 11
                min_cr = 1000
            elif command_name == 'gs':
                rolls = 1
                min_cr = 100

            # inform the user that they don't have enough crystals for gacha to work
            if rolls:
                if discord_user.gacha_info.crystal_owned < min_cr:
                    embed = discord.Embed(
                        title=f'Không thể quay rương, số :gem: không đủ',
                        description=f'{author.mention}, bạn đang có {discord_user.gacha_info.crystal_owned} :gem:.'
                        f' Cần tối thiểu {"{:,}".format(min_cr)} :gem: để quay rương.\n'
                        f'Nhập lệnh `{prefix}gdaily` để nhận :gem: hằng ngày nhé!',
                        color=discord.Color.teal())
                    await self.bot.say_as_embed(embed=embed)
                    return
                # take 1,000 crystals from the user's balance
                else:
                    discord_user.gacha_info.crystal_owned = F('crystal_owned') - min_cr
                    discord_user.gacha_info.crystal_used = F('crystal_used') + min_cr

                # process job given by the user
                if job.lower() in ['dk', 'darkknight']:
                    job_processed = 'Dark Knight'
                elif job.lower() in ['bm', 'bowmaster']:
                    job_processed = 'Bowmaster'
                elif job.lower() in ['bs', 'bis', 'bish', 'bishop']:
                    job_processed = 'Bishop'
                elif job.lower() in ['nl', 'nightlord']:
                    job_processed = 'Night Lord'
                elif job.lower() in ['cs', 'cor', 'sair', 'corsair']:
                    job_processed = 'Corsair'
                elif job.lower() in ['dw', 'dawnwarior']:
                    job_processed = 'Dawn Warrior'
                elif job.lower() in ['wa', 'windarcher']:
                    job_processed = 'Wind Archer'
                elif job.lower() in ['bw', 'blazewizard']:
                    job_processed = 'Blaze Wizard'
                elif job.lower() in ['nw', 'nightwalker']:
                    job_processed = 'Night Walker'
                elif job.lower() in ['tb', 'thunderbreaker']:
                    job_processed = 'Thunder Breaker'
                else:
                    embed = discord.Embed(
                        title=f'Không tìm được Job với cụm: {job}',
                        description=f'Vui lòng thử lại với *tên viết tắt của Job* hoặc *tên đầy đủ không dấu cách*.',
                        colour=discord.Color.teal())
                    await self.bot.say_as_embed(embed=embed)
                    return

                gacha_items = TreasureBoxGacha.objects.filter(job__job=job_processed)
                rate = []
                for item in gacha_items:
                    rate.append(item.rate)

                if rolls == 1:
                    result = choices(gacha_items, rate, k=rolls)
                else:
                    result = choices(gacha_items, rate, k=rolls - 1)

                    # for guaranteed unique item with multi rolls
                    guaranteed = gacha_items.filter(rank__rank='Unique')
                    uresult = choices(guaranteed)[0]
                    result.append(uresult)

                # randomly give Emblem to Unique/Legendary items with the rate of 10%
                # items with Emblem have an increase of stats of 30%
                emblem = ['(Emblem)', None]
                weights = [0.1, 0.9]
                emblem_stat_increase = 0.3
                # populate this to show the result in discord embed
                display_result = []
                # populate this to count number of items per rank
                rank_counts = []

                # process the result for final data display
                for gacha in result:

                    sub_type = gacha.item.sub_type
                    job = gacha.item.job
                    rank = gacha.rank

                    rank_counts.append(rank.rank)

                    display_data = {
                        'rank': rank.rank,
                        'sub_type': sub_type.sub_type,
                        'stat': {}
                    }

                    # give some emotes to distinguish item types
                    if sub_type.type.type == 'Weapon':
                        display_data.update({'name': f':crossed_swords: {gacha.item.name}'})
                    elif sub_type.type.type == 'Armor':
                        display_data.update({'name': f':shield: {gacha.item.name}'})
                    elif sub_type.type.type == 'Armor':
                        display_data.update({'name': f':ring: {gacha.item.name}'})
                    else:
                        display_data.update({'name': gacha.item.name})

                    # randomize stats
                    stats = gacha.item.stats.all()
                    for stat in stats:
                        try:
                            stat_range = ItemStatRange.objects.get(sub_type=sub_type, rank=rank, stat=stat, job=job)
                        except ItemStatRange.DoesNotExist:
                            # print(f'Not recognized stat: {stat}. Please check ItemStatRange data.')
                            continue
                        stat_amount = uniform(stat_range.min, stat_range.max)
                        display_data['stat'].update({stat.stat: round(stat_amount)})

                    # add emblem
                    if gacha.rank.rank in ['Unique', 'Legendary']:

                        # rank decorator based on rank
                        if gacha.rank.rank == 'Unique':
                            display_data['rank'] += ' :orange_book:'
                        else:
                            display_data['rank'] += ' :green_book:'

                        em = choices(emblem, weights)[0]
                        # increase emblem item count and modify stats
                        if em:
                            display_data['name'] += f' {em}'
                            for key, value in display_data['stat'].items():
                                display_data['stat'][key] = round(value * (1 + emblem_stat_increase))

                            if gacha.rank.rank == 'Unique':
                                discord_user.gacha_info.unique_emblem_item_count = F('unique_emblem_item_count') + 1
                            elif gacha.rank.rank == 'Legendary':
                                discord_user.gacha_info.legendary_emblem_item_count = F('legendary_emblem_item_count') + 1
                    display_result.append(display_data)

                # count items based on ranks
                item_rank_count = [0, 0, 0, 0]
                for item in rank_counts:
                    if item == 'Rare':
                        item_rank_count[0] += 1
                    elif item == 'Epic':
                        item_rank_count[1] += 1
                    elif item == 'Unique':
                        item_rank_count[2] += 1
                    elif item == 'Legendary':
                        item_rank_count[3] += 1

                # update the user gacha info
                discord_user.gacha_info.rare_item_count = F('rare_item_count') + item_rank_count[0]
                discord_user.gacha_info.epic_item_count = F('epic_item_count') + item_rank_count[1]
                discord_user.gacha_info.unique_item_count = F('unique_item_count') + item_rank_count[2]
                discord_user.gacha_info.legendary_item_count = F('legendary_item_count') + item_rank_count[3]

                # make text to inform the user of items obtained
                text_item_rank_count = f'Rare: `{item_rank_count[0]}` | Epic: `{item_rank_count[1]}` | '
                text_item_rank_count += f'Unique: `{item_rank_count[2]}` | Legendary: `{item_rank_count[3]}`'

                if rolls == 1:
                    desr = f'Job: {job_processed}'
                else:
                    desr = f'Job: {job_processed}\n {text_item_rank_count}'

                embed = discord.Embed(
                    title=f'Kết quả mở Treasure Box {rolls} lần của [{author.display_name}]',
                    description=desr,
                    colour=discord.Color.teal())

                for item_result in display_result:
                    text_info = f'Rank: **{item_result["rank"]}**\nType: **{item_result["sub_type"]}**\nStat:\n'
                    for key, value in item_result['stat'].items():
                        text_info += f'+ **{key}: {value}**\n'
                    embed.add_field(
                        name=item_result['name'],
                        value=text_info)

                discord_user.gacha_info.save()
                discord_user.gacha_info.refresh_from_db()
                crystals = '{:,}'.format(discord_user.gacha_info.crystal_owned)
                embed.set_footer(
                    text=f'Bạn còn [💎 x{crystals}] trong tài khoản.',
                    icon_url='https://i.imgur.com/Sh9kXA8.png')
                await self.bot.say_as_embed(embed=embed)

    @commands.command(pass_context=True, name='glist')
    @commands.check(is_treasure_box_channel)
    async def gachalist(self, context):
        prefix = self.bot.command_prefix
        job_abbrs = [
            ('Dark Knight', 'dk'),
            ('Bowmaster', 'bm'),
            ('Bishop', 'bs'),
            ('Night Lord', 'nl'),
            ('Corsair', 'cs'),

            ('Dawn Warrior', 'dw'),
            ('Wind Archer', 'wa'),
            ('Blaze Wizard', 'bw'),
            ('Night Walker', 'nw'),
            ('Thunder Breaker', 'tb'),

        ]
        message = context.message
        author = message.author
        self.check_user_in_db(author.id, author.name)

        text_job_abbrs = 'Viết tắt | Tên Job\n'
        for job in job_abbrs:
            text_job_abbrs += f'{job[1]}       : {job[0]}\n'

        embed = discord.Embed(
            title='Danh sách Job và các tên viết tắt dùng để quay rương',
            description=f'```{text_job_abbrs}```\n'
            f'**Lệnh quay rương**\n'
            f'• `{prefix}gs viết_tắt` (1 lần)\n'
            f'• `{prefix}g viết_tắt` (10+1 lần)\n'
            f'Ví dụ quay rương 10+1 lần cho Dark Knight: `{prefix}g dk`\n',
            colour=discord.Color.teal())
        await self.bot.say(embed=embed)

    @commands.command(pass_context=True, name='gdaily')
    @commands.check(is_treasure_box_channel)
    async def gachadaily(self, context):

        message = context.message
        author = message.author
        discord_user = self.check_user_in_db(author.id, author.name)

        # check if user already redeemed crystals
        if discord_user.gacha_info.daily_checked():
            embed = discord.Embed(
                title=None,
                description='Bạn đã nhận :gem: hôm nay rồi nhé. Vui lòng thử lại **sau 00:00 sáng mai**.',
                colour=discord.Color.teal())
            await self.bot.say(embed=embed)
            return

        # gives the user crystals
        vn_tz = timezone('Asia/Ho_Chi_Minh')
        discord_user.gacha_info.daily_check = datetime.now().astimezone(vn_tz)
        discord_user.gacha_info.crystal_owned = F('crystal_owned') + 10000
        discord_user.gacha_info.save()

        discord_user.gacha_info.refresh_from_db()
        crystals = '{:,}'.format(discord_user.gacha_info.crystal_owned)

        embed = discord.Embed(
            title=None,
            description=f'{author.mention} đã nhận :gem: x10,000  vào tài khoản quay rương!\n'
            f'Hiện tại bạn đang có **:gem: x{crystals}**.',
            colour=discord.Color.teal())
        await self.bot.say(embed=embed)

    @commands.command(pass_context=True, name='ginfo')
    @commands.check(is_treasure_box_channel)
    async def gachainfo(self, context):

        message = context.message
        author = message.author

        # check for user in db, create one if not present
        discord_user = self.check_user_in_db(author.id, author.name)
        gacha_info = discord_user.gacha_info

        # add thousand separator
        owned = '{:,}'.format(gacha_info.crystal_owned)
        used = '{:,}'.format(gacha_info.crystal_used)

        embed = discord.Embed(
            title=f'Thông tin rương đồ của {author.display_name}',
            description=None,
            colour=discord.Color.teal())
        embed.add_field(
            name='Pha lê',
            value=f'• Đang có: :gem: x**{owned}**\n• Đã dùng: :gem: x**{used}**',
            inline=False)
        embed.add_field(
            name='Rương đồ',
            value=f'• Rare: **{gacha_info.rare_item_count}**\n'
            f'• Epic: **{gacha_info.epic_item_count}**\n'
            f'• Unique: **{gacha_info.unique_item_count}** (**{gacha_info.unique_emblem_item_count}** món có nền (Emblem))\n'
            f'• Legendary: **{gacha_info.legendary_item_count}** (**{gacha_info.legendary_emblem_item_count}** món có nền (Emblem))\n',
            inline=False)

        # check for daily Crystal redemption
        if discord_user.gacha_info.daily_checked() is True:
            text_daily_checked = 'Đã nhận hôm nay.'
        else:
            text_daily_checked = f'Chưa nhận, dùng lệnh `{self.bot.command_prefix}gdaily` để nhận :gem:.'
        embed.add_field(
            name='Nhận 💎 hằng ngày',
            value=text_daily_checked)
        # set the thumbnail image for better visualizations
        embed.set_thumbnail(url='https://i.imgur.com/Sj2rPTN.png')
        await self.bot.say(embed=embed)

    def check_user_in_db(self, user_id, user_name):
        discord_user, created = DiscordUser.objects.get_or_create(discord_id=user_id, defaults={'discord_name': user_name})
        gacha_info, created = GachaInfo.objects.get_or_create(discord_user=discord_user)
        return discord_user

    @gacha.error
    @gachalist.error
    @gachadaily.error
    @gachainfo.error
    async def gacha_error(self, error, context):
        print(error)
        return


def setup(bot):
    bot.add_cog(Gacha(bot))
