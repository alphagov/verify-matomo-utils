# Grafana Alert Concourse Resource

[Concourse][concourse] resource for checking resolved [Grafana][grafana] alerts.

The intended use it to allow triggering a pipeline once an alert has been resolved. This is useful for running a cleanup
script which would otherwise need to be run by hand.

This resource Grafana's annotations API, rather than the alerting API. This is because the alerting API has no history of
alerts. The annotations API provides a detailed history of when alerts have been triggered and then resolved.

## Source Configuration

* `grafana_url`: *Required*<br/>The URL of the Grafana instance.
* `alert_id`: *Required*<br/>The ID of the alert to check - this can be found using the Grafana alerts API.

## Behaviour

### `check`:

Fetches the annotations for the configured alert for the previous week. Reports a new version if there is a new pair of 
'alerting' and 'ok' annotations.

The new version contains the extracted creation time of the annotations as 'start' and 'end' timestamps.

### `in`:

Takes the requested version and writes the JSON to file called `grafana-alert` in the directory provided by Concourse.

### `out`: Not implemented

<hr>

## Example Configuration

### Resource Type

```
resource_types:
  - name: grafana-alert
    type: registry-image
    source:
      repository: ghcr.io/alphagov/verify/grafana-alert-concourse-resource
      tag: latest
```

### Resource

```
resources:
  - name: matomo-500-alert
    type: grafana-alert
    source:
      grafana_url: https://grafana.tools.signin.service.gov.uk
      alert_id: 518
```

### Plan

```
jobs:
  - name: run-cleanup-script-after-alert
    plan:
      - get: matomo-500-alert
        trigger: true
      - task: run-script
        image: some-base-image
        config:
          platform: linux
          inputs:
            - name: matomo-500-alert
          run:
            path: bash
            args:
              - -c
              - |
                start_time=$(cat matomo-500-alert/grafana-alert | jq -r .start)
                end_time=$(cat matomo-500-alert/grafana-alert | jq -r .end)
                
                ./clean-up.sh $start_time $end_time
```

## Running the tests

Install required dependencies with:

```
pip install -r requirements-dev.txt
```

Then from the root of the repo run:

```
python -m pytest
```

[grafana]: https://grafana.com
[concourse]: https://concourse-ci.org
