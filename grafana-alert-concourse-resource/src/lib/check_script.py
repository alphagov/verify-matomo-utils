#!/usr/bin/env python

import json
import sys

from .utils import call_grafana_api, last_resolved_alert_version, validate_source


def main():
    input_json = json.loads(sys.stdin.read())
    source = input_json.get("source")
    supplied_version = input_json.get("version")

    validate_source(source)
    response = call_grafana_api(source)
    latest_version = last_resolved_alert_version(response)

    if not supplied_version:
        print(json.dumps([latest_version]) if latest_version else json.dumps([]))
    else:
        print(json.dumps([latest_version])
              if latest_version and latest_version != supplied_version
              else json.dumps([supplied_version])
              )


if __name__ == '__main__':
    main()
