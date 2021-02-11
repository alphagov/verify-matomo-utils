#!/usr/bin/env python
import os
import argparse
from datetime import timedelta

import boto3

from helpers import get_date, get_output_filename, get_logger, confirm_or_abort, get_stage
from check_logs import main as check_logs
from fetch_missing_matomo_requests import download_failed_requests
from replay import main as replay_events
from archive import main as archive_events


if __name__ == '__main__':
    starting_stage = get_stage()
    starting_stage_index = starting_stage[0]

    LOGGER = get_logger()
    client = boto3.client('logs')

    LOGGER.info(f"Starting at the '{starting_stage[1]}' stage.")
    if starting_stage_index == 1:
        LOGGER.info("Starting check logs")
        start_datetime, end_datetime = check_logs(client)
        LOGGER.info("Finished check logs")

    if starting_stage_index <= 2:
        LOGGER.info("Downloading failed requets from cloudwatch. This may take a few minutes...")
        if starting_stage_index == 2:
            start_datetime = get_date("What date did the failed requests begin? (dd/mm/yy)")
            end_datetime = get_date("What date did the failed requests end? (dd/mm/yy)") + timedelta(1)

        output_filename = download_failed_requests(
            client,
            start_datetime - timedelta(seconds=1),
            end_datetime + timedelta(seconds=1),
        )
        LOGGER.info("Downloading complete")

        confirm_or_abort(
                f"You should check the contents of '{os.getenv('HOST_WORKING_DIR') + '/' if os.getenv('HOST_WORKING_DIR') else ''}"
                f"{output_filename}' and ensure the requests to be replayed are correct.\nOnce you've done this enter 'yes'. Or enter 'no' to abort."
            )

    if starting_stage_index <= 3:
        LOGGER.info("Starting replay of events")
        if starting_stage_index == 3:
            output_filename = get_output_filename("Which file should events be imported from? It should be in the root directory of the app on the host machine.")
        replay_events(output_filename)
        LOGGER.info('Finished replay of events')

        confirm_or_abort("\nThe events must now be archived. Do you want to proceed ('no' will abort)? (yes/no)\n")

    if starting_stage_index <= 4:
        LOGGER.info("Starting archiving events")
        if starting_stage_index >= 3:
            start_datetime = get_date("What date does archiving need to start from? (dd/mm/yy)")
            end_datetime = get_date("What date does archiving need to finish? (dd/mm/yy)") + timedelta(1)
        archive_events(start_datetime, end_datetime)
        LOGGER.info("Finished archiving events")

    exit(0)

