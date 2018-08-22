import os
import django
from django.db.models import F
import discord
from discord.ext import commands
import config
from datetime import date, datetime
from random import choices, uniform
from collections import Counter
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_config')
django.setup()
from web.apps.items.models import Item, ItemStatRange
from web.apps.gachas.models import TreasureBoxGacha
from web.apps.users.models import DiscordUser, GachaInfo


class Gacha:
    """A cog for gacha commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, name='g')
    async def gacha(self, context, job=None, rolls=None):
        """MapleStory Mobile Treasure Box Gacha"""

        message = context.message
        author = message.author
        prefix = self.bot.command_prefix

        discord_user = self.check_user_in_db(author.id, author.name)

        if job is None or rolls is None:

            embed = discord.Embed(
                title=f'Cách quay rương và các lệnh liên quan',
                description=f'`{prefix}g` : hiện hướng dẫn này.\n'
                f'**`{prefix}g job 11`** : `job` là tên viết tắt của Job muốn quay rương.\n'
                f'**`{prefix}glist`** : xem tên viết tắt của các Job có thể quay rương.\n'
                f'**`{prefix}gdaily`** : nhận 10,000 Pha lê để quay rương hằng ngày (reset vào 7:00 sáng).\n'
                f'**`{prefix}ginfo`** : xem thông tin rương đồ của mình.',
                color=discord.Color.teal())
            embed.add_field(
                name='Thông tin cần biết',
                value='+ Mỗi lần xoay rương (x11) sẽ cần **1,000 Pha lê**\n'
                '+ Chỉ số của item sẽ **ngẫu nhiên** trong khoảng Min - Max của item đó.\n'
                '[**Credits to Lukishi**](https://docs.google.com/spreadsheets/d/1zEix7SJoHMyqKJxxheUtluKLOEmwtfgTJwXENZHsEoY/htmlview)\n'
                '+ Các món đồ có nền (Emblem) không đủ dữ kiện, nên sẽ tạm tính chỉ số Min - Max **bằng 130%** so với item không có nền')
            embed.add_field(
                name='Ví dụ',
                value=f'Quay rương (x11) cho Dark Knight: **`{prefix}g dk 11`**\n'
                f'Có thể dùng tên job viết liền (không dấu cách) để quay rương:\n**`{prefix}g darkknight 11`**',)
            await self.bot.say_as_embed(embed=embed)

        else:
            # inform the user that they don't have enough crystals for gacha to work
            if discord_user.gacha_info.crystal_owned <= 1000:
                embed = discord.Embed(
                    title=f'Không thể quay rương, số Pha lê không đủ',
                    description=f'{author.mention}, bạn đang có `{discord_user.gacha_info.crystal_owned} Pha lê`.'
                    ' Cần tối thiểu 1,000 Pha lê để quay rương.\n'
                    f'Nhập lệnh `{prefix}gdaily` để nhận Pha lê hằng ngày nhé!',
                    color=discord.Color.teal())
                await self.bot.say_as_embed(embed=embed)
                return
            # take 1,000 crystals from the user's balance
            else:
                discord_user.gacha_info.crystal_owned = F('crystal_owned') - 1000
                discord_user.gacha_info.crystal_used = F('crystal_used') + 1000

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

            rolls = int(rolls)
            if rolls == 11:
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

                embed = discord.Embed(
                    title='Kết quả mở Treasure Box 11 lần',
                    description=f'Job: {job_processed}\n {text_item_rank_count}',
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
                embed.set_footer(text=f'Bạn còn [{crystals} Pha lê] trong tài khoản.')
                await self.bot.say_as_embed(embed=embed)

    @commands.command(pass_context=True, name='glist')
    async def gachalist(self, context):
        job_abbrs = [
            ('Dark Knight', 'dk'),
            ('Bowmaster', 'bm'),
            ('Bishop', 'bs'),
            ('Night Lord', 'nl'),
            ('Corsair', 'cs'),
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
            f'Lệnh quay rương: `{self.bot.command_prefix}g viết_tắt số_lượng` (`số_lượng` = `11`)\n'
            f'Ví dụ quay rương cho Dark Knight: `{self.bot.command_prefix}g dk 11`\n',
            colour=discord.Color.teal())
        await self.bot.say(embed=embed)

    @commands.command(pass_context=True, name='gdaily')
    async def gachadaily(self, context):

        message = context.message
        author = message.author
        discord_user = self.check_user_in_db(author.id, author.name)

        # check if user already redeemed crystals
        if discord_user.gacha_info.daily_checked():
            embed = discord.Embed(
                title=None,
                description='Bạn đã nhận Pha lê hôm nay rồi nhé. Vui lòng thử lại **sau 7:00 sáng ngày mai**.',
                colour=discord.Color.teal())
            await self.bot.say(embed=embed)
            return

        # gives the user crystals
        discord_user.gacha_info.daily_check = datetime.utcnow()
        discord_user.gacha_info.crystal_owned = F('crystal_owned') + 10000
        discord_user.gacha_info.save()

        discord_user.gacha_info.refresh_from_db()
        crystals = '{:,}'.format(discord_user.gacha_info.crystal_owned)

        embed = discord.Embed(
            title=None,
            description=f'{author.mention} đã nhận 10,000 Pha lê vào tài khoản quay rương!\n'
            f'Hiện tại bạn đang có **{crystals}** Pha lê.',
            colour=discord.Color.teal())
        await self.bot.say(embed=embed)

    @commands.command(pass_context=True, name='ginfo')
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
            name='Pha lê:',
            value=f'Đang có: {owned}\nĐã dùng: {used}',
            inline=False)
        embed.add_field(
            name='Rương đồ:',
            value=f'+ Rare: **{gacha_info.rare_item_count}**\n'
            f'+ Epic: **{gacha_info.epic_item_count}**\n'
            f'+ Unique: **{gacha_info.unique_item_count}** (**{gacha_info.unique_emblem_item_count}** món có nền (Emblem))\n'
            f'+ Legendary: **{gacha_info.legendary_item_count}** (**{gacha_info.legendary_emblem_item_count}** món có nền (Emblem))\n',
            inline=False)

        # check for daily Crystal redemption
        if discord_user.gacha_info.daily_checked() is True:
            text_daily_checked = 'Đã nhận hôm nay'
        else:
            text_daily_checked = f'Chưa nhận, dùng lệnh `{self.bot.command_prefix}gdaily` để nhận Pha lê.'
        embed.add_field(
            name='Nhận Pha lê hằng ngày:',
            value=text_daily_checked)
        # set the thumbnail image for better visualizations
        embed.set_thumbnail(url='https://i.imgur.com/Sj2rPTN.png')
        await self.bot.say(embed=embed)

    def check_user_in_db(self, user_id, user_name):
        discord_user, created = DiscordUser.objects.get_or_create(discord_id=user_id, defaults={'discord_name': user_name})
        gacha_info, created = GachaInfo.objects.get_or_create(discord_user=discord_user)
        return discord_user


def setup(bot):
    bot.add_cog(Gacha(bot))
