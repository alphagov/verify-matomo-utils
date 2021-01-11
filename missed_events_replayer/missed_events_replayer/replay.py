import subprocess
from getpass import getpass

from helpers import get_input, console_print, get_logger, get_dry_run

LOGGER = get_logger()


def replay_events(dry_run, matomo_url, matomo_token, events_log_file):
    try:
        replayed_result = subprocess.run(
            [
                'python2',
                '-u',
                '/app/log-analytics/import_logs.py',
                f"{dry_run}",
                f'--url={matomo_url}',
                f'--token-auth={matomo_token}',
                '--log-format-name=nginx_json',
                '--replay-tracking',
                '--enable-static',
                '--enable-bots',
                '--enable-reverse-dns',
                f'/app/logs/{events_log_file}'
            ],
            check=True
        )
    except subprocess.CalledProcessError:
        LOGGER.error("Failed to replay events")
        raise


def main(events_log_file):
    matomo_url = get_input("Enter the URL for Matomo (probably https://analytics.tools.signin.service.gov.uk/):")
    console_print("Enter the Matomo API token (this can be found in "
            "blackbox in 'verify-tools-matomo-api-auth-token.gpg').")
    matomo_token = getpass(prompt='Token: ')

    dry_run = '?'
    while dry_run:
        dry_run = get_dry_run(dry_run)
        replay_events(dry_run, matomo_url, matomo_token, events_log_file)
