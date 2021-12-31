from aiogram.types import message
import requests
from sqlalchemy.sql.expression import false, true
import settings
import os
import shutil
from requests.exceptions import (ConnectionError, HTTPError, Timeout)
from aiogram import types

def get_desc_and_tags(path_url, lang, url_method=False):
    # path_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRYtDnnrAGa7In3xr6oK_2ogSwyrphTVZhGCg&usqp=CAU"
    if url_method:
        api_route = settings.url_api
        payload = {'json': {'imageUrl': path_url,
                    'lang': lang}}
    else:
        api_route = settings.file_api
        payload = {'files': {'image_file': open(path_url, 'rb')},
                    'data': {'lang': lang}}
    url = settings.url
    url = url + api_route
    try:
        response = requests.post(url, **payload, timeout=settings.ml_models_timeout)
        result = response.json()
    except  (ConnectionError, HTTPError, Timeout):
        result = {'error': 'server unavailable'}
    answer, uuid = make_desc_tags_answer(result)
    return answer, uuid


def set_result_rating(uuid, rating):
    api_route = '/api/demo/description/rating'
    url = settings.url
    url = url + api_route
    payload = {'image_uuid': uuid,
                'rating': rating}
    try:
        response = requests.post(url, json=payload, timeout=settings.ml_models_timeout)
        result = response.json()
    except  (ConnectionError, HTTPError, Timeout):
        result = {'error': 'server unavailable'}
    return result
    

def make_desc_tags_answer(result):
    if result.get('error'):
        return 'Сервисы недоступны!', None
    answer = 'description: '
    if result.get('description'):
        answer += f"{result.get('description')}\n"
    else: 
        answer += 'Cервис недоступен!\n'
    answer += 'tags:\n'
    if result.get('tags'):
        for tag in result['tags']:
            if tag['confidence'] > 0.2:
                answer += f"{tag['tag']}: {tag['confidence']}\n" 
    else: 
        answer += 'Сервис недоступен!'
    return answer, result['image_uuid']


async def form_file_path_url(msg: types.Message):
    if msg.text:
        return msg.text.lower(), True
    user_path = f'downloads/{msg.from_user.id}'
    os.makedirs(user_path, exist_ok=True)
    if hasattr(msg, 'document') and msg.document is not None:
        print(msg)
        file_name = os.path.join(user_path,
                                 f"{msg.document.file_unique_id}.{msg.document.mime_type.split('/')[1]}")
        await msg.document.download(file_name)
    else: 
        file_name = os.path.join(user_path, f'{msg.photo[-1].file_id}.jpg')
        await msg.photo[-1].download(file_name)
    return file_name, False
    

def silentremove(path):
    shutil.rmtree(path, ignore_errors=True)
    

if __name__ == '__main__':
    silentremove('downloads')