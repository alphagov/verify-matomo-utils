#!/usr/bin/env python3

import argparse
import json


def append_to_file(file, thing):
    json.dump(thing, file)
    file.write('\n')


def append_many(path, iterable):
    with open(path, 'a', encoding='utf8') as file:
        for thing in iterable:
            append_to_file(file, thing)


def file_to_json(path):
    with open(path, 'r') as file:
        return json.load(file)
    return None


def parse(aws_log_event):
    # See https://github.com/matomo-org/matomo-log-analytics/blob/ec1f9c2f0dcaf680a27a0ef2676c0d1ab45e1ae2/import_logs.py#L159-L162
    #  for context as to why the replacement is done
    return json.loads(aws_log_event['message'].replace('\\x', '\\u00'))


def should_include(request_details):
    try:
        status = int(request_details['status'])
    except ValueError:
        return False
    if status < 500:
        return False
    if request_details['user_agent'] == 'Smokey Test':
        return False
    path = request_details['path']
    if not (path[:11] == '/matomo.php' or path[:10] == '/piwik.php'):
        return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path',
            help='Path to the file downloaded from a call to `aws logs filter-log-events`')
    args = parser.parse_args()
    input_path = args.input_path
    output_path = input_path + '.ndjson'
    aws_entries = file_to_json(input_path)
    if not aws_entries:
        print('Failed to parse file.')
        return
    filtered_messages = []
    for event in aws_entries['events']:
        request_details = parse(event)
        if should_include(request_details):
            filtered_messages.append(request_details)
    append_many(output_path, filtered_messages)


if __name__ == "__main__":
    main()
