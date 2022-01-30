import aiohttp
import settings
import os
import logging
import shutil
from aiogram import types
from aiohttp.client_exceptions import ClientError

async def async_get_desc(path_url=None, lang='en', tags_format='list', url_method=False):
    if url_method:
        api_route = settings.url_api
        payload = {'json': {'imageUrl': path_url,
                    'lang': lang}}
    else:
        api_route = settings.file_api
        payload = {'data': {'image_file': open(path_url, 'rb'),
                    'lang': lang}}
    url = settings.url
    url = url + api_route
    timeout = aiohttp.ClientTimeout(connect=settings.ml_models_timeout[0],
                                    sock_read=settings.ml_models_timeout[1])
    try:                               
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, **payload) as resp:
                result = await resp.json()
    except ClientError as e:
        logging.exception(f'ClienError: {e}')
        result = {'error': 'ClientError'}
    answer, uuid = make_desc_tags_answer(result, tags_format)
    return answer, uuid


async def async_set_rating(uuid, rating):
    url = settings.url
    url = url + settings.rating_api
    payload = {'image_uuid': uuid,
               'rating': rating}
    timeout = aiohttp.ClientTimeout(connect=settings.ml_models_timeout[0],
                                    sock_read=settings.ml_models_timeout[1])
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as resp:
                result = await resp.json()
    except ClientError as e:
        logging.exception(f'ClienError: {e}')
        result = {'error': 'ClientError'}
    return result


def make_desc_tags_answer(result, tags_format):
    answer = []
    if result.get('error'):
        if result['error'] == 'INVALID_URL':
            error = '<b>Invalid photo url!<b>'
        else:
            error = '<b>Service unavailable!</b>'
        answer.append(error)
        return answer, None
    answer.append('<b>Description:</b>')
    if result.get('description'):
        desc = result['description']
        answer.append(desc.capitalize())
    else: 
        answer.append('Service unavailable!')
    answer.append('<b>Tags:</b>')
    tags = result.get('tags')
    if tags and len(tags) > 0:
        i = 0
        answer_tags = ''
        num_tags = len(tags)

        if tags_format == 'list':
            patern = '{},'
        else:
            patern = '#{}'

        for tag in tags:
            i += 1
            answer_tags += patern.format(tag['tag'])
            if i == num_tags:
                if tags_format == 'list':
                    answer_tags = answer_tags[:-1]
                    break
            answer_tags += ' '
        answer.append(answer_tags)
    elif len(tags) == 0:
        answer.append('Sorry, tags not found!')
    else: 
        answer.append('Service unavailable!')
    return answer, result['image_uuid']


async def form_file_path_url(msg: types.Message):
    if msg.text:
        return msg.text, True
    user_path = f'downloads/{msg.from_user.id}'
    os.makedirs(user_path, exist_ok=True)
    if hasattr(msg, 'document') and msg.document is not None:
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