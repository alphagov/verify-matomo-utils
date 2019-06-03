#!/usr/bin/env bash

if [ ! -f "access.log" ]; then
    echo "Please copy the 'access.log' you wish to replay into this directory."
    exit 1
fi

docker build -t matomo-import .

cat << 'EOF'
In the container, you will want to run a command like:
python -u /log-analytics/import_logs.py \
    --url=<matomo-url> \
    --log-format-name=nginx_json \
    --replay-tracking \
    --enable-static \
    --enable-bots \
    --enable-reverse-dns \
    --recorders=2 \
    --login=<matomo-login> \
    --password='<matomo-password>' \
    /access.log
Remember to substitute in your Matomo URL and login credentials.
EOF

docker run --rm \
    --mount type=bind,source="$(pwd)"/access.log,target=/access.log \
    -it matomo-import
