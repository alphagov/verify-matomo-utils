from datetime import datetime, timedelta, timezone
import os
import boto3
import logging
import time
from _decimal import Decimal

LOG_LEVEL = 'LOG_LEVEL'
NUM_OF_DAYS = 'NUM_OF_DAYS'
START_DATE = 'START_DATE'
DATE_FORMAT = '%Y-%m-%d'
FILENAME_SUFFIX = '_matomo_requests.json'
MAX_REQUESTS = 10_000
PERIOD_WIDTH_IN_SECONDS = 60 * 5

_logger = None


def get_logger():
    global _logger
    if not _logger:
        logging.basicConfig(level=logging.INFO)
        _logger = logging.getLogger(__name__)
        _logger.setLevel(os.getenv(LOG_LEVEL, logging.INFO))
    return _logger


def log_unset_env_variable_error_and_exit(environment_variable):
    get_logger().error(f'{environment_variable} environment variable is not set.')
    exit(1)


def validate_environment_variables():
    if os.getenv(START_DATE) is None:
        log_unset_env_variable_error_and_exit(START_DATE)
    if os.getenv(NUM_OF_DAYS) is None:
        log_unset_env_variable_error_and_exit(NUM_OF_DAYS)


def get_start_date():
    try:
        return datetime.strptime(os.getenv(START_DATE), DATE_FORMAT)
    except ValueError:
        get_logger().exception(f'START_DATE has an invalid format. Please follow the format: "{DATE_FORMAT}".')
        exit(1)


def get_number_of_days():
    try:
        return int(os.getenv(NUM_OF_DAYS))
    except ValueError:
        get_logger().exception('NUM_OF_DAYS has an invalid format. Please specify an integer.')
        exit(1)


def wait_for_the_query_to_complete(response):
    queryId = response['queryId']
    status = 'Running'
    seconds_slept = 0
    while status != 'Complete':
        time.sleep(1)
        seconds_slept += 1
        if seconds_slept % 30 == 0:
            get_logger().debug(f'Still waiting for a request. Spent {seconds_slept} seconds waiting so far.')
        response = client.get_query_results(queryId=queryId)
        status = response['status']
    return response


def run_query(start_timestamp, end_timestamp):
    return client.start_query(
        logGroupName='matomo',
        startTime=int(start_timestamp.timestamp() * 1000),
        endTime=int(end_timestamp.timestamp() * 1000),
        queryString=
        """fields @message
        | sort @timestamp asc
        | filter @logStream like /matomo-nginx/
        | filter status!='200'
        | filter status!='204'
        | filter user_agent!='ELB-HealthChecker/2.0'
        | filter path like /idsite=1/
        | filter path like /rec=1/""",
        limit=10000
    )


def write_requests_to_a_file(response, period_start, period_end, output_filename):
    count_written = 0
    with open(output_filename, 'a+') as f:
        for message in response['results']:
            if len(message) >= MAX_REQUESTS:
                get_logger().warning(
                        f'10000 requests received from the period {period_start} to {period_end}.'
                        + ' Some requests may not have been downloaded properly as a result.'
                        + ' Please consider decreasing the offset to ensure all requests are downloaded.')
            for message in message:
                if message['field'] == '@message':
                    f.write(message['value'] + '\n')
                    count_written += 1
                    break
    if count_written > 0:
        get_logger().debug(
                f'Wrote {count_written} requests to file {output_filename}'
                + f' from within the period {period_start} to {period_end}')


if __name__ == '__main__':
    validate_environment_variables()

    client = boto3.client('logs')

    start_date = get_start_date()
    num_of_days = get_number_of_days()
    end_date = start_date + timedelta(days=num_of_days, microseconds=-1)

    output_filename = start_date.strftime(DATE_FORMAT) + '_' + end_date.strftime(DATE_FORMAT) + FILENAME_SUFFIX
    if os.path.exists(output_filename):
        os.remove(output_filename)

    period_start = datetime.utcfromtimestamp(start_date.replace(tzinfo=timezone.utc).timestamp())
    while period_start < end_date:
        period_end = period_start + timedelta(seconds=PERIOD_WIDTH_IN_SECONDS, microseconds=-1)
        get_logger().debug(f'Running query from {period_start} to {period_end}')
        response = run_query(period_start, period_end)
        response = wait_for_the_query_to_complete(response)
        write_requests_to_a_file(response, start_date, end_date, output_filename)
        period_start += timedelta(seconds=PERIOD_WIDTH_IN_SECONDS)
