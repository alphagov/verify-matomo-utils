import os
import logging
from datetime import datetime

from rich.console import Console
from rich.logging import RichHandler

LOG_LEVEL = 'LOG_LEVEL'
DATE_FORMAT = '%d/%m/%y'
ERROR_STYLE = 'bold white on red'
CONSOLE = Console(style='bold green')
LOGGER = None


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


def get_date(prompt, start_date_to_compare=None):
    while True:
        try:
            date = datetime.strptime(get_input(prompt), DATE_FORMAT)
        except ValueError:
            CONSOLE.print("Invalid date format - please enter a date as dd/mm/yy.", style=ERROR_STYLE)
            continue
        if date.date() > datetime.today().date():
            CONSOLE.print("Invalid date - please enter a date in the past or today.", style=ERROR_STYLE)
            continue
        elif start_date_to_compare and date.date() < start_date_to_compare.date():
            CONSOLE.print("Invalid date - please enter an end date the same or after the start date.", style=ERROR_STYLE)
        else:
            break
    return date


def get_output_filename(prompt):
    while True:
        filename = get_input(prompt)
        if os.path.exists(f"/app/logs/{filename}"):
            return filename
        else:
            CONSOLE.print("File doesn't exist, please try again.", style=ERROR_STYLE)

def get_input(prompt):
    return CONSOLE.input("\n" + prompt + "\n")


def confirm_or_abort(prompt):
    while True:
        looks_good = get_input(prompt).lower()
        if looks_good not in ('yes', 'no'):
            CONSOLE.print("Invalid input - please enter 'yes' or 'no'", style=ERROR_STYLE)
            continue
        elif looks_good == 'yes':
            break
        else:
            LOGGER.error("Aborting due to user input")
            exit(1)


def get_dry_run(current_dry_run):
    if current_dry_run == '--dry-run':
        prompt = "Do you want to perform another dry run? 'no' will cause the events to be replayed. (yes/no/abort)"
    else:
        prompt = "Do you want to perform a dry run before actually replaying the events? 'no' will cause the events to be replayed. (yes/no/abort)"
    while True:
        do_dry_run = get_input().lower()
        if do_dry_run == 'abort':
            LOGGER.error('Aborting due to user input')
            exit(1)
        try:
            dry_run = {'yes': '--dry-run', 'no': ''}[do_dry_run]
        except KeyError:
            CONSOLE.print("Invalid entry - please enter 'yes', 'no', or abort", style=ERROR_STYLE)
            continue
        return dry_run


def console_print(output, **kwargs):
    CONSOLE.print(output, **kwargs)
