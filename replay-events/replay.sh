#!/usr/bin/env bash

set -e

if [ -z "${MATOMO_URL}" ]; then
    echo "Please ensure you specify a valid URL for Matomo."
    echo "This is done by setting the \"MATOMO_URL\" variable."
    exit 1
fi
if [ -z "${MATOMO_TOKEN}" ]; then
    echo "Please ensure you specify an access token for Matomo."
    echo "This can be provided through the \"MATOMO_TOKEN\" variable."
    exit 1
fi

if [ ! -f "access.log" ]; then
    echo "Please copy the 'access.log' you wish to replay into this directory."
    exit 1
fi

function be_in_directory {
    cd "$( dirname "${BASH_SOURCE[0]}" )"
}

be_in_directory

docker build -t matomo-replay-events .

docker run --rm \
    --mount type=bind,source="$(pwd)"/access.log,target=/access.log \
    -e MATOMO_URL \
    -e MATOMO_TOKEN \
    -it matomo-replay-events
