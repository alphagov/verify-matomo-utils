FROM python:2-alpine

RUN apk --update add --no-cache git
RUN git clone --depth=1 https://github.com/adityapahuja/matomo-log-analytics.git log-analytics && \
    rm -rf /log-analytics/.git
COPY docker-entrypoint.sh /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
