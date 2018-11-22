import discord
from config import DEBUG


def get_channel(server=None, id=454890599410302977):
    """Return the given channel Object if in Production,
    # bot-test channel if in Development
    """
    if server is not None:
        if DEBUG is True:
            channel = server.get_channel(454890599410302977)
        else:
            channel = server.get_channel(id)
    else:
        if DEBUG is True:
            # bot-test channel
            channel = discord.Object(id=454890599410302977)
        else:
            # id-given channel
            channel = discord.Object(id=id)
    return channel
