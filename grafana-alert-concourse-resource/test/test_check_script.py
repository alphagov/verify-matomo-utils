import io
import json
import sys
from unittest.mock import patch

from freezegun import freeze_time
import pytest
import requests_mock

from src.lib import check_script


@patch('sys.stdin')
class TestCheckScript:

    input_json = json.dumps({
        'source': {
            'grafana_url': 'https://grafana',
            'alert_id': '606',
        },

        'version': {
            'end':	'2021-05-26T16:01:25Z',
            'name':	'Matomo 5XX responses alert',
            'start': '2021-05-26T15:55:45Z'
        }
    })

    @freeze_time("2020-03-08")
    @requests_mock.Mocker(kw='req_mocker')
    def test_returns_a_version_containing_the_start_and_end_times_of_the_most_recent_alert(self, stdin_mock, **kwargs):
        stdin_mock.read.return_value = self.input_json
        kwargs['req_mocker'].get(
            'https://grafana/api/annotations?alertId=606&from=1583020800000&to=1583625600000',
            json=self.sample_response()
        )

        captured_stdout = io.StringIO()
        sys.stdout = captured_stdout

        check_script.main()

        sys.stdout = sys.__stdout__

        assert captured_stdout.getvalue() == '[{"start": "2021-08-18T14:55:17Z", "end": "2021-08-18T15:50:06Z", "name": "Matomo 5XX responses alert"}]\n'

    @freeze_time("1984-09-28")
    @requests_mock.Mocker(kw='req_mocker')
    def test_returns_a_version_containing_the_start_and_end_times_of_the_most_recent_alert_when_no_version_supplied(self, stdin_mock, **kwargs):
        no_version_input = json.loads(self.input_json)
        del no_version_input['version']
        kwargs['req_mocker'].get(
            'https://grafana/api/annotations?alertId=606&from=464572800000&to=465177600000',
            json=self.sample_response()
        )
        stdin_mock.read.return_value = json.dumps(no_version_input)

        captured_stdout = io.StringIO()
        sys.stdout = captured_stdout

        check_script.main()

        sys.stdout = sys.__stdout__

        assert captured_stdout.getvalue() == '[{"start": "2021-08-18T14:55:17Z", "end": "2021-08-18T15:50:06Z", "name": "Matomo 5XX responses alert"}]\n'

    @freeze_time("1984-09-28")
    @requests_mock.Mocker(kw='req_mocker')
    def test_returns_an_empty_array_when_no_alerts_found_and_no_version_supplied(self, stdin_mock, **kwargs):
        no_version_input = json.loads(self.input_json)
        del no_version_input['version']
        kwargs['req_mocker'].get(
            'https://grafana/api/annotations?alertId=606&from=464572800000&to=465177600000',
            json=[]
        )
        stdin_mock.read.return_value = json.dumps(no_version_input)

        captured_stdout = io.StringIO()
        sys.stdout = captured_stdout

        check_script.main()

        sys.stdout = sys.__stdout__

        assert captured_stdout.getvalue() == '[]\n'

    @freeze_time("1984-09-28")
    @requests_mock.Mocker(kw='req_mocker')
    def test_returns_supplied_version_when_no_alerts_found_and_version_supplied(self, stdin_mock, **kwargs):
        stdin_mock.read.return_value = self.input_json
        kwargs['req_mocker'].get(
            'https://grafana/api/annotations?alertId=606&from=464572800000&to=465177600000',
            json=[]
        )

        captured_stdout = io.StringIO()
        sys.stdout = captured_stdout

        check_script.main()

        sys.stdout = sys.__stdout__

        assert captured_stdout.getvalue() == '[{"end": "2021-05-26T16:01:25Z", "name": "Matomo 5XX responses alert", "start": "2021-05-26T15:55:45Z"}]\n'

    @freeze_time("1984-09-28")
    @requests_mock.Mocker(kw='req_mocker')
    def test_returns_version_when_latest_alert_is_supplied_version(self, stdin_mock, **kwargs):
        stdin_mock.read.return_value = self.input_json
        kwargs['req_mocker'].get(
            'https://grafana/api/annotations?alertId=606&from=464572800000&to=465177600000',
            json=[]
        )

        captured_stdout = io.StringIO()
        sys.stdout = captured_stdout

        check_script.main()

        sys.stdout = sys.__stdout__

        assert captured_stdout.getvalue() == '[{"end": "2021-05-26T16:01:25Z", "name": "Matomo 5XX responses alert", "start": "2021-05-26T15:55:45Z"}]\n'


    @freeze_time("1984-09-28")
    @requests_mock.Mocker(kw='req_mocker')
    def test_returns_supplied_version_when_no_alerts_found_and_version_supplied(self, stdin_mock, **kwargs):
        stdin_mock.read.return_value = self.input_json
        kwargs['req_mocker'].get(
            'https://grafana/api/annotations?alertId=606&from=464572800000&to=465177600000',
            json=self.sample_response()[2:]
        )

        captured_stdout = io.StringIO()
        sys.stdout = captured_stdout

        check_script.main()

        sys.stdout = sys.__stdout__

        assert captured_stdout.getvalue() == '[{"end": "2021-05-26T16:01:25Z", "name": "Matomo 5XX responses alert", "start": "2021-05-26T15:55:45Z"}]\n'

    @freeze_time("1984-09-28")
    @requests_mock.Mocker(kw='req_mocker')
    def test_returns_no_new_version_if_half_of_annotation_pair_is_missing(self, stdin_mock, **kwargs):
        no_version_input = json.loads(self.input_json)
        del no_version_input['version']
        stdin_mock.read.return_value = json.dumps(no_version_input)
        kwargs['req_mocker'].get(
            'https://grafana/api/annotations?alertId=606&from=464572800000&to=465177600000',
            json=[self.sample_response()[0]]
        )

        captured_stdout = io.StringIO()
        sys.stdout = captured_stdout

        check_script.main()

        sys.stdout = sys.__stdout__
        assert captured_stdout.getvalue() == '[]\n'


    def test_exits_if_invalid_source_input(self, stdin_mock):
        for source_key in ['grafana_url', 'alert_id']:
            invalid_input_json = json.loads(self.input_json)
            invalid_input_json['source'][source_key] = None
            stdin_mock.read.return_value = json.dumps(invalid_input_json)

            captured_stderr = io.StringIO()
            sys.stderr = captured_stderr

            with pytest.raises(SystemExit) as e:
                check_script.main()

            sys.stderr = sys.__stderr__

            assert e.value.code == 1
            assert captured_stderr.getvalue() == f"[ERROR] {source_key} is not set\n"

    @freeze_time("1984-09-28")
    @requests_mock.Mocker(kw='req_mocker')
    def test_exits_if_bad_http_response(self, stdin_mock, **kwargs):
        stdin_mock.read.return_value = self.input_json
        kwargs['req_mocker'].get(
            'https://grafana/api/annotations?alertId=606&from=464572800000&to=465177600000',
            status_code=400,
            reason="Oh no..."
        )

        captured_stderr = io.StringIO()
        sys.stderr = captured_stderr

        with pytest.raises(SystemExit) as e:
            check_script.main()

        sys.stderr = sys.__stderr__

        assert e.value.code == 1
        assert captured_stderr.getvalue() == "Fetching alert annotations for alert ID '606' from 'https://grafana'\n" \
            "[ERROR] HTTPError when calling Grafana API: " \
            "400 Client Error: Oh no... for url: https://grafana/api/annotations?alertId=606&from=464572800000&to=465177600000\n"

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
