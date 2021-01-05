#!/usr/bin/env sh

set -e

if [ -z "${AWS_DEFAULT_REGION}" ]; then
    echo "Please ensure you specify the 'AWS_DEFAULT_REGION' for communication with AWS services."
    exit 1
fi
if [ -z "${AWS_ACCESS_KEY_ID}" ] || \
        [ -z "${AWS_SECRET_ACCESS_KEY}" ] || \
        [ -z "${AWS_SESSION_TOKEN}" ]; then
    echo "Please ensure you authenticate through AWS STS before running this script."
    echo "This should provide 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY' and 'AWS_SESSION_TOKEN' variables."
    exit 1
fi
if [ -z "${START_DATE}" ]; then
    echo "Please ensure you use the \"START_DATE\" variable to specify a start date to begin searching from."
    echo "Only a date should be provided, in the format 'yyyy-mm-dd'."
    echo "The script assumes logs should be searched from the start of this day, in a UTC timezone."
    exit 1
fi
if [ -z "${NUM_OF_DAYS}" ]; then
    echo "Number of days not specified. Will search for 1 day of logs."
    export NUM_OF_DAYS=1
fi

set -u

function be_in_directory {
    # Sourced from Stack Overflow answer
    # https://stackoverflow.com/a/29835459
    # author: https://stackoverflow.com/users/1230559/city
    # answer author: https://stackoverflow.com/users/45375/mklement0
    cd -- "$(dirname -- "$0")"
}

be_in_directory

docker build -t matomo-retrieve-logs .

docker run --rm \
    --mount type=bind,source="$(pwd)",target=/app \
    -e AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY \
    -e AWS_SESSION_TOKEN \
    -e AWS_DEFAULT_REGION \
    -e START_DATE \
    -e NUM_OF_DAYS \
    -e LOG_LEVEL \
    -e OUTPUT_FILENAME \
    -e PERIOD_WIDTH_IN_SECONDS \
    -it matomo-retrieve-logs
