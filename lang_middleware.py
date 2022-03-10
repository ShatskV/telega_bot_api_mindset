"""Setup i18n middleware."""
from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware

from queiries import get_user_from_db, get_group_from_db

# from config import I18N_DOMAIN, LOCALES_DIR, default_lang
from config import settings


async def get_lang(item_id):
    """Get lang from DB."""
    if item_id > 0:
        item = await get_user_from_db(item_id)
    else:
        item = await get_group_from_db(item_id)
    if item:
        return item.lang


class ACLMiddleware(I18nMiddleware):
    """Class 18n middleware."""

    async def get_user_locale(self, action, args):
        """Get locale."""
        user = types.User.get_current()
        chat = types.Chat.get_current()
        if not chat or not user:
            return settings.default_lang
        return await get_lang(chat.id) or user.locale or settings.default_lang


def setup_middleware(dp):
    """Middleware setup."""
    i18n = ACLMiddleware(settings.I18N_DOMAIN, settings.LOCALES_DIR)
    dp.middleware.setup(i18n)
    return i18n
