from decouple import config
import os


DEBUG = config('DEBUG', default=False, cast=bool)
BOT_TOKEN = config('BOT_TOKEN')
MY_ID = config('MY_ID', cast=str)
SERVER_ID = config('SERVER_ID', cast=str)

# Twitter stuff
TWITTER_CONSUMER_KEY = config('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = config('TWITTER_CONSUMER_SECRET')

TWITTER_OWNER = config('TWITTER_OWNER')
TWITTER_OWNER_ID = config('TWITTER_OWNER_ID')

TWITTER_ACCESS_TOKEN = config('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = config('TWITTER_ACCESS_TOKEN_SECRET')

FACEBOOK_ACCESS_TOKEN = config('FACEBOOK_TEST_ACCESS_TOKEN')

# francis/config.py -> francis
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
