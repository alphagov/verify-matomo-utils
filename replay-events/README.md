# replay-events

This contains a Dockerfile used to define an environment with Python 2 to run the Matomo log analytics script.
An entrypoint script uses environment variables passed in from Docker to run the Matomo log analytics script to replay
the events from a supplied JSON Nginx access log.
A fork of the python is being used to handle `X-Forwarded-For` headers as given by AWS Application ELBs.
Since automatic token authentication using Matomo hasn't worked in testing thus far, a token needs to be manually
supplied to the script.
A token can be retrieved from the Matomo UI.
In recent versions of Matomo: after logging in, go to the admin page (the cog) and go to the `Settings` page within
the `Personal` group.
An `API Authentication Token` is available towards the bottom of the page, and can be supplied to the script via the
`MATOMO_TOKEN` environment variable.
The `MATOMO_URL` environment variable should also be set to the Matomo base URL.

There is a bash script suppied to simplify building and running the docker container.
It tags the image `matomo-replay-events` by default.
An example workflow using this script might be something like this:

```
mv download-logs/aws_logs.txt.ndjson replay-events/access.log
cd replay-events
export MATOMO_URL='https://my.matomo.url/'
export MATOMO_TOKEN=hex_string_here
./replay.sh
```

Remember to move or copy your (ndjson) access log into the directory prior to building.
(You can specify a different filename by changing the bind mount `source` passed to the `docker run` command in
`replay.sh`.)
