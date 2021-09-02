#!/usr/bin/env python

import json
import sys

from .utils import eprint


def main():
    input_json = json.loads(sys.stdin.read())
    requested_version = input_json.get("version")
    destination_dir = sys.argv[1]

    eprint(f"Version: {requested_version}")

    with open(f"{destination_dir}/grafana-alert", "w") as f:
        f.write(json.dumps(requested_version))

    print(json.dumps({"version": requested_version}))


if __name__ == '__main__':
    main()
