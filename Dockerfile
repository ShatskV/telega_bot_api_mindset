FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# ENV APP_SETTINGS=init_config.DevelopmentConfig

WORKDIR /telegrambot_mindset

# RUN apt-get update && apt-get install -y netcat

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python3.9", "bot.py"]
