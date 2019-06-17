#!/bin/sh

if [ -z "${MATOMO_URL}" ]; then
    echo "No Matomo URL detected: aborting."
    exit 1
fi
if [ -z "${MATOMO_TOKEN}" ]; then
    echo "No Matomo token detected: aborting."
    exit 1
fi

python -u /log-analytics/import_logs.py \
    --url="$MATOMO_URL" \
    --token-auth="$MATOMO_TOKEN" \
    --log-format-name=nginx_json \
    --replay-tracking \
    --enable-static \
    --enable-bots \
    --enable-reverse-dns \
    --recorders=2 \
    /access.log
