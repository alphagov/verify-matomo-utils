#!/bin/sh

if [ -z "${MATOMO_URL}" ]; then
    echo "No Matomo URL detected: aborting."
    exit 1
fi
if [ -z "${MATOMO_LOGIN}" ]; then
    echo "No Matomo login detected: aborting."
    exit 1
fi
if [ -z "${MATOMO_PASSWORD}" ]; then
    echo "No Matomo password detected: aborting."
    exit 1
fi

python -u /log-analytics/import_logs.py \
    --url="$MATOMO_URL" \
    --login="$MATOMO_LOGIN" \
    --password="$MATOMO_PASSWORD" \
    --log-format-name=nginx_json \
    --replay-tracking \
    --enable-static \
    --enable-bots \
    --enable-reverse-dns \
    --recorders=2 \
    /access.log
