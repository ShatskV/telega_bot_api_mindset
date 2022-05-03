from typing import Union
from aiogram.types import Message, CallbackQuery
from config import settings
from db import TgChatHistory, TypeUpdate, TgActionApi


def create_cls_history(msg: Union[CallbackQuery, Message]) -> TgChatHistory:
    """Create class TgChatHistory for db."""
    if isinstance(msg, CallbackQuery):
        callback_data = msg.data
        type_update = TypeUpdate.callback
        msg = msg.message
    else:
        type_update = TypeUpdate.message
        callback_data = None
    # content_type = msg.content_type
    content_type = getattr(msg, 'content_type', None)
    date_msg = msg.date
    from_bot = True if str(msg.from_user.id) == settings.BOT_ID else False
    mime_type = getattr(content_type, 'mime_type', None)

    if (content_type == 'photo') or (mime_type and ('image' in mime_type)):
        is_image = True
    else:
        is_image = False

    cls_history = TgChatHistory(tg_msg_id=msg.message_id,
                                tg_user_id=msg.from_user.id,
                                tg_chat_id=msg.chat.id,
                                type_update=type_update,
                                text=getattr(msg, 'text', None),
                                callback_data=callback_data,
                                from_bot=from_bot,
                                is_image=is_image,
                                file_id=getattr(content_type, 'file_id', None),
                                caption=getattr(msg, 'caption', None),
                                content_type=content_type,
                                mime_type=mime_type,
                                create_at=date_msg)
    return cls_history


def create_api_history(msg: Union[CallbackQuery, Message], url, payload, result) -> TgActionApi:
    if isinstance(msg, CallbackQuery):
        msg = msg.message
    image_uuid = result.get('image_uuid') or payload.get('json', {}).get('image_uuid')
    is_success = False if result.get('error', False) else True
    imageurl = payload.get('json', {}).get('imageUrl')
    rating = payload.get('json', {}).get('rating')
    add_info = {'imageUrl': imageurl} if imageurl else {}
    if rating:
        add_info['rating'] = rating
    add_info = None if add_info == {} else str(add_info)
    lang = payload.get('json', {}).get('lang') or payload.get('data', {}).get('lang')
    cls_api = TgActionApi(tg_user_id=msg.from_user.id,
                          tg_chat_id=msg.chat.id,
                          tg_msg_id=msg.message_id,
                          api_url=url,
                          image_uuid=image_uuid,
                          is_success=is_success,
                          lang=lang,
                          response=str(result) if result is not None else None,
                          add_info=add_info)
    return cls_api
