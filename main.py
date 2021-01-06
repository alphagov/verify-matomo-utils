#!/usr/bin/env python
from datetime import timedelta

import boto3

from check_logs.check_logs import main as check_logs
from retrieve_logs.fetch_missing_matomo_requests import get_logger, download_failed_requests

if __name__ == '__main__':
    LOGGER = get_logger()
    client = boto3.client('logs')

    LOGGER.info(">>> Starting check logs")
    start_datetime, end_datetime = check_logs(client)
    LOGGER.info(">>> Finished check logs")

    LOGGER.info("Downloading failed requets from cloudwatch. This may take a few minutes...")
    download_failed_requests(client, start_datetime - timedelta(seconds=1), end_datetime - timedelta(seconds=1))
