import unittest
from unittest.mock import Mock, patch

import requests

from clients.http import ExternalServiceError, NotFoundError, get_json
from clients.rates import get_rate
from clients.weather import get_weather


def response(status, body, headers=None):
    result = Mock()
    result.status_code = status
    result.headers = headers or {}
    result.json.return_value = body
    return result


class ClientTests(unittest.TestCase):
    @patch("clients.http.time.sleep")
    @patch("clients.http.requests.get")
    def test_retries_timeout_and_503(self, get, sleep):
        get.side_effect = [
            requests.exceptions.Timeout(),
            response(503, {}),
            response(200, {"ok": True}),
        ]

        self.assertEqual(get_json("https://example.test"), {"ok": True})
        self.assertEqual(get.call_count, 3)
        self.assertEqual(sleep.call_count, 2)

    @patch("clients.http.time.sleep")
    @patch("clients.http.requests.get")
    def test_numeric_retry_after(self, get, sleep):
        get.side_effect = [
            response(429, {}, {"Retry-After": "2"}),
            response(200, {"ok": True}),
        ]

        get_json("https://example.test")
        sleep.assert_called_once_with(2.0)

    @patch("clients.http.time.sleep")
    @patch("clients.http.requests.get")
    def test_exhausted_retries(self, get, sleep):
        get.side_effect = requests.exceptions.ConnectionError()

        with self.assertRaises(ExternalServiceError):
            get_json("https://example.test")
        self.assertEqual(get.call_count, 3)

    @patch("clients.http.requests.get")
    def test_unknown_currency(self, get):
        get.return_value = response(422, {"message": "invalid currency"})

        with self.assertRaises(NotFoundError):
            get_rate("ZZZ")

    @patch("clients.http.requests.get")
    def test_valid_rate(self, get):
        get.return_value = response(200, {"base": "USD", "quote": "RUB", "rate": 92.15})

        self.assertEqual(get_rate("USD"), 92.15)

    @patch("clients.weather.get_json")
    def test_weather_parsing(self, get_json_mock):
        get_json_mock.side_effect = [
            {"results": [{"latitude": 55.75, "longitude": 37.62}]},
            {"current": {"temperature_2m": -3.2, "weather_code": 0}},
        ]

        self.assertEqual(
            get_weather("Moscow"),
            {"temp_c": -3.2, "description": "clear sky"},
        )

    @patch("clients.weather.get_json")
    def test_malformed_weather(self, get_json_mock):
        get_json_mock.side_effect = [
            {"results": [{"latitude": 55.75, "longitude": 37.62}]},
            {"current": {"weather_code": 0}},
        ]

        with self.assertRaises(ExternalServiceError):
            get_weather("Moscow")


if __name__ == "__main__":
    unittest.main()
