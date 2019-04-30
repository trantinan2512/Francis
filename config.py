from decouple import config, Csv
import os

DEBUG = config('DEBUG', default=False, cast=bool)
FRANCIS_TOKEN = config('FRANCIS_TOKEN')
OZ_TOKEN = config('OZ_TOKEN')
MY_ID = config('MY_ID', cast=int)
SERVER_ID = config('SERVER_ID', cast=int)

# Twitter stuff
TWITTER_CONSUMER_KEY = config('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = config('TWITTER_CONSUMER_SECRET')

TWITTER_OWNER = config('TWITTER_OWNER')
TWITTER_OWNER_ID = config('TWITTER_OWNER_ID')

TWITTER_ACCESS_TOKEN = config('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = config('TWITTER_ACCESS_TOKEN_SECRET')

FACEBOOK_ACCESS_TOKEN = config('FACEBOOK_TEST_ACCESS_TOKEN')

# msvn_discordbot/config.py -> msvn_discordbot
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# GOOGLE API AUTH
GAPI_AUTH_DICT = {
    "type": config('GAPI_TYPE'),
    "project_id": config('GAPI_PROJECT_ID'),
    "private_key_id": config('GAPI_PRIVATE_KEY_ID'),
    "private_key": config('GAPI_PRIVATE_KEY').replace('\\n', '\n'),
    "client_email": config('GAPI_CLIENT_EMAIL'),
    "client_id": config('GAPI_CLIENT_ID'),
    "auth_uri": config('GAPI_AUTH_URI'),
    "token_uri": config('GAPI_TOKEN_URI'),
    "auth_provider_x509_cert_url": config('GAPI_AUTH_PROVIDER_X509_CERT_URL'),
    "client_x509_cert_url": config('GAPI_CLIENT_X509_CERT_URL'),
}

AUTOASIGN_COLOR_ROLES = [
    'Anchor',
    'Apricot',
    'Black',
    'Canary',
    'Cardinal',
    'Carrot',
    'Chateau',
    'Fire',
    'Forest',
    'Green',
    'Lilac',
    'Maroon',
    'Mint',
    'Ocean',
    'Pink',
    'Prussian',
    'Ruby',
    'Slate',
    'Steel',
    'Tawny',
    'Teal',
    'Violet',
]

AUTOASIGN_CHANNEL_ROLES = [
    'GMS',
    'GMSM',
    'GMS2',
    'THMS',
    'KMS',
    'KMS2',
    'KMSM',

]

AUTOASIGN_NOTIFY_ROLES = [
    'Notify GMS',
    'Notify GMSM'
]

AUTOASIGN_DAWN_NOTIFY_ROLES = [
    'Event Notify',
]

AUTOASIGN_DAWN_EVENT_ROLES = [
    'Investigator',
]

AUTOASIGN_JOB_ROLES = [
    'Hero', 'Dark Knight', 'Paladin',
    'Bowmaster', 'Marksman',
    'Arch Mage IL', 'Arch Mage FP', 'Bishop',
    'Night Lord', 'Shadower', 'Dual Blade',
    'Buccaneer', 'Corsair', 'Cannoneer', 'Jett',
    'Dawn Warrior', 'Wind Archer', 'Blaze Wizard', 'Night Walker', 'Thunder Breaker', 'Mihile',
    'Mercedes', 'Aran', 'Phantom', 'Luminous', 'Evan', 'Shade',
    'Battle Mage', 'Wild Hunter', 'Mechanic', 'Blaster', 'Xenon',
    'Demon Slayer', 'Demon Avenger',
    'Kaiser', 'Angelic Buster', 'Cadena',
    'Hayato', 'Kanna',
    'Illium', 'Ark',
    'Beast Tamer', 'Kinesis', 'Zero', 'Pink Bean',
    'Beginner', 'Citizen',
]

AUTOASIGN_ROLES = AUTOASIGN_COLOR_ROLES + AUTOASIGN_CHANNEL_ROLES + AUTOASIGN_JOB_ROLES
AUTOASIGN_ROLES += AUTOASIGN_NOTIFY_ROLES + AUTOASIGN_DAWN_NOTIFY_ROLES + AUTOASIGN_DAWN_EVENT_ROLES

DAWN_SERVER_ID = 364323564737789953
MSVN_SERVER_ID = 453555802670759947

REACT_FOR_ROLE_MESSAGE_ID = 472966572340674560
REACT_FOR_NOTIFICATION_ROLE_MESSAGE_ID = 472967231781863427

DAWN_REACT_FOR_ROLE_MESSAGE_ID = config('DAWN_REACT_FOR_ROLE_MESSAGE_ID', cast=int, default=557788422379667457)
DAWN_REACT_FOR_ROLE_EMOJI_IDS = config('DAWN_REACT_FOR_ROLE_EMOJI_IDS', cast=Csv())
DAWN_REACT_FOR_ROLE_ROLE_IDS = config('DAWN_REACT_FOR_ROLE_ROLE_IDS', cast=Csv())

DAWN_COLOR_CHANGE_ROLE_IDS = config('DAWN_COLOR_CHANGE_ROLE_IDS', cast=Csv(int))

EMBED_DEFAULT_COLOR = 0xf900e5
DISCORD_ROLE_FOR_INVESTIGATION = config('DISCORD_ROLE_FOR_INVESTIGATION', default='Investigator')

SPIDER_DELAY = config('SPIDER_DELAY', default=30, cast=int)
