FROM python:3.7-alpine

WORKDIR /usr/src/app

COPY requirements.txt .
RUN apk --no-cache add --virtual build postgresql-dev gcc python3-dev musl-dev \
    && pip install -r requirements.txt \
    && pip install psycopg2-binary \
    && apk del build \
    && apk --no-cache add postgresql-libs

COPY run.py .
COPY DiscordFeedBot/ ./DiscordFeedBot

CMD python3 ./run.py