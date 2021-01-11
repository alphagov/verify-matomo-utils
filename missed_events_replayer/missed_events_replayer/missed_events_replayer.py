#!/usr/bin/env python
import os
from datetime import timedelta

import boto3

from check_logs import main as check_logs, confirm_or_abort
from fetch_missing_matomo_requests import get_logger, download_failed_requests
from replay import main as replay_events
from archive import main as archive_events

if __name__ == '__main__':
    LOGGER = get_logger()
    client = boto3.client('logs')

    LOGGER.info("Starting check logs")
    start_datetime, end_datetime = check_logs(client)
    LOGGER.info("Finished check logs")

    LOGGER.info("Downloading failed requets from cloudwatch. This may take a few minutes...")
    output_filename = download_failed_requests(
        client,
        start_datetime - timedelta(seconds=1),
        end_datetime + timedelta(seconds=1)
    )
    LOGGER.info("Downloading complete")

    confirm_or_abort(f"\nYou should check the contents of '{os.getenv('HOST_WORKING_DIR') + '/' if os.getenv('HOST_WORKING_DIR') else ''}"
            f"{output_filename}' and ensure the requests to be replayed are correct.\nOnce you've done this enter 'yes'. Or enter 'no' to abort.\n")

    LOGGER.info("Starting replay of events")
    replay_events(output_filename)
    LOGGER.info('Finished replay of events')

    confirm_or_abort("\nThe events must now archived. Do you want to proceed ('no' will abort)? (yes/no)\n")
    LOGGER.info("Starting archiving events")
    archive_events(start_datetime, end_datetime)
    LOGGER.info("Finished archiving events")

    exit(0)




