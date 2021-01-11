FROM python:3.9.1-alpine

WORKDIR /app

RUN apk add --no-cache python2 git

RUN git clone --depth=1 https://github.com/adityapahuja/matomo-log-analytics.git log-analytics

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY missed_events_replayer missed_events_replayer

ENTRYPOINT [ "python", "-u", "missed_events_replayer/missed_events_replayer.py" ]

