# Replaying missed events to Matomo

This Python app is used to replay missed events to Matomo. It builds on and replaces previous scripts that
did a similar thing. It's intended that this app is run by a CI pipeline. It can be run locally if required.

## Prerequisites

* [Docker](https://www.docker.com/)
* [The GDS CLI](https://github.com/alphagov/gds-cli)
* Admin perms for the Verify tools account
* Access to passwords in blackbox

## Use

The app should be invoked with the `replay_missed_events.sh` script. This will build and run a Docker container,
ensuring that your AWS credentials are passed to it. It takes two positional arguments, the start datetime and the end 
datetime of the failed requests in ISO8601 format. You'll also need to set the `MATOMO_URL` and `MATOMO_API_TOKEN` env
variables.

```
MATOMO_URL=https://analytics.tools.signin.service.gov.uk/ MATOMO_API_TOKEN=<from blackbox> ./replay_missed_events.sh 2020-09-28T12:13:14Z 2020-09-28T13:14:15Z
```

### What the app does

#### 1. Fetch the logs for missed events from CloudWatch
This stage downloads the missed events from CloudWatch and saves them locally. It  uses threads to make this
as quick as possible. The default number of threads is set to 8. Any higher than this and you risk getting throttled by
AWS. You can override the number of threads used with the 'NUM_THREADS' env variable when running the script.
#### 2. Replay the missed events from a log file to Matomo
This will read the file of event logs and replay them to Matomo. It uses a fork of the Matomo log analytics script to do this.
The URL of Matomo and an API token will need setting as env variables (`MATOMO_URL` and `MATOMO_API_TOKEN`). The token can be 
found in blackbox in the 'verify-tools-matomo-api-auth-token.gpg' file.
#### 3. Archive the Matomo events
This step uses the AWS ECS API to determine which instance Matomo is running on, and then issue a command to re-archive
the events for a particular period. This will only actually archive if new events have been replayed to Matomo first.
