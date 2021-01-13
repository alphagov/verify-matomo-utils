import time
import re
from datetime import datetime, timedelta

from fetch_missing_matomo_requests import download_failed_requests
from helpers import get_date, confirm_or_abort, get_logger

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


def query_limits(client, start_date, end_date, sort_order):
    return client.start_query(
        logGroupName = 'matomo',
        startTime=int(start_date.timestamp() * 1000),
        endTime=int((end_date + timedelta(1)).timestamp() * 1000),
        queryString=QUERY_STRING + f"| sort @timestamp {sort_order}",
        limit=RESULTS_LIMIT
    )['queryId']


def return_date_and_records_count_from_completed_query(client, query_id):
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


def main(client):
    start_date = get_date("What date did the failed requests begin (dd/mm/yy)?")
    end_date = get_date("What date did the failed requests end (dd/mm/yy)?", start_date)

    start_datetime, records_count = return_date_and_records_count_from_completed_query(
        client, 
        query_limits(
            client, 
            start_date, 
            end_date, 
            "asc"
        )
    )
    end_datetime, _ = return_date_and_records_count_from_completed_query(
        client, 
        query_limits(
            client, 
            start_date, 
            end_date, 
            "desc"
        )
    )
    confirm_or_abort(f"There were {int(records_count)} failed requests between {start_datetime.strftime(DATETIME_FORMAT)} "
                f"and {end_datetime.strftime(DATETIME_FORMAT)}.\nIs this correct? (yes/no)")

    return start_datetime, end_datetime
