#!/usr/bin/env bash

set -eu

function usage {
  echo "If you want to start the replay script from a particular stage, supply the '--start-with' option"
  echo
  echo "$ replay_missed_events.sh [--start-with (check|fetch|replay|archive)]"
  echo
  exit 1
}

if [[ $# -gt 0 ]]; then
  if [[ $# != 2 ]]; then
    usage
  fi
  if [[ $1 != '--start-with' ]] || ! [[ $2 =~ ^(check|fetch|replay|archive)$ ]]; then
    usage
  fi
fi

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
    -e HOST_WORKING_DIR=$(pwd) \
    -it matomo-missed-events-replayer \
    $@
