"""Bot settings."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
url = os.environ.get('URL')
ml_models_timeout = (2, 7)
desc_api = '/api/demo/description/'
file_api = desc_api + 'file'
url_api = desc_api + 'url'
rating_api = desc_api + 'rating'
# basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_URI = os.environ.get('SQLALCHEMY_URI')

langs = ['en', 'ru']
default_lang = 'en'

I18N_DOMAIN = 'picpackbot'
BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / 'locales'

USER_AGENT = {'User-agent': 'picpack_telegram_bot'}

WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST')
WEBHOOK_PATH = os.environ.get('WEBHOOK_PATH')
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = os.environ.get('WEBAPP_HOST')
WEBAPP_PORT = os.environ.get('WEBAPP_PORT')
