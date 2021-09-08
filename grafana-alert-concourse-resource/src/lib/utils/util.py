#!/usr/bin/env python

import sys
import time

from datetime import datetime

import requests
from requests import HTTPError


def eprint(message):
    print(message, file=sys.stderr)


def validate_source(source):
    if source.get("grafana_url") is None:
        eprint("[ERROR] grafana_url is not set")
        exit(1)
    if source.get("alert_id") is None:
        eprint("[ERROR] alert_id is not set")
        exit(1)


def call_grafana_api(source):
    grafana_url = source['grafana_url']
    alert_id = source['alert_id']
    eprint(f"Fetching alert annotations for alert ID '{alert_id}' from '{grafana_url}'")
    response = requests.get(
        f"{grafana_url}/api/annotations?alertId={alert_id}&from={one_week_ago_milliseconds()}&to={now_milliseconds()}"
    )

    try:
        response.raise_for_status()
        eprint("Success!")
    except HTTPError as e:
        eprint(f"[ERROR] HTTPError when calling Grafana API: {e}")
        exit(1)

    return response


def last_resolved_alert_version(grafana_response):
    response_json = grafana_response.json()
    eprint(response_json)
    sorted_annotations = sorted(response_json, key=lambda x: x['id'], reverse=True)
    try:
        # get a tuple of the first pair of 'ok'/'alerting' annotations in the list
        alert_annotations_tuple = next(
            (ann, sorted_annotations[sorted_annotations.index(ann) + 1]) for ann in sorted_annotations
            if ann['newState'] == 'ok' and ann['prevState'] == 'alerting'
        )
    except StopIteration:  # No alerts found
        eprint('No alert annotations found')
        return None
    except IndexError:  # The annotation after the last resolved annotation has dropped out of the time period fetched
        eprint('No matching "alerting" annotation found')
        return None

    eprint(f'Alert annotations found: {alert_annotations_tuple}')

    return {
        'start': milliseconds_to_iso8601(alert_annotations_tuple[1]['created']),
        'end': milliseconds_to_iso8601(alert_annotations_tuple[0]['created']),
        'name': alert_annotations_tuple[0]['alertName'],
    }


def now_milliseconds():
    return int(time.time() * 1000)


def one_week_ago_milliseconds():
    return int(now_milliseconds() - (60 * 60 * 24 * 7 * 1000))


def milliseconds_to_iso8601(milliseconds):
    return datetime.fromtimestamp(int(milliseconds) // 1000).isoformat() + 'Z'
