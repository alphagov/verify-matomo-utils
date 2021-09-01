#!/usr/bin/env python

import argparse

from datetime import timedelta, datetime

import boto3

from helpers import get_logger, validate_environment_variables
from fetch_missing_matomo_requests import download_failed_requests
from replay import replay_events
from archive import main as archive_events


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "start",
        type=lambda d: datetime.strptime(d, "%Y-%m-%dT%H:%M:%SZ"),
        help="The datetime that the missed events started in ISO8601 format (YYYY-MM-DDThh:mm:ssZ)"
    )
    parser.add_argument(
        "end",
        type=lambda d: datetime.strptime(d, "%Y-%m-%dT%H:%M:%SZ"),
        help="The datetime that the missed events finished in ISO8601 format (YYYY-MM-DDThh:mm:ssZ)"
    )
    args = parser.parse_args()

    return args.start, args.end


if __name__ == '__main__':
    validate_environment_variables()
    start_datetime, end_datetime = parse_args()

    LOGGER = get_logger()
    client = boto3.client('logs')

    LOGGER.info(f"Downloading failed requests from CloudWatch between {start_datetime} and {end_datetime}. This may "
                f"take a few minutes...")
    output_filename = download_failed_requests(
        client,
        start_datetime - timedelta(minutes=10),
        end_datetime + timedelta(minutes=10),
    )
    LOGGER.info("Download complete")

    LOGGER.info("Starting replay of events")
    replay_events(output_filename)
    LOGGER.info('Finished replay of events')

    LOGGER.info("Starting archiving events")
    archive_events(start_datetime, end_datetime)
    LOGGER.info("Finished archiving events")

    exit(0)

