FROM python:3.9.1-alpine

WORKDIR /app

COPY retrieve_logs/*.py retrieve_logs/
COPY main.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "-u", "main.py" ]

