#!/usr/bin/env python
import subprocess
from getpass import getpass

from rich.console import Console

from fetch_missing_matomo_requests import get_logger
from check_logs import ERROR_STYLE

LOGGER = get_logger()
c = Console(style='bold green')

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

def get_dry_run(current_dry_run):
    if current_dry_run == '--dry-run':
        prompt = "\nDo you want to perform another dry run? 'no' will cause the events to be replayed. (yes/no/abort)\n"
    else:
        prompt = "\nDo you want to perform a dry run before actually replaying the events? 'no' will cause the events to be replayed. (yes/no/abort)\n"
    while True:
        do_dry_run = c.input(prompt).lower()
        if do_dry_run == 'abort':
            LOGGER.error('Aborting due to user input')
            exit(1)
        try:
            dry_run = {'yes': '--dry-run', 'no': ''}[do_dry_run]
        except KeyError:
            c.print("Invalid entry - please enter 'yes', 'no', or abort", style=ERROR_STYLE)
            continue
        return dry_run

def main(events_log_file):
    matomo_url = c.input("\nEnter the URL for Matomo (probably https://analytics.tools.signin.service.gov.uk/):\n")
    c.print("\nEnter the Matomo API token (this can be found in "
            "blackbox in 'verify-tools-matomo-api-auth-token.gpg').")
    matomo_token = getpass(prompt='Token: ')

    dry_run = '?'
    while dry_run:
        dry_run = get_dry_run(dry_run)
        replay_events(dry_run, matomo_url, matomo_token, events_log_file)

