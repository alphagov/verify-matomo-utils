#!/usr/bin/env bash

set -e

if [ -z "${MATOMO_URL}" ]; then
    echo "Please ensure you specify a valid URL for Matomo."
    echo "This is done by setting the \"MATOMO_URL\" variable."
    exit 1
fi
if [ -z "${MATOMO_LOGIN}" ] || [ -z "${MATOMO_PASSWORD}" ]; then
    echo "Please ensure you specify credentials for Matomo."
    echo "This is done by setting the \"MATOMO_LOGIN\" and \"MATOMO_PASSWORD\" variables."
    exit 1
fi

if [ ! -f "access.log" ]; then
    echo "Please copy the 'access.log' you wish to replay into this directory."
    exit 1
fi

docker build -t matomo-replay-events .

docker run --rm \
    --mount type=bind,source="$(pwd)"/access.log,target=/access.log \
    -e MATOMO_URL \
    -e MATOMO_LOGIN \
    -e MATOMO_PASSWORD \
    -it matomo-replay-events
