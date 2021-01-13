# Replaying missed events to Matomo

This interactive Python app is used to replay missed events to Matomo. It builds on and replaces previous scripts that
did a similar thing. The intention of this app is to provided an "end to end" service that prevents you having to dig
through a long page in the team manual. It will perform all the steps for you interactively.

## Prerequisits

* [Docker](https://www.docker.com/)
* [The GDS CLI](https://github.com/alphagov/gds-cli)
* Admin perms for the Verify tools account
* Access to passwords in blackbox

## Use

The app should be invoked with the `replay_missed_events.sh` script. This will build and run a Docker container,
ensuring that your AWS credentials are passed to it. 

The app will take you through all the steps required to download and replay the missed events to Matomo, however you can
choose which stage to start from. This may be useful if you've already downloaded them, or you just need to archive some
replayed events. The stages are listed below.

### Stages

#### 1. Check the date range of an episode of missing logs
This stage will ask for a date range when events were missed. It will then query CloudWatch and tell you how many missed
requests occured in that time period, and when exactly they started/stopped. These start and stop times are used by
later stages to ensure we only deal with time periods we need to.
#### 2. Fetch the logs for missed events from CloudWatch
This stage actually downloads the missed events from CloudWatch and saves them locally. It now uses threads to make this
as quick as possible. The default number of threads is set to 8. Any higher than this and you risk getting throttled by
AWS. You override the number of threads used with the 'NUM_THREADS' env variable when running the script.
#### 3. Replay the missed events from a log file to Matomo
This will read the file of event logs and replay them to Matomo. It uses a fork of the Matomo log anaytics script to do.
You will need to enter the URL of Matomo as well as the API token. This can be found in blackbox in the 'verify-tools-matomo-api-auth-token.gpg' file.
#### 4. Archive the Matomo events
This step uses the AWS ECS api to determine which instance Matomo is running on, and then issue a command to re-archive
the events for a particular period. This will only actually archice if new events have been replayed to Matomo first.
