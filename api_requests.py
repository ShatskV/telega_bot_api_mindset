import logging
from typing import Union

import aiohttp
from aiogram import types
from aiohttp.client_exceptions import ClientError

from bot_init import _
from config import settings
from queiries import add_api_history


async def async_get_desc(path_url, lang, url_method=False, exc_true=None, msg=None):
    """Select method and get resquest from API."""
    if url_method:
        api_route = settings.url_api
        payload = {'json': {'imageUrl': path_url,
                            'lang': lang}}
    else:
        api_route = settings.file_api
        payload = {'exc_true': exc_true,  # exc_true - raise exc or not
                   'data': {'image_file': open(path_url, 'rb'),
                            'lang': lang}}
    url = settings.url
    url = url + api_route
    result = await async_get_request(url=url, msg=msg, **payload)
    # answer, uuid = make_desc_tags_answer(result, tags_format)
    return result


async def async_set_rating(uuid, rating, msg: Union[types.Message, types.CallbackQuery] = None):
    """Set rating for image by uuid."""
    url = settings.url
    api = settings.rating_api
    url = url + api
    payload = {'exc_true': False,
               'json': {'image_uuid': uuid,
                        'rating': rating}}
    result = await async_get_request(url, msg, **payload)
    if result.get('error'):
        logging.error(f'API rating return err: {result}')


async def async_get_request(url, msg=None, exc_true=True, **payload):
    timeout = aiohttp.ClientTimeout(connect=settings.ml_models_timeout[0],
                                    sock_read=settings.ml_models_timeout[1])
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=settings.USER_AGENT, **payload) as resp:
                result = await resp.json()
    except (ClientError, ValueError) as e:
        result = {'error': 'connection problem!'}
        if not exc_true:
            logging.critical(f'API rating error: {e}')
            return result
        else:
            raise e
    finally:
        await session.close()
        await add_api_history(msg=msg, url=url, payload=payload, result=result)
    return result
