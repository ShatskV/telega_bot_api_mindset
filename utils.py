from aiogram.types import message
import requests
import aiohttp
import settings
import os
import asyncio
import shutil
from requests.exceptions import (ConnectionError, HTTPError, Timeout)
from aiogram import types
from aiogram.dispatcher import FSMContext
def get_desc_and_tags(path_url=None, lang='en', url_method=False):
    path_url = 'https://cdn.motor1.com/images/mgl/3PMJX/s3/car-for-whole-life.webp'
    # url_method = True
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
    answer, uuid = make_desc_tags_answer(result, 'list')
    return answer, uuid

async def async_get_desc(path_url, lang, tags_format, url_method=False):
    if url_method:
        api_route = settings.url_api
        payload = {'json': {'imageUrl': path_url,
                    'lang': lang}}
        print(path_url)
    else:
        api_route = settings.file_api
        # payload = {'files': {'image_file': open(path_url, 'rb')},
        #             'data': {'lang': lang}}
        payload = {'data': {'image_file': open(path_url, 'rb'),
                    'lang': lang}}
    url = settings.url
    url = url + api_route
    timeout = aiohttp.ClientTimeout(connect=settings.ml_models_timeout[0],
                                    sock_read=settings.ml_models_timeout[1])
    async with aiohttp.ClientSession(timeout=timeout) as session:
        # try:
        # async with session.post(url, **payload) as resp:
        #     result = await resp.json()
        path_url = 'https://cdn.motor1.com/images/mgl/3pmjx/s3/car-for-whole-life.webp'
        async with session.post(url, json={'imageUrl': path_url,
                    'lang': lang}) as resp:
            result = await resp.json()
    # print(result)

    # try:
    #     response = requests.post(url, **payload, timeout=settings.ml_models_timeout)
    #     result = response.json()
            # except  (ConnectionError, HTTPError, Timeout):
            #     result = {'error': 'server unavailable'}
    answer, uuid = make_desc_tags_answer(result, tags_format)
    return answer, uuid

def set_result_rating(uuid, rating):
    # api_route = '/api/demo/description/rating'
    url = settings.url
    url = url + settings.rating_api
    payload = {'image_uuid': uuid,
                'rating': rating}
    try:
        response = requests.post(url, json=payload, timeout=settings.ml_models_timeout)
        result = response.json()
    except  (ConnectionError, HTTPError, Timeout):
        result = {'error': 'server unavailable'}
    # return result

async def async_set_rating(uuid, rating):
    url = settings.url
    url = url + settings.rating_api
    payload = {'image_uuid': uuid,
               'rating': rating}
    timeout = aiohttp.ClientTimeout(connect=settings.ml_models_timeout[0],
                                    sock_read=settings.ml_models_timeout[1])
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json=payload) as resp:
            result = await resp.json()
    return result


def make_desc_tags_answer(result, tags_format):
    answer = []
    print('------------------')
    print(result)
    print('------------------')

    if result.get('error'):
        answer.append('<b>Service unavailable!</b>')
        return answer, None
    answer.append('<b>Description:</b>')
    if result.get('description'):
        desc = result['description']
        answer.append(desc.capitalize())
    else: 
        answer.append('Service unavailable!')
    answer.append('<b>Tags:</b>')
    tags = result.get('tags')
    if tags:
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
        
        # for tag in result['tags']:
        #     i += 1
        #     tags += patern.format(tag['tag'])
        #     if i == num_tags-1:
        #         if tags_format == 'list':
        #             tags = tags[:-1]
        #             break
        #     if i % (tags_in_row - 1) == 0 and i != num_tags-1:
        #         tags += '\n'
        #         continue
        #     tags += ' '
        answer.append(answer_tags)
    else: 
        answer.append('Service unavailable!')
    print(answer)
    return answer, result['image_uuid']


async def form_file_path_url(msg: types.Message):
    if msg.text:
        return msg.text.lower(), True
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
    # silentremove('downloads')
    answer, uuid = get_desc_and_tags(url_method=True)
    print(answer)