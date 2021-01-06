#!/usr/bin/env python
from datetime import timedelta

import boto3

from check_logs.check_logs import main as check_logs, confirm_or_abort
from retrieve_logs.fetch_missing_matomo_requests import get_logger, download_failed_requests

if __name__ == '__main__':
    LOGGER = get_logger()
    client = boto3.client('logs')

    LOGGER.info(">>> Starting check logs")
    start_datetime, end_datetime = check_logs(client)
    LOGGER.info(">>> Finished check logs")

    LOGGER.info(">>> Downloading failed requets from cloudwatch. This may take a few minutes...")
    output_file_path = download_failed_requests(
        client,
        start_datetime - timedelta(seconds=1),
        end_datetime - timedelta(seconds=1)
    )
    LOGGER.info(">>> Downloading complete")

    confirm_or_abort(f"\nYou should check the contents of {output_file_path} and ensure the requests to be replayed "
            f"are correct. Once you've done this enter 'yes'. Or enter 'no' to abort.")


