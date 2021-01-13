#!/usr/bin/env bash

set -eu

eval $(gds aws verify-tools -e)
export AWS_DEFAULT_REGION=eu-west-2

docker build -t matomo-missed-events-replayer .

docker run --rm \
    --mount type=bind,source="$(pwd)",target=/app/logs \
    -e AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY \
    -e AWS_SESSION_TOKEN \
    -e AWS_DEFAULT_REGION \
    -e LOG_LEVEL \
    -e OUTPUT_FILENAME \
    -e PERIOD_WIDTH_IN_SECONDS \
    -e NUM_THREADS \
    -e HOST_WORKING_DIR=$(pwd) \
    -it matomo-missed-events-replayer
