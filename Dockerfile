FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_METHOD=polling
WORKDIR /telegrambot_mindset

COPY requirements.txt .

RUN apt-get update

RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt

COPY . .

# RUN pybabel compile -d locales -D picpackbot
# RUN chmod +x ./*.sh
RUN ./run_bot.sh

# ENTRYPOINT ["python3.9", "bot_start.py"]
# ENTRYPOINT ["./run_bot.sh"]