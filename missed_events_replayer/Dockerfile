ARG base_image=python:3.9.1-alpine
FROM ${base_image}

WORKDIR /app

RUN apk add --no-cache python2 git jq

RUN git clone --depth=1 https://github.com/alphagov/matomo-log-analytics.git log-analytics

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY missed_events_replayer missed_events_replayer

ENTRYPOINT [ "python", "-u", "missed_events_replayer/missed_events_replayer.py" ]

