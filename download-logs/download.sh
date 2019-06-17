#!/usr/bin/env bash

set -e

numberregex='^[0-9]+$'
if ! [[ $1 =~ ${numberregex} && $2 =~ ${numberregex} ]]; then
    echo "You must specify a start and end time in milliseconds."
    exit 1
fi

echo "More specific results can be obtained by providing one or more '--log-stream-name' arguments."
echo "Log stream names can be determined from CloudWatch in the console."
echo "(You currently need to modify this script to add stream names.)"
echo "Are you sure you wish to proceed? [yN]"
read REPLY && if [[ $REPLY =~ ^[Yy]$ ]]; then
    aws logs filter-log-events \
        --start-time $1 \
        --end-time $2 \
        --log-group-name "matomo" \
        --filter-pattern='{ $.status = 5* }' \
        > aws_logs.txt
fi
