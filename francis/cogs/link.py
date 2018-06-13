from discord.ext import commands
import discord


class Link:
    """A cog for Link management commands"""

    def __init__(self, bot, util):
        self.bot = bot
        self.util = util

    @commands.command(pass_context=True)
    async def link(self, context, game=None):
        """Lệnh lấy link hữu ích cho game"""

        if game:
            game = game.lower()

        prefix = self.bot.command_prefix

        if game is None or game not in ['gms', 'gmsm']:

            embed = discord.Embed(
                title='Vui lòng nhập tên_game',
                description=''
                f'Cú pháp: `{prefix}link tên_game`\n'
                f'`tên_game` là `GMS` hoặc `GMSM` (hiện tại chỉ hỗ trợ 2 game này).\n\n'
                f'Ví dụ: `{prefix}link gms`',
                color=discord.Color.red())

            await self.util.say_as_embed(embed=embed)

        elif game == 'gms':

            embed = discord.Embed(
                title='Các link hữu ích GMS:',
                description=f'Cú pháp: `{prefix}link gms`\n---',
                color=discord.Color.blue())

            embed.add_field(
                name='Tải Game',
                value=f'[Link Download](https://games.nexon.net/nexonlauncher)\n'
                'Tải xuống -> Cài Nexon Launcher -> Tìm tới MapleStory -> Download\n.')

            embed.add_field(
                name='Các link hướng dẫn',
                value=f'[Câu hỏi thường gặp](https://zblackwing.com/faq/)\n'
                '[Hướng dẫn game](https://zblackwing.com/) -> Menu **Hướng dẫn Game**\n'
                '[Update Notes Việt hóa](https://zblackwing.com/)\n.')
            embed.add_field(
                name='Các link hữu ích khác',
                value=f'[Tình trạng server](http://www.southperry.net/stat.php)\n'
                '[Mô phỏng hệ thống Cube](https://stripedypaper.github.io/cube/)\n'
                '[Orange Mushroom Blog - Update Notes KMS Anh hóa](https://orangemushroom.net/)')

            await self.util.say_as_embed(embed=embed)

        elif game == 'gmsm':

            embed = discord.Embed(
                title='Các link hữu ích GMSM:',
                description=f'Cú pháp: `{prefix}link gmsm`\n---',
                color=discord.Color.blue())

            embed.add_field(
                name='Tải Game',
                value=f'[Link Android](https://play.google.com/store/apps/details?id=com.nexon.maplem.global)\n'
                '[Link iOS](https://itunes.apple.com/au/app/maplestory-m/id1290086677)\n.')

            embed.add_field(
                name='Các link hướng dẫn',
                value=f'*Đang cập nhật*\n.')
            embed.add_field(
                name='Các link hữu ích khác',
                value=f'[Các câu hỏi xoay quanh Official Launch](https://www.facebook.com/zblackwing/posts/2055933801331800)\n')

            await self.util.say_as_embed(embed=embed)