import os
import subprocess
import sys

from helpers import get_logger, MATOMO_URL, MATOMO_API_TOKEN


def replay_events(events_log_file):
    try:
        subprocess.run(
            [
                'python2',
                '-u',
                '/app/log-analytics/import_logs.py',
                f'--url={os.getenv(MATOMO_URL)}',
                f'--token-auth={os.getenv(MATOMO_API_TOKEN)}',
                '--log-format-name=nginx_json',
                '--replay-tracking',
                '--enable-static',
                '--enable-bots',
                '--enable-reverse-dns',
                f'./{events_log_file}'
            ],
            check=True,
            stdout=sys.stderr
        )
    except subprocess.CalledProcessError:
        get_logger().error("Failed to replay events")
        raise
