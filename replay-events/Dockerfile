FROM alpine as analytics-fork

RUN apk --update add --no-cache git
RUN git clone --depth=1 https://github.com/adityapahuja/matomo-log-analytics.git

FROM python:2-alpine

COPY --from=analytics-fork /matomo-log-analytics /log-analytics

ENTRYPOINT ["/bin/sh"]
