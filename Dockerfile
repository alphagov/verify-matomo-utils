FROM python:3.9.1-alpine

RUN apk add --no-cache python2 git

WORKDIR /app

RUN git clone --depth=1 https://github.com/adityapahuja/matomo-log-analytics.git log-analytics

COPY check_logs/*.py check_logs/
COPY retrieve_logs/*.py retrieve_logs/
COPY replay_events/*.py replay_events/
COPY archive_events/*.py archive_events/
COPY main.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD [ "python", "-u", "main.py" ]

