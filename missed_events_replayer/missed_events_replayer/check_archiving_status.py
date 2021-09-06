#!/usr/bin/env python

import argparse
import sys

import boto3

from helpers import get_logger


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command_id",
        help="The ID of the archiving command"
    )
    parser.add_argument(
        "instance_id",
        help="The ec2 instance ID the command is running on"
    )
    args = parser.parse_args()

    return args.command_id, args.instance_id


def get_command_invocation(ssm_client, command_id, ec2_instance_id):
    return ssm_client.get_command_invocation(
            CommandId=command_id,
            InstanceId=ec2_instance_id,
    )


def pretty_print_command_response(command_response):
    stdout_content = command_response['StandardOutputContent']
    for line in stdout_content:
        if line[-1] != "\\n":
            print(line, end='', file=sys.stderr)
        else:
            print(line[:-1], file=sys.stderr)


if __name__ == "__main__":
    LOGGER = get_logger()

    command_id, instance_id = parse_args()

    LOGGER.info(f"Checking status of command with ID {command_id} running on ec2 instance with ID: {instance_id}")
    response = get_command_invocation(
        boto3.client('ssm'),
        command_id,
        instance_id
    )

    status = response['Status']
    LOGGER.info(f"Status: {status}")

    if status == 'Success':
        LOGGER.info('The following output is from the archiving task running on Matomo:\n')
        pretty_print_command_response(response)

    print(status)



