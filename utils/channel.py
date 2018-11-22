from config import DEBUG


def get_channel(bot, id=454890599410302977):
    """Return the given channel Object if in Production,
    # bot-test channel if in Development
    """
    if DEBUG is True:
        # bot-test channel
        channel = bot.get_channel(id=454890599410302977)
    else:
        # id-given channel
        channel = bot.get_channel(id=id)
    return channel
