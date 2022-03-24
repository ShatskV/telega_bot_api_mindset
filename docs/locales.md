# Переводы для picpackbot

Запускаем первый раз:
1. Вытаскиваем тексты из файлов (он сам находит из функции _(...))
pybabel extract . -o locales/picpackbot.pot
2. Создаем папку для перевода на английский
pybabel init -i locales/picpackbot.pot -d locales -D picpackbot -l en
3. То же, на русский
pybabel init -i locales/picpackbot.pot -d locales -D picpackbot -l ru
4. Переводим, переводы соберутся сами при старте

Обновляем переводы:
1. Вытаскиваем тексты из файлов, Добавляем текст в переведенные версии
pybabel extract . -o locales/picpackbot.pot
pybabel update -d locales -D picpackbot -i locales/picpackbot.pot
3. Вручную делаем переводы, они при старте бота соберутся сами