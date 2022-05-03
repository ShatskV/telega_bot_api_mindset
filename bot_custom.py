import typing

from aiogram import Bot, types
from aiogram.types import base
from aiogram.dispatcher.middlewares import BaseMiddleware

from history_utils import create_cls_history
from queiries import add_object_to_db, update_message


class MyBot(Bot):
    async def send_message(self,
                           chat_id: typing.Union[base.Integer, base.String],
                           text: base.String,
                           parse_mode: typing.Optional[base.String] = None,
                           entities: typing.Optional[typing.List[types.MessageEntity]] = None,
                           disable_web_page_preview: typing.Optional[base.Boolean] = None,
                           disable_notification: typing.Optional[base.Boolean] = None,
                           reply_to_message_id: typing.Optional[base.Integer] = None,
                           allow_sending_without_reply: typing.Optional[base.Boolean] = None,
                           reply_markup: typing.Union[types.InlineKeyboardMarkup,
                                                      types.ReplyKeyboardMarkup,
                                                      types.ReplyKeyboardRemove,
                                                      types.ForceReply, None] = None) -> types.Message:
        message = await super().send_message(chat_id, text, parse_mode, entities, disable_web_page_preview,
                                             disable_notification, reply_to_message_id, allow_sending_without_reply,
                                             reply_markup)

        await add_object_to_db(create_cls_history(message))
        return message

    async def delete_message(self, chat_id: typing.Union[base.Integer, base.String],
                             message_id: base.Integer) -> base.Boolean:
        await update_message(message_id=message_id, is_delete=True)
        return await super().delete_message(chat_id, message_id)

    async def edit_message_text(self, text: base.String, chat_id: typing.Union[base.Integer, base.String, None] = None,
                                message_id: typing.Optional[base.Integer] = None,
                                inline_message_id: typing.Optional[base.String] = None,
                                parse_mode: typing.Optional[base.String] = None,
                                entities: typing.Optional[typing.List[types.MessageEntity]] = None,
                                disable_web_page_preview: typing.Optional[base.Boolean] = None,
                                reply_markup: typing.Union[types.InlineKeyboardMarkup, None] = None) -> types.Message or base.Boolean:
        if message_id is not None:
            await update_message(message_id=message_id, text=text, bot_message_edit=True)
        return await super().edit_message_text(text, chat_id, message_id, inline_message_id, parse_mode, entities,
                                               disable_web_page_preview, reply_markup)


class SaveToDb(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict) -> None:
        await add_object_to_db(create_cls_history(message))

    async def on_process_callback_query(self, callback_query: types.CallbackQuery, data: dict) -> None:
        await add_object_to_db(create_cls_history(callback_query))
