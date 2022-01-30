from email.policy import default
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram import types
from settings import I18N_DOMAIN, LOCALES_DIR
from settings import default_lang
from queiries import get_user_from_db


async def get_lang(user_id):
    user = await get_user_from_db(user_id)
    if user:
        return user.lang


class ACLMiddleware(I18nMiddleware):
    async def get_user_locale(self, action, args):
        user = types.User.get_current()
        return await get_lang(user.id) or user.locale or default_lang


def setup_middleware(dp):
    i18n = ACLMiddleware(I18N_DOMAIN, LOCALES_DIR)
    dp.middleware.setup(i18n)
    return i18n