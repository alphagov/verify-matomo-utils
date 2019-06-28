# verify-matomo-utils

Collection of tools used for interacting with Matomo (formerly called Piwik)

## What is here?

This is just a collection of helper scripts.
The current intention is to make it easier to replay data into Matomo from Nginx logs in CloudWatch.
More details about how to use them are included in other documentation.
There is no context in this repo to keep it as generic as possible.
(i.e. it shouldn't be exclusive to any individual Matomo setup.)

- [`retrieve-logs`](./retrieve-logs) - downloads logs from AWS CloudWatch via Insights
- [`replay-events`](./replay-events) - replays requests into Matomo from an Nginx access log
  (or other compatible file format)
