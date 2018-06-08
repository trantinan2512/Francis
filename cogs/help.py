from discord.ext import commands
import discord


class Help:
    """A cog for Help management commands"""

    def __init__(self, bot, util):
        self.bot = bot
        self.util = util

    @commands.command(pass_context=True)
    async def help(self, context, category=None):
        """Trợ giúp về sử dụng bot"""

        if category:
            category = category.lower()

        prefix = self.bot.command_prefix
        server = context.message.server

        gms_role = discord.utils.get(server.roles, name='GMS')
        gmsm_role = discord.utils.get(server.roles, name='GMSM')

        if category is None:
            embed = discord.Embed(
                title=None,
                description=None,
                color=discord.Color.teal())

            embed.add_field(
                name='Các lệnh về Role có thể tự Thêm/Xóa.',
                value=f'`{prefix}help role`')
            embed.add_field(
                name='Thông tin về Role @Guild Leader.',
                value=f'`{prefix}help leader`')
            embed.add_field(
                name='Thông tin về Role @Trader.',
                value=f'`{prefix}help trader`')
            embed.add_field(
                name='Thông tin về Role @Content Creator.',
                value=f'`{prefix}help creator`\n*Đang thi công*')
            embed.add_field(
                name='Các Link hữu ích.',
                value=f'`{prefix}help link`\n*Đang thi công*')
            embed.add_field(
                name='Các lệnh của Music Bot.',
                value=f'`{prefix}help music`\n*Đang thi công*')

            await self.util.say_as_embed(embed=embed)

        elif category == 'role':

            # role_request_channel = discord.utils.get(context.message.server.channels, name='yêu-cầu-role')

            embed = discord.Embed(
                title='Danh sách lệnh liên quan đến Role có thể tự Thêm/Xóa',
                description=f'Sử dụng `{prefix}role` hoặc `{prefix}rrole` để biết thêm chi tiết.\n'
                f'Đối với các Role không thể tự thêm/xóa, sử dụng lệnh `{prefix}help` để được hướng dẫn\n---',
                color=discord.Color.magenta())

            embed.add_field(
                name='Thêm role.',
                value=f'`{prefix}role tên_role`')
            embed.add_field(
                name='Xóa Role.',
                value=f'`{prefix}rrole tên_role`')
            embed.add_field(
                name='Xóa Role theo loại.',
                value=f'`{prefix}rrole all loại_role`')
            embed.add_field(
                name='Danh sách Role.',
                value=f'`{prefix}list`')

            await self.util.say_as_embed(embed=embed)

        elif category.startswith('lead'):

            leader_role = discord.utils.get(server.roles, name='Guild Leader')

            guild_recruit_gms = discord.utils.get(server.channels, name='tuyển-mem-guild-gms')
            guild_recruit_gmsm = discord.utils.get(server.channels, name='tuyển-mem-guild-gms-m')

            embed = discord.Embed(
                title='1. Thông tin về Role @Guild Leader',
                description=f'Khi có role {leader_role.mention}, bạn sẽ có thể đăng thông tin về Guild mình để chiêu mộ '
                f'thành viên vào Guild tại {guild_recruit_gms.mention} và {guild_recruit_gmsm.mention} '
                f'(cần có role {gms_role.mention} và {gmsm_role.mention}).\n.',
                color=discord.Color.blue())

            embed.add_field(
                name='2. Format đăng bài tuyển thành viên',
                value='```'
                'Tên Guild: \n'
                'Server: \n'
                'Tên In-game chủ Guild/phó Guild: \n'
                'Đặc điểm Guild: Vui vẻ hòa đồng / Đi boss hàng ngày / Chém gió bựa nhân / Cày cuốc leo top / ...\n'
                'Mục tiêu của Guild: \n'
                'Yêu cầu ứng viên: \n'
                'Số lượng tuyển: \n'
                '```.')
            embed.add_field(
                name='3. Nội quy của kênh tuyển thành viên',
                value=''
                '▬ Chỉ đăng bài với format như trên.\n'
                '▬ Chỉ đăng **1 bài duy nhất** (nếu đăng lại phải xóa bài trước đó).\n'
                '▬ Mỗi lần đăng bài cách nhau tối thiểu **1 giờ**.\n'
                '▬ Có thể sửa hoặc xóa bài tuyển thành viên.\n'
                '▬ Nếu muốn vào Guild, bạn có thể inbox trực tiếp đại diện Guild.\n'
                '▬ Việc quản lý Guild tùy thuộc vào Guild.'
            )

            await self.util.say_as_embed(embed=embed)
        elif category.startswith('trade'):

            trader_role = discord.utils.get(server.roles, name='Trader')
            trade_warning_role = discord.utils.get(server.roles, name='Trade Warning')
            admin_role = discord.utils.get(server.roles, name='Admin')
            super_mod_role = discord.utils.get(server.roles, name='Super Mod')

            trade_gms = discord.utils.get(server.channels, name='mua-bán-gms')
            trade_gmsm = discord.utils.get(server.channels, name='mua-bán-gms-m')

            embed = discord.Embed(
                title='1. Thông tin về Role @Trader',
                description=f'Khi có role {trader_role.mention}, bạn sẽ có thể đăng bài mua bán, giao dịch trong các kênh '
                f'{trade_gms.mention} và {trade_gmsm.mention} '
                f'(cần có role {gms_role.mention} và {gmsm_role.mention}).\n.',
                color=discord.Color.dark_green())

            embed.add_field(
                name='2. Format đăng bài mua bán',
                value=''
                '```B>  [Tên_món_đồ] [Giá]```'
                'B = Buy = Mua\n'
                '```S>  [Tên_món_đồ] [Giá]```'
                'S = Sell = Bán\n'
                '```T>  Có [Tên_món_đồ_đang_sở_hữu] muốn đổi lấy [Tên_món_đồ_muốn_đổi]```'
                'T = Trade = Trao đổi\n'
                '```GA> [Tên_món_đồ]```'
                'GA = Give Away = Cho không (việc lựa chọn người nhận hoàn toàn do người đăng quyết định)\n\n'
                '*Có thể dùng **tối đa 2 hình ảnh** để mô tả món đồ.\n.')
            embed.add_field(
                name='3. Mặt hàng và quy định',
                value=''
                '▬ Tất cả vật phẩm, mesos trong game đều có thể giao dịch.\n'
                '▬ Cẩn trọng với vật phẩm, mesos kiếm được từ hoạt động bất chính (hack, bot).\n'
                '▬ **Không** mua bán lấy hiện kim/tiền mặt.\n'
                '▬ Giao dịch được thực hiện hoàn toàn trong game. Đàm phán ở kênh mà bạn cho là tiện nhất.\n.'
            )
            embed.add_field(
                name='4. Nội quy kênh mua bán',
                value=''
                '▬ Chỉ đăng bài với các format như trên.\n'
                '▬ Mỗi lần đăng bài cách nhau tối thiểu **1 giờ**.\n'
                '▬ **Không** mua bán lấy hiện kim/tiền mặt.\n'
                '▬ Có thể sửa hoặc xóa bài.\n'
                '▬ **Không xin xỏ**. Chỉ đăng bài nếu bạn có nhu cầu mua bán, trao đổi, hay cho không.\n'
                '▬ Liên hệ inbox người đăng bài để đàm phán giao dịch.\n'
                f'▬ Kiểm tra xem người đăng bài có role {trader_role.mention} trước khi giao dịch.\n'
                f'▬ **Tuyệt đối không giao dịch** với người có role {trade_warning_role.mention}'
                '- người đã có tiền sử lừa đảo bị phát hiện trong group.\n.'
            )
            embed.add_field(
                name='5. Xử trí khi bị lừa đảo, báo cáo lừa đảo',
                value=''
                '▬ Nếu bị lừa đảo, cảm giác mình đang nói chuyện với lừa đảo, hãy inbox trực tiếp cho'
                f'{admin_role.mention} hoặc {super_mod_role.mention}.\n'
                '▬ Kể rõ vụ việc xảy ra, kèm theo bằng chứng.\n'
                '▬ Các trường hợp **vu khống** sẽ chịu hậu quả.'
            )
            await self.util.say_as_embed(embed=embed)
