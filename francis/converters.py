from discord.ext import commands
import config

role_converter = commands.RoleConverter()


class CustomRoleConverter(commands.Converter):
    async def convert(self, context, argument):

        role_words = argument.lower().lstrip('@').split(' ')
        parsed_role_words = []
        for word in role_words:
            if word in ['gms', 'kms', 'gmsm', 'thms', 'kmsm', 'gms2', 'kms2', 'il', 'fp']:
                parsed_role_words.append(word.upper())
            else:
                parsed_role_words.append(word.capitalize())

        parsed_role_name = ' '.join(parsed_role_words)
        try:
            role = await role_converter.convert(context, parsed_role_name)
            if role.name not in config.AUTOASIGN_ROLES and role.id not in config.AUTOASIGN_ROLES:
                raise commands.BadArgument(
                    f'{role.mention} is not assignable. '
                    f'Please use `{context.prefix}roles` to see a full list of assignable roles.')
            return role
        except commands.BadArgument:
            raise commands.BadArgument(f'`{parsed_role_name}` role not found.')


class GameCodeConverter(commands.Converter):
    code_to_game = {
        'hi3': 'Honkai Impact 3rd'
    }

    async def convert(self, context, argument):
        _argument = argument.lower()
        if _argument in self.code_to_game:
            return self.code_to_game[_argument]
        else:
            iter_ = [f"{key:<5} : {value}\n" for key, value in self.code_to_game.items()]
            raise commands.BadArgument(
                f'`{argument}` is not a valid game code. Allowed game codes:'
                f'```\n'
                f'{"".join(iter_)}'
                f'```')
