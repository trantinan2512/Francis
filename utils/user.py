from web.apps.users.models import DiscordUser


def get_user_obj(discord_user):
    user_obj, created = DiscordUser.objects.update_or_create(
        discord_id=discord_user.id,
        defaults={
            'discord_name': discord_user.display_name
        }
    )
    return user_obj
