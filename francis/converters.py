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
            return role
        except commands.BadArgument:
            raise commands.BadArgument(f'`{parsed_role_name}` role not found.')
