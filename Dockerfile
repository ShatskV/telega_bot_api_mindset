FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_METHOD=webhook
WORKDIR /telegrambot_mindset

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt
COPY . .

ENTRYPOINT ["python3.9", "bot_start.py"]
