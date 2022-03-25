# telegram_bot_mindset

**Telegram bot Picpack**

Телеграм бот генерирует описание и теги для картинки, также загружает картинки на Яндекс.диск

## Запуск бота:
- Получить Токен через BotFather
- Создать файл .env из env.example, поменять переменные окружения и версию миграции

## Запустить через docker:
- prod: 
    ```
    docker-compose -f docker-compose.prod.yml up --build
    ```
- dev: 
    ```
    docker-compose -f docker-compose.prod.yml up --build
    ```
- prod использует метод webhook, dev - polling

## Запустить локально:
- Обновить миграции для локальной базы
- Добавить в .env `APP_METHOD=dev` или `APP_METHOD=prod`
- Запустить бот через run_bot.sh

### В папке docs содержится инструкция по переводам бота и миграциям



