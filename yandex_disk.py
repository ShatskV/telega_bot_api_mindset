import asyncio
import logging
from pathlib import Path

from aiohttp.client_exceptions import ClientError
from yadisk_async import YaDisk
from yadisk_async.exceptions import UnauthorizedError, YaDiskError

from config import settings


async def yandex_upload(tag, uuid, filename, token):
    file_ext = Path(filename).suffix
    y = YaDisk(token=token)
    path = settings.YADISK_PATH
    tag_path = f'{path}/{tag}'
    file_path = f'{tag_path}/{uuid}{file_ext}'
    try:
        if not await y.exists(tag_path):
            if not await y.exists(path):
                await y.mkdir(path)
            await y.mkdir(tag_path)
        await y.upload(filename, file_path)
    except ClientError as e:
        logging.error(f'Aiohhtp error!:\n{e}', exc_info=True)
        return None
    except UnauthorizedError as e:
        logging.error(f'Ya_disk auth error!:\n{e}')
        return 'bad_token'
    except YaDiskError as e:
        logging.error(f'Ya_disk error!:\n{e}')
        return False
    finally:
        await y.close()
    return True


async def yandex_check(token):
    y = YaDisk(token=token)
    try:
        valid_token = await y.check_token()
    except ClientError as e:
        logging.error(f'Aiohhtp error!:\n{e}', exc_info=True)
        return None
    except YaDiskError as e:
        logging.error(f'Ya_disk error!:\n{e}')
        return False
    finally:
        await y.close()
    return valid_token
