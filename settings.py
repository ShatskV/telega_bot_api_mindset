import os
from dotenv import load_dotenv
load_dotenv()
url = 'http://app-staging.picpack.io:80'
ml_models_timeout = (2,7)
desc_api = '/api/demo/description/'
file_api = desc_api + 'file'
url_api = desc_api + 'url'
rating_api = desc_api + 'rating'
basedir = os.path.abspath(os.path.dirname(__file__))
# SQLALCHEMY_URI = 'sqlite:///' + os.path.join(basedir, 'telega.db')
SQLALCHEMY_URI = os.environ.get('SQLALCHEMY_URI')

langs=['en', 'ru']
tags_format = ['list', 'instagram']