FROM python:3.9.1-alpine

RUN apk add --no-cache python2 git

WORKDIR /app

RUN git clone --depth=1 https://github.com/adityapahuja/matomo-log-analytics.git log-analytics

COPY missed_events_replayer missed_events_replayer
COPY requirements.txt .

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "-u", "missed_events_replayer/missed_events_replayer.py" ]

