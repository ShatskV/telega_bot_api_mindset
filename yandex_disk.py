import logging
from pathlib import Path

from aiohttp.client_exceptions import ClientError
from yadisk_async import YaDisk
from yadisk_async.exceptions import UnauthorizedError, YaDiskError
from queiries import add_yandex_query

from config import settings


async def yandex_upload(tag, uuid, filename, token, message=None):
    ya_log = {}
    file_ext = Path(filename).suffix
    y = YaDisk(token=token)
    path = settings.YADISK_PATH
    tag_path = f'{path}/{tag}'
    file_path = f'{tag_path}/{uuid}{file_ext}'
    ya_log['file_path'] = file_path
    ya_log['token'] = token
    try:
        if not await y.exists(tag_path):
            if not await y.exists(path):
                await y.mkdir(path)
            await y.mkdir(tag_path)
        await y.upload(filename, file_path)
    except ClientError as e:
        err_text = f'Aiohhtp error!:\n{e}'
        ya_log['error'] = err_text
        logging.error(err_text, exc_info=True)
        return None
    except UnauthorizedError as e:
        err_text = f'Ya_disk auth error!:\n{e}'
        ya_log['error'] = err_text
        logging.error(err_text)
        return 'bad_token'
    except YaDiskError as e:
        err_text = f'Ya_disk error!:\n{e}'
        ya_log['error'] = err_text
        logging.error(err_text)
        return False
    finally:
        await y.close()
        await add_yandex_query(ya_log=ya_log, message=message)
    return True


async def yandex_check(token, message=None):
    ya_log = {}
    y = YaDisk(token=token)
    ya_log['token'] = token
    try:
        valid_token = await y.check_token()
    except ClientError as e:
        err_text = f'Aiohhtp error!:\n{e}'
        ya_log['error'] = err_text
        logging.error(err_text, exc_info=True)
        return None
    except YaDiskError as e:
        err_text = f'Ya_disk error!:\n{e}'
        ya_log['error'] = err_text
        logging.error(err_text)
        return False
    finally:
        await y.close()
        await add_yandex_query(ya_log=ya_log, message=message)
    return valid_token
