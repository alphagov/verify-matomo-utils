# verify-matomo-utils

Collection of tools used for interacting with Matomo (formerly called Piwik)

## What is here?

This is just a collection of helper scripts.
The current intention is to make it easier to replay data into Matomo from Nginx logs in CloudWatch.
More details about how to use them are included in other documentation.
There is no context in this repo to keep it as generic as possible.
(i.e. it shouldn't be exclusive to any individual Matomo setup.)

- [`missed_events_replayer`](./missed_events_replayer) - downloads logs from AWS CloudWatch via Insights, replays the
  requests into Matomo from the downloaded Nginx access logs and then archives them in Matomo. An interactive script.
