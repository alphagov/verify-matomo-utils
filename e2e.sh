#!/usr/bin/env sh

set -e

eval $(gds aws verify-tools -e)
export AWS_DEFAULT_REGION=eu-west-2

set -u

function be_in_directory {
    # Sourced from Stack Overflow answer
    # https://stackoverflow.com/a/29835459
    # author: https://stackoverflow.com/users/1230559/city
    # answer author: https://stackoverflow.com/users/45375/mklement0
    cd -- "$(dirname -- "$0")"
}

be_in_directory

docker build -t matomo-retrieve-and-replay-logs .

docker run --rm \
    --mount type=bind,source="$(pwd)",target=/app \
    -e AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY \
    -e AWS_SESSION_TOKEN \
    -e AWS_DEFAULT_REGION \
    -e LOG_LEVEL \
    -e OUTPUT_FILENAME \
    -e PERIOD_WIDTH_IN_SECONDS \
    -it matomo-retrieve-and-replay-logs
