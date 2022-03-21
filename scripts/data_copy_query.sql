INSERT INTO bot."RatingQuery" (message_id, image_uuid)
SELECT message_id, image_uuid
FROM public."RatingQuery";

INSERT INTO bot.tg_actions (
    id,
    tg_user_id,
    action_type,
    image_uuid,
    image_name,
    lang,
    image_type,
    image_size,
    create_at,
    responce
)
SELECT 
    id,
    tg_user_id,
    action_type::action::text::bot.action,
    image_uuid,
    image_name,
    lang,
    image_type,
    image_size,
    create_at,
    responce
FROM public.tg_actions;

INSERT INTO bot.tg_chat_history (
    id,
    tg_msg_id,
    tg_user_id,
    user_msg,
    bot_msg,
    bot_message_edit,
    create_at
)
SELECT
    id,
    tg_msg_id,
    tg_user_id,
    user_msg,
    bot_msg,
    bot_message_edit,
    create_at
FROM public.tg_chat_history;

INSERT INTO bot.tg_users (
    id,
    tg_user_id,
    user_id,
    tg_user_name,
    first_name,
    last_name,
    lang,
    tags_format,
    rating,
    free_act,
    create_at,
    bot_feedback,
    is_banned
)
SELECT 
    id,
    tg_user_id,
    user_id,
    tg_user_name,
    first_name,
    last_name,
    lang,
    tags_format::tagformat::text::bot.tagformat,
    rating,
    free_act,
    create_at,
    bot_feedback,
    is_banned
FROM public.tg_users;

SELECT setval('bot."RatingQuery_message_id_seq"', (SELECT last_value FROM public."RatingQuery_message_id_seq"), true);

SELECT setval('bot.tg_actions_id_seq', (SELECT last_value FROM public.tg_actions_id_seq), true);

SELECT setval('bot.tg_chat_history_id_seq', (SELECT last_value FROM public.tg_chat_history_id_seq), true);

SELECT setval('bot.tg_users_id_seq', (SELECT last_value FROM public.tg_users_id_seq), true);

