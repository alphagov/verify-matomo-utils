#!/usr/bin/env python
from retrieve_logs.fetch_missing_matomo_requests import get_logger, download_failed_requests
from datetime import datetime, timedelta
import time
import re
import boto3

DATE_FORMAT = '%d/%m/%y'
DATETIME_FORMAT = '%m/%d/%Y %H:%M:%S'
QUERY_STRING = """fields @message
    | filter @logStream like /matomo-nginx/
    | filter status >= 500
    | filter user_agent != 'ELB-HealthChecker/2.0'
    | filter path like /idsite=1/
    | filter path like /rec=1/
    """
RESULTS_LIMIT = 1
LOGGER = get_logger()

def get_date(prompt, start_date_to_compare=None):
    while True:
        try:
            date = datetime.strptime(input(prompt), DATE_FORMAT)
        except ValueError:
            print("Invalid date format - please enter a date as dd/mm/yy.")
            continue
        if date.date() > datetime.today().date():
            print("Invalid date - please enter a date in the past or today.")
            continue
        elif start_date_to_compare and date.date() < start_date_to_compare.date():
            print("Invalid date - please enter an end date the same or after the start date.")
        else:
            break
    return date

def query_limits(start_date, end_date, sort_order):
    return client.start_query(
        logGroupName = 'matomo',
        startTime=int(start_date.timestamp() * 1000),
        endTime=int((end_date + timedelta(1)).timestamp() * 1000),
        queryString=QUERY_STRING + f"| sort @timestamp {sort_order}",
        limit=RESULTS_LIMIT
    )['queryId']

def return_date_and_records_count_from_completed_query(query_id):
    status = ''
    while status != 'Complete':
        time.sleep(1)
        response = client.get_query_results(queryId=query_id)
        status = response['status']
    if not response['results']:
        LOGGER.error('No failed results found in date range. Check your dates and try again.')
        exit(1)
    elif len(response['results']) > 1:
        LOGGER.error('Too many results returned - this should not happen 😕')
        exit(1)

    return datetime.utcfromtimestamp(
        float(
            re.findall(
                r'msec": "(.+?)"', 
                [r['value'] for r in response['results'][0] if r['field'] == '@message'][0]
            )[0]
        )
    ), response['statistics']['recordsMatched']

start_date = get_date("\nWhat date did the failed requests begin (dd/mm/yy)?\n")
end_date = get_date("\nWhat date did the failed requests end (dd/mm/yy)?\n", start_date)

client = boto3.client('logs')
start_datetime, records_count = return_date_and_records_count_from_completed_query(query_limits(start_date, end_date, "asc"))
end_datetime, _ = return_date_and_records_count_from_completed_query(query_limits(start_date, end_date, "desc"))

while True:
    looks_good = input(f"\nThere were {int(records_count)} failed requests between {start_datetime.strftime(DATETIME_FORMAT)} and "
            f"{end_datetime.strftime(DATETIME_FORMAT)}.\nIs this correct? (yes/no)\n").lower()
    if looks_good not in ('yes', 'no'):
        print("Invalid input - please enter 'yes' or 'no'")
        continue
    elif looks_good == 'yes':
        break
    else:
        LOGGER.error("Aborting due to user input")
        exit(1)

LOGGER.info("Downloading failed requets from cloudwatch. This may take a few minutes...")
download_failed_requests(client, start_datetime - timedelta(seconds=1), end_datetime - timedelta(seconds=1))