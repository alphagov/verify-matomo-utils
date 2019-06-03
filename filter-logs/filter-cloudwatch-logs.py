#!/usr/bin/env python3

import argparse
import datetime
import json


class CloudwatchMatomoNginxLogStats:
    def __init__(self):
        self.total_count = 0
        self.non_error_status_count = 0
        self.smokey_count = 0
        self.matomo_count = 0
        self.piwik_count = 0
        self.other_path_count = 0
        self.other_paths = set()
        self.hours = {}

    def log_ingested_at(self, ingestion_time):
        self.total_count += 1
        # grouping by hour, requires conversion from milliseconds
        parsed_timestamp = datetime.datetime.fromtimestamp(int(ingestion_time / 1000))
        hour_representation = parsed_timestamp.strftime('%Y-%m-%d %H')
        if hour_representation not in self.hours:
            self.hours[hour_representation] = 1
        else:
            self.hours[hour_representation] += 1

    def non_matomo_path(self, path):
        self.other_path_count += 1
        self.other_paths.add(path.split('?', 1)[0])

    def report(self):
        included = self.matomo_count + self.piwik_count
        excluded = self.non_error_status_count + self.smokey_count + self.other_path_count
        return (f'Encountered {self.total_count} messages, ({included} included, {excluded} excluded,) of which:'
            + f'\n\tnon-error status (excluded): {self.non_error_status_count}'
            + f'\n\tsmokey UA (excluded): {self.smokey_count}'
            + f'\n\tnon-matomo paths (excluded): {self.other_path_count}'
            + f'\n\tmatomo paths (included): {self.matomo_count}'
            + f'\n\tpiwik paths (included): {self.piwik_count}'
            + f'\nHours: {json.dumps(self.hours)}'
            + f'\nNon-matomo paths encountered: {json.dumps(list(self.other_paths))}'
        )


def append_to_file(file, thing):
    json.dump(thing, file)
    file.write('\n')


def append_many(path, iterable, getter=None):
    with open(path, 'a', encoding='utf8') as file:
        for thing in iterable:
            if getter:
                thing = getter(thing)
            append_to_file(file, thing)


def file_to_json(path):
    with open(path, 'r') as file:
        return json.load(file)
    return None


def parse(aws_log_event, stats):
    stats.log_ingested_at(aws_log_event['ingestionTime'])
    # See https://github.com/matomo-org/matomo-log-analytics/blob/ec1f9c2f0dcaf680a27a0ef2676c0d1ab45e1ae2/import_logs.py#L159-L162
    #  for context as to why the replacement is done
    try:
        return json.loads(aws_log_event['message'].replace('\\x', '\\u00'))
    except json.decoder.JSONDecodeError as e:
        print(f'Error encountered parsing log entry {aws_log_event["message"]}')
        print(stats.report())
        raise e


def should_include(request_details, stats):
    try:
        status = int(request_details['status'])
    except ValueError:
        stats.non_error_status_count += 1
        return False
    if status < 500:
        stats.non_error_status_count += 1
        return False
    if request_details['user_agent'] == 'Smokey Test':
        stats.smokey_count += 1
        return False
    path = request_details['path']
    if path[:11] == '/matomo.php':
        stats.matomo_count += 1
    elif path[:10] == '/piwik.php':
        stats.piwik_count += 1
    else:
        stats.non_matomo_path(path)
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
    stats = CloudwatchMatomoNginxLogStats()
    for event in aws_entries['events']:
        request_details = parse(event, stats)
        if should_include(request_details, stats):
            filtered_messages.append({
                'parsed_message': request_details,
                'event': event
            })
    # sort messages by timestamp, earliest first
    # see the requirements on https://matomo.org/docs/log-analytics-tool-how-to/
    filtered_messages.sort(key=(lambda m: m['event']['timestamp']))
    append_many(output_path, filtered_messages, getter=(lambda m: m['parsed_message']))
    print(stats.report())


if __name__ == "__main__":
    main()
