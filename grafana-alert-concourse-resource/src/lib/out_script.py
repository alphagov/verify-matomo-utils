#!/usr/bin/env python

import json

from .utils import eprint


def main():
    eprint("Out not supported")
    print(json.dumps({"version": None}))


if __name__ == '__main__':
    main()

