import config
import re


def process_role(role):
    """Process the role given by the user.
    Return None if no roles detected"""

    # strip the leading @ in case someone fucks up
    role = role.lstrip('@')

    tmp_cap = list()

    for w in role.split(' '):
        if w.lower() in ['fp', 'il', 'gms', 'gmsm']:
            tmp_cap.append(w.upper())
        else:
            tmp_cap.append(w.capitalize())

    capped_role = ' '.join(tmp_cap)

    if role in config.AUTOASIGN_ROLES:
        return role

    elif capped_role in config.AUTOASIGN_ROLES:
        return capped_role

    elif role.upper() in config.AUTOASIGN_ROLES:
        return role.upper()

    elif role.startswith('all'):
        # returns a tuple
        return 'all', role.lstrip('all').strip()

    else:
        return None


def is_image_url(argument):
    img_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.tiff')
    return argument.lower().startswith('http') and any(ext in argument.lower() for ext in img_extensions)


def is_hex_code(argument):
    hex_re = re.compile('^0x\w{6}$', re.IGNORECASE)
    if hex_re.match(argument):
        return True
    else:
        return False


def is_normal_message_type(argument):
    if argument == 'normal':
        return True
    else:
        return False
