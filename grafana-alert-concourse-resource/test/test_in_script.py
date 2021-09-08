import io
import json
import sys
from unittest.mock import patch

from freezegun import freeze_time
import pytest
import requests_mock

from src.lib import in_script


@pytest.fixture(scope="session")
def temp_dir(tmpdir_factory):
    dirname = tmpdir_factory.mktemp('fake_concourse_dir')
    return dirname


@patch('sys.stdin')
class TestInScript:

    input_json = json.dumps({
        'version': {
            'end':	'2021-05-26T16:01:25Z',
            'name':	'Matomo 5XX responses alert',
            'start': '2021-05-26T15:55:45Z'
        }
    })

    @freeze_time("2020-03-08")
    @requests_mock.Mocker(kw='req_mocker')
    def test_writes_the_supplied_version_to_file_and_stdout(self, stdin_mock, temp_dir, **kwargs):
        with patch.object(sys, 'argv', ['_', temp_dir]):
            stdin_mock.read.return_value = self.input_json
            kwargs['req_mocker'].get(
                'https://grafana/api/annotations?alertId=606&from=1583020800000&to=1583625600000',
                json=self.sample_response()
            )

            captured_stdout = io.StringIO()
            sys.stdout = captured_stdout

            in_script.main()

            sys.stdout = sys.__stdout__

            assert captured_stdout.getvalue() == '{"version": {"end": "2021-05-26T16:01:25Z", "name": "Matomo 5XX responses alert", "start": "2021-05-26T15:55:45Z"}}\n'

            with open(f"{temp_dir}/grafana-alert", "r") as f:
                file_content = [line.strip() for line in f.readlines()][0]
                assert file_content == '{"end": "2021-05-26T16:01:25Z", "name": "Matomo 5XX responses alert", "start": "2021-05-26T15:55:45Z"}'

    def sample_response(self):
        return [
            {
                "id": 9665,
                "alertName": "Matomo 5XX responses alert",
                "newState": "ok",
                "prevState": "alerting",
                "created": 1629301806142,
            },
            {
                "id": 9661,
                "alertName": "Matomo 5XX responses alert",
                "newState": "alerting",
                "prevState": "ok",
                "created": 1629298517126,
            },
            {
                "id": 9386,
                "alertName": "Matomo 5XX responses alert",
                "newState": "ok",
                "prevState": "alerting",
                "created": 1622044885112,
            },
            {
                "id": 9385,
                "alertName": "Matomo 5XX responses alert",
                "newState": "alerting",
                "prevState": "ok",
                "created": 1622044545175,
            }
        ]








