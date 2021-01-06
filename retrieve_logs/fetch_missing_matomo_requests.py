import os
import logging
import time
import re
from datetime import date, datetime, timedelta, timezone, time as datetime_time
from concurrent import futures

import boto3

LOG_LEVEL = 'LOG_LEVEL'
NUM_OF_DAYS = 'NUM_OF_DAYS'
OUTPUT_FILENAME = 'OUTPUT_FILENAME'
PERIOD_WIDTH_IN_SECONDS = 'PERIOD_WIDTH_IN_SECONDS'
START_DATE = 'START_DATE'
NUM_THREADS = int(os.getenv('NUM_THREADS', 8))

DATE_FORMAT = '%Y-%m-%d'
FILENAME_SUFFIX = '_matomo_requests.json'
MAX_REQUESTS = 10_000

_logger = None


def get_logger():
    global _logger
    if not _logger:
        logging.basicConfig(level=logging.INFO)
        _logger = logging.getLogger(__name__)
        _logger.setLevel(os.getenv(LOG_LEVEL, logging.INFO))
    return _logger


def log_too_many_requests_and_exit(period_start, period_end):
    get_logger().error(
            f'{MAX_REQUESTS} requests received from the period {period_start} to {period_end}.'
            + ' Some requests may not have been downloaded properly as a result.'
            + ' The period size should be decreased to ensure all requests are downloaded.')
    exit(1)


def log_unset_env_variable_error_and_exit(environment_variable):
    get_logger().error(f'{environment_variable} environment variable is not set.')
    exit(1)


def validate_environment_variables():
    if os.getenv(START_DATE) is None:
        log_unset_env_variable_error_and_exit(START_DATE)
    if os.getenv(NUM_OF_DAYS) is None:
        log_unset_env_variable_error_and_exit(NUM_OF_DAYS)


def get_start_datetime():
    try:
        start_date_env = os.getenv(START_DATE)
        if start_date_env == 'yesterday':
            start_of_day = datetime.combine(date.today(), datetime_time())
            return start_of_day - timedelta(days=1)
        return datetime.strptime(start_date_env, DATE_FORMAT)
    except ValueError:
        get_logger().exception(
                f'START_DATE has an invalid format. Please follow the format "{DATE_FORMAT}"'
                + ' or use the keyword "yesterday".')
        exit(1)


def get_number_of_days():
    try:
        return int(os.getenv(NUM_OF_DAYS))
    except ValueError:
        get_logger().exception('NUM_OF_DAYS has an invalid format. Please specify an integer.')
        exit(1)


def get_period_width():
    try:
        return int(os.getenv(PERIOD_WIDTH_IN_SECONDS, 60 * 5))
    except ValueError:
        get_logger().exception('PERIOD_WIDTH_IN_SECONDS has an invalid format. Please specify an integer.')
        exit(1)


def get_output_filename(start_datetime, end_datetime):
    filename = os.getenv(OUTPUT_FILENAME)
    if filename is None or len(filename) < 1:
        return start_datetime.strftime(DATE_FORMAT) + '_' + end_datetime.strftime(DATE_FORMAT) + FILENAME_SUFFIX
    return filename

def run_query(client, start_timestamp, end_timestamp):
    response =  client.start_query(
        logGroupName='matomo',
        startTime=int(start_timestamp.timestamp() * 1000),
        endTime=int(end_timestamp.timestamp() * 1000),
        queryString=
        """fields @message
        | sort @timestamp asc
        | filter @logStream like /matomo-nginx/
        | filter status >= '500'
        | filter user_agent!='ELB-HealthChecker/2.0'
        | filter path like /idsite=1/
        | filter path like /rec=1/""",
        limit=MAX_REQUESTS
    )
    queryId = response['queryId']
    status = 'Running'
    seconds_slept = 0
    while status != 'Complete':
        time.sleep(1)
        seconds_slept += 1
        if seconds_slept % 30 == 0:
            get_logger().debug(f'Still waiting for a request. Spent {seconds_slept} seconds waiting so far.')
        response = client.get_query_results(queryId=queryId)
        try:
            status = response['status']
        except KeyError:
            print(response.keys())
            raise
    return start_timestamp, end_timestamp, response

def extract_requests_from_response(response, period_start, period_end):
    messages = []
    for message_list in response['results']:
        if len(message_list) >= MAX_REQUESTS:
            log_too_many_requests_and_exit(period_start, period_end)
        for message in message_list:
            if message['field'] == '@message':
                messages.append(message['value'])
                break
    get_logger().debug(f'extracted {len(messages)} requests for the period {period_start} to {period_end}')

    return messages

def write_requests_to_file(requests, output_filename):
    total_written = 0
    with open(output_filename, 'a+') as f:
        for request in sorted(requests, key=lambda request: re.findall(r'msec": "(.+?)"', request)[0]):
            total_written += 1
            f.write(request + '\n')

    return total_written

def download_failed_requests(client, start_datetime, end_datetime):
    period_width = get_period_width()
    output_filename = get_output_filename(start_datetime, end_datetime)
    if os.path.exists(output_filename):
        os.remove(output_filename)

    period_start = datetime.utcfromtimestamp(start_datetime.replace(tzinfo=timezone.utc).timestamp())
    total_written = 0
    futures_list = []
    requests = []
    with futures.ThreadPoolExecutor(NUM_THREADS) as executor:
        while period_start <= end_datetime:
            period_end = period_start + timedelta(seconds=period_width, microseconds=-1)
            get_logger().debug(f'Scheduling query from {period_start} to {period_end}')
            futures_list.append(executor.submit(run_query, client, period_start, period_end))
            period_start += timedelta(seconds=period_width)

        for future in futures.as_completed(futures_list):
            period_start, period_end, response = future.result()
            requests += extract_requests_from_response(response, period_start, period_end)

    total_written = write_requests_to_file(requests, output_filename)

    get_logger().info(f'Wrote {total_written} requests to file "{output_filename}".')


if __name__ == '__main__':
    validate_environment_variables()

    client = boto3.client('logs')

    start_datetime = get_start_datetime()
    num_of_days = get_number_of_days()
    end_datetime = start_datetime + timedelta(days=num_of_days, microseconds=-1)

    download_failed_requests(client, start_datetime, end_datetime)

