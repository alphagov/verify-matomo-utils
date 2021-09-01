import os
import logging
from datetime import datetime

from rich.console import Console
from rich.logging import RichHandler

LOG_LEVEL = 'LOG_LEVEL'
DATE_FORMAT = '%d/%m/%y'
ERROR_STYLE = 'bold white on red'
CONSOLE = Console(style='bold green')
MATOMO_URL = 'MATOMO_URL'
MATOMO_API_TOKEN = 'MATOMO_API_TOKEN'
LOGGER = None


def validate_environment_variables():
    if os.getenv(MATOMO_URL) is None:
        log_unset_env_variable_error_and_exit(MATOMO_URL)
    if os.getenv(MATOMO_API_TOKEN) is None:
        log_unset_env_variable_error_and_exit(MATOMO_API_TOKEN)


def log_unset_env_variable_error_and_exit(environment_variable):
    get_logger().error(f'{environment_variable} environment variable is not set.')
    exit(1)


def get_logger():
    global LOGGER
    if not LOGGER:
        logging.basicConfig(
                format="%(message)s", 
                datefmt="[%X]", 
                handlers=[RichHandler(rich_tracebacks=True)]
            )
        LOGGER = logging.getLogger(__name__)
        LOGGER.setLevel(os.getenv(LOG_LEVEL, logging.INFO))
    return LOGGER


def console_print(output, **kwargs):
    CONSOLE.print(output, **kwargs)
