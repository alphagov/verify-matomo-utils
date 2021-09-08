import boto3

from helpers import get_logger

LOGGER = get_logger()
DATE_RANGE_FORMAT = '%Y-%m-%d'
MAX_WAIT_SECONDS = 172800
SLEEP_TIME = 60
client = boto3.client('ecs')


def get_matomo_container_instance_arn():
    all_container_instance_arns = client.list_container_instances(cluster='platform-web')['containerInstanceArns']
    for arn in all_container_instance_arns:
        task_arns = client.list_tasks(cluster='platform-web', containerInstance=arn)['taskArns']
        if not task_arns:
            continue
        task_defs = client.describe_tasks(cluster='platform-web', tasks=task_arns)['tasks']
        for task_def in task_defs:
            if any(container['name'] == 'matomo' for container in task_def['containers']):
                return arn

    LOGGER.error(f"No container instances found running Matomo. Instance IDs: f{all_container_instance_arns}")
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
                ],
                'executionTimeout': [f"{MAX_WAIT_SECONDS}"]
            },
        )['Command']['CommandId']

    LOGGER.info("The progress of the archiving can be found in the AWS tools account: "
                "https://eu-west-2.console.aws.amazon.com/systems-manager/run-command/executing-commands")

    return f"{command_id} {ec2_instance_id}"

