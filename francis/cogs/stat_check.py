from discord.ext import commands
import discord
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.config.settings')
django.setup()
from web.apps.items.models import ItemStatRange


class StatCheck:
    """A cog for Link management commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['st', 'stat'])
    async def check_stat(self, context, sub_type=None, job=None):
        """Lệnh lấy stat cho MapleStory Mobile"""

        prefix = self.bot.command_prefix

        if sub_type is None:

            embed = discord.Embed(
                title='Hướng dẫn kiểm tra chỉ số item GMSM',
                description=f'• **`{prefix}st`** : hiện hướng dẫn này.\n'
                f'• **`{prefix}st loại_trang_bị job`** : Kiểm tra chỉ số của `loại_trang_bị` mà `job` sử dụng.\n'
                f'• **`{prefix}stlist`** : xem danh sách các `loại_trang_bị` và `job` có thể kiểm tra chỉ số.\n'
                f'• **`{prefix}stinfo`** : xem ghi chú và nguồn của các chỉ số.',
                color=discord.Color.teal())

            await self.bot.say_as_embed(embed=embed)

        else:

            item_list = ItemStatRange.objects.filter(sub_type__sub_type__iexact=sub_type)
            item_list = item_list.distinct('rank')

            distincted = item_list.distinct('job').values_list('job__job')
            job_list_text = []
            for job_item in distincted:
                job_list_text.append(job_item[0])

            jobs_text = ', '.join(job_list_text)

            if item_list.count() == 0:
                embed = discord.Embed(
                    title=f':x: Không tìm thấy trang bị có loại: {sub_type}',
                    description=f'Nhập lệnh `{prefix}stlist` để biết các `loại_trang_bị` và tên `job` khả dụng.',
                    color=discord.Color.red())
                await self.bot.say_as_embed(embed=embed)
                return
            else:
                table_text = 'Rank           Min    Max            \n'
                emblem_inc = 1.3
                if item_list[0].job_specific is False and sub_type.lower() not in ['shoulder', 'cape', 'belt']:
                    if job is None:
                        embed = discord.Embed(
                            title=f':x: Trang bị bạn đang tìm {sub_type} cần phải cung cấp thêm tên `job`',
                            description=f'Vui lòng thử lại với cú pháp: `{prefix}st {sub_type} job`\n'
                            f'Nhập lệnh `{prefix}stlist` để biết các tên `job` khả dụng.',
                            color=discord.Color.red())
                        await self.bot.say_as_embed(embed=embed)
                        return
                    else:
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
                            job_processed = job

                        item_list = item_list.filter(job__job__iexact=job_processed, stat__stat__iexact='PHY DEF')
                        jobs_text = item_list[0].job.job
                        if item_list.count() == 0:
                            embed = discord.Embed(
                                title=f':x: Không tìm thấy chỉ số cho **{sub_type}** thuộc nghề **{job}**',
                                description=f'Có thể bạn đã nhập sai tên `job`.\n'
                                f'Nhập lệnh `{prefix}stlist` để biết các `job` khả dụng.',
                                color=discord.Color.red())
                            await self.bot.say_as_embed(embed=embed)
                            return

                for item in item_list:

                    table_text += item.rank.rank + self.add_space(14 - len(item.rank.rank))
                    table_text += '{:,}'.format(int(round(item.min))) + self.add_space(6 - len('{:,}'.format(int(round(item.min)))))
                    table_text += '{:,}'.format(int(round(item.max))) + '\n'
                    if item.rank.rank in ['Unique', 'Legendary', 'Mythic']:
                        table_text += item.rank.rank + '(E)' + self.add_space(11 - len(item.rank.rank))
                        table_text += '{:,}'.format(int(round(item.min * emblem_inc)))
                        table_text += self.add_space(6 - len('{:,}'.format(int(round(item.min * emblem_inc)))))
                        table_text += '{:,}'.format(int(round(item.max * emblem_inc))) + '\n'

                embed = discord.Embed(
                    title='Kiểm tra chỉ số trang bị',
                    description=f'Trang bị: **{item_list[0].sub_type.sub_type}**\n'
                    f'Nghề: **{jobs_text}**',
                    color=discord.Color.blue())

                embed.add_field(
                    name='Kết quả',
                    value=f'```{table_text}```')

                await self.bot.say_as_embed(embed=embed)

    @commands.command(pass_context=True, name='stlist')
    async def stat_list(self, context):
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

        item_abbrs = [
            'spear', 'bow', 'wand', 'claw', 'gun', '2hsword', 'staff', 'knuckler',
            'hat', 'outfit', 'gloves', 'shoes',
            'shoulder', 'belt', 'cape',
        ]

        text_job_abbrs = 'Viết tắt | Tên Job\n'
        for job in job_abbrs:
            text_job_abbrs += f'{job[1]}       : {job[0]}\n'

        embed = discord.Embed(
            title='Danh sách loại_trang_bị và job có thể kiểm tra chỉ số',
            description=None,
            colour=discord.Color.teal())
        embed.add_field(
            name='loại_trang_bị',
            value=f'```{", ".join(item_abbrs)}```')
        embed.add_field(
            name='job',
            value=f'```{text_job_abbrs}```\n')
        embed.add_field(
            name='Ví dụ',
            value=f'• Kiểm tra chỉ số Spear: `{prefix}st spear`\n'
            f'• Kiểm tra chỉ số Outfit của Bishop: `{prefix}st outfit bs`')

        await self.bot.say(embed=embed)

    @commands.command(pass_context=True, name='stinfo')
    async def stat_information(self, context):

        embed = discord.Embed(
            title='Ghi chú về thông tin chỉ số',
            description='• Dữ kiện về đồ có nền (Emblem) còn thiếu, nên tạm tính Min-Max bằng 130% so với item thông thường.\n'
            '• Chỉ số đã được làm tròn, bạn có thể xem nguồn bên dưới để biết chỉ số chính xác.\n'
            '• Nguồn: [Bách khoa toàn thư của Lukishi](https://docs.google.com/spreadsheets/d/1zEix7SJoHMyqKJxxheUtluKLOEmwtfgTJwXENZHsEoY/htmlview)',
            colour=discord.Color.teal())

        await self.bot.say(embed=embed)

    def add_space(self, no_of_spaces):
        spaces = ''
        while no_of_spaces >= 0:
            spaces += ' '
            no_of_spaces -= 1
        return spaces


def setup(bot):
    bot.add_cog(StatCheck(bot))
