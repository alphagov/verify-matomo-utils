import time

import boto3

from helpers import console_print, get_logger

LOGGER = get_logger()
DATE_RANGE_FORMAT = '%Y-%m-%d'
MAX_WAIT_SECONDS = 600
client = boto3.client('ecs')


def get_matomo_container_instance_arn():
    all_container_instance_arns = client.list_container_instances(cluster='platform-web')['containerInstanceArns']

    for arn in all_container_instance_arns:
        task_arns = client.list_tasks(cluster='platform-web', containerInstance=arn)['taskArns']
        task_defs = client.describe_tasks(cluster='platform-web', tasks=task_arns)['tasks']
        for task_def in task_defs:
            if any(container['name'] == 'matomo' for container in task_def['containers']):
                return arn

    LOGGER.error(f"No container instances found running Matomo. Instance IDs: f{all_container_instance_arns}")
    exit(1)


def wait_and_return_succesful_command_response(ssm_client, command_id, ec2_instance_id):
    slept_time = 0
    while True:
        time.sleep(1)
        slept_time += 1
        command_response = ssm_client.get_command_invocation(
                CommandId=command_id, 
                InstanceId=ec2_instance_id,
            )
        if command_response['Status'] == 'Success':
            return command_response
        if slept_time >= MAX_WAIT_SECONDS:
            LOGGER.error(f'Response not received within {MAX_WAIT_SECONDS} seconds. Status: {command_response}')
            exit(1)


def main(archive_start_date, archive_end_date):
    ec2_instance_id = client.describe_container_instances(
            cluster='platform-web', 
            containerInstances=[get_matomo_container_instance_arn()],
        )['containerInstances'][0]['ec2InstanceId']

    ssm_client = boto3.client('ssm')
    
    date_range_string = f'{archive_start_date.strftime(DATE_RANGE_FORMAT)},{archive_end_date.strftime(DATE_RANGE_FORMAT)}'

    command_id = ssm_client.send_command(
            InstanceIds=[ec2_instance_id], 
            DocumentName='AWS-RunShellScript', 
            Parameters={
                'commands': [
                    "container_id=$(sudo docker ps | grep platform-deployer-verify-matomo | awk '{print $1}')",
                    f'sudo docker exec -u www-data "$container_id" ./console core:archive --force-idsites="1" --force-date-range={date_range_string}'
                ]
            },
        )['Command']['CommandId']
    
    command_response = wait_and_return_succesful_command_response(ssm_client, command_id, ec2_instance_id)
    pretty_print_command_response(command_response)


def pretty_print_command_response(command_response):
    LOGGER.info('The following output is from the archiving task runnong on Matomo...\n')
    stdout_content = command_response['StandardOutputContent']
    for line in stdout_content:
        if line[-1] != "\\n":
            console_print(line, end='')
        else:
            console_print(line[:-1])
