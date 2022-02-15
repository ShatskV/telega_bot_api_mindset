"""Setup i18n middleware."""
from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware

from queiries import get_user_from_db

# from config import I18N_DOMAIN, LOCALES_DIR, default_lang
from config import settings


async def get_lang(user_id):
    """Get lang from DB."""
    user = await get_user_from_db(user_id)
    if user:
        return user.lang


class ACLMiddleware(I18nMiddleware):
    """Class 18n middleware."""

    async def get_user_locale(self, action, args):
        """Get locale."""
        user = types.User.get_current()
        return await get_lang(user.id) or user.locale or settings.default_lang


def setup_middleware(dp):
    """Middleware setup."""
    i18n = ACLMiddleware(settings.I18N_DOMAIN, settings.LOCALES_DIR)
    dp.middleware.setup(i18n)
    return i18n
