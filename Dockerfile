FROM python:3.9.1-alpine

WORKDIR /app

COPY retrieve_logs/fetch_missing_matomo_requests.py retrieve_logs/
COPY retrieve_logs/requirements.txt retrieve_logs/
COPY retrieve_logs/__init__.py retrieve_logs/
COPY entrypoint.py .

RUN pip install --no-cache-dir -r retrieve_logs/requirements.txt

CMD [ "python", "-u", "entrypoint.py" ]

