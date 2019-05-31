# verify-matomo-utils

Collection of tools used for interacting with Matomo (formerly called Piwik)

## What is here?

This is just a collection of helper scripts.
The current intention is to make it easier to replay data into Matomo from Nginx logs in CloudWatch.
More details about how to use them are included in other documentation.
There is no context in this repo to keep it as generic as possible.
(i.e. it shouldn't be exclusive to any individual Matomo setup.)

### download-logs

This script can be used to download logs from AWS CloudWatch.
It assumes the logs in question are inside a log group called "matomo".
Pass it two millisecond timestamps and it will download any errored requests from Nginx between those timestamps.
For example, to get logs from between 9:32 and 9:49 on 2019-01-01, pass in `1546507920000` and `1546508999999`:

```
cd download-logs
./download.sh 1546507920000 1546508999999
```

The script currently prompts you to continue, advising that you specify `--log-stream-name` arguments.
Doing so will make the request faster, since it only has to check the log streams specified.
If you don't know the streams that need including, or you want to be sure you get all logs within that timestamp, it should be fine to continue without these, but be aware the request will take longer as a result.
(If it's running for 10+ minutes for 150k log events across a period of a day, then something might be up.)

The script writes its output to a file named `aws_logs.txt` in the current directory.

### filter-logs

This script can be used to transform the output of `download-logs` back into an Nginx JSON format.
It essentially strips the wrapper from the response to `download-logs` above, and then transforms the JSON array of events (where each element spans multiple lines) into a newline-delimited JSON (ndjson: each event is a separate JSON entity, on a single line) that the Matomo log analytics script can ingest.
It is a Python 3 script, and expects to be passed as an argument a single file to transform, for example:

```
python3 filter-logs/filter-cloudwatch-logs.py download-logs/aws_logs.txt
```

By default, the above command would output a file `download-logs/aws_logs.txt.ndjson`.
Note that if that output file already exists, the transformed output will be appended, rather than overwrite the existing data.

### replay-events

This is essentially a Dockerfile used to define an environment with Python 2 to run the Matomo log analytics script.
A fork is being used to handle `X-Forwarded-For` headers as given by AWS Application ELBs.
The command itself has to be run manually once inside the docker image, as token authentication using Matomo hasn't worked in testing thus far, so authentication credentials need to be supplied directly.
An example workflow might be something like this:

```
mv download-logs/aws_logs.txt.ndjson replay-events/access.log
cd replay-events
docker build -t matomo-replay-events .
docker run --rm -it matomo-replay-events
# inside docker container:
python -u /log-analytics/import_logs.py \
    --url=https://your.matomo.url/ \
    --log-format-name=nginx_json \
    --replay-tracking \
    --enable-static \
    --enable-bots \
    --enable-reverse-dns \
    --recorders=2 \
    --login=matomo-username \
    --password='matomo-password' \
    /access.log
```

Remember to move or copy your (ndjson) access log into the directory prior to building.
(You can specify a different filename by changing the Dockerfile.)
