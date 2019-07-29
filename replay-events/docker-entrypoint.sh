#!/bin/sh

if [ -z "${MATOMO_URL}" ]; then
    echo "No Matomo URL detected: aborting."
    exit 1
fi
if [ -z "${MATOMO_TOKEN}" ]; then
    echo "No Matomo token detected: aborting."
    exit 1
fi
dry_run_parameter=""
if [ -n "${DRY_RUN}" ]; then
    dry_run_parameter="--dry-run"
fi

python -u /log-analytics/import_logs.py \
    ${dry_run_parameter} \
    --url="$MATOMO_URL" \
    --token-auth="$MATOMO_TOKEN" \
    --log-format-name=nginx_json \
    --replay-tracking \
    --enable-static \
    --enable-bots \
    --enable-reverse-dns \
    /access.log
