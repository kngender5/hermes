import json
import pytest
import urllib.error
from unittest.mock import MagicMock, patch

import sys
import os

# Add the scripts directory to the path so we can import maps_client
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

import maps_client


@pytest.fixture
def mock_sleep(mocker):
    return mocker.patch("time.sleep")


@pytest.fixture
def mock_error_exit(mocker):
    # Mock error_exit to just raise an exception to stop execution in tests
    def side_effect(msg):
        raise SystemExit(msg)
    return mocker.patch("maps_client.error_exit", side_effect=side_effect)


class MockResponse:
    def __init__(self, data):
        self.data = data
        self.read_called = False

    def read(self):
        self.read_called = True
        return self.data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def test_http_get_success(mocker):
    mock_urlopen = mocker.patch("urllib.request.urlopen")
    mock_response = MockResponse(b'{"status": "ok"}')
    mock_urlopen.return_value = mock_response

    result = maps_client.http_get("http://example.com", retries=1)

    assert result == {"status": "ok"}
    mock_urlopen.assert_called_once()
    assert mock_response.read_called


def test_http_get_http_error_no_retry(mocker, mock_error_exit):
    mock_urlopen = mocker.patch("urllib.request.urlopen")
    # Simulate a 404 error, which shouldn't be retried
    mock_urlopen.side_effect = urllib.error.HTTPError(
        url="http://example.com", code=404, msg="Not Found", hdrs={}, fp=None
    )

    with pytest.raises(SystemExit) as excinfo:
        maps_client.http_get("http://example.com", retries=3)

    assert "HTTP 404: Not Found" in str(excinfo.value)
    mock_urlopen.assert_called_once()
    mock_error_exit.assert_called_once()


def test_http_get_http_error_retry(mocker, mock_error_exit, mock_sleep):
    mock_urlopen = mocker.patch("urllib.request.urlopen")
    # Simulate a 503 error, which should be retried
    error_503 = urllib.error.HTTPError(
        url="http://example.com", code=503, msg="Service Unavailable", hdrs={}, fp=None
    )
    mock_urlopen.side_effect = [error_503, error_503, MockResponse(b'{"status": "ok"}')]

    result = maps_client.http_get("http://example.com", retries=3)

    assert result == {"status": "ok"}
    assert mock_urlopen.call_count == 3
    assert mock_sleep.call_count == 2
    mock_error_exit.assert_not_called()


def test_http_get_url_error_retry(mocker, mock_error_exit, mock_sleep):
    mock_urlopen = mocker.patch("urllib.request.urlopen")
    # Simulate a URLError, which should be retried
    error_url = urllib.error.URLError("timeout")
    mock_urlopen.side_effect = [error_url, MockResponse(b'{"status": "ok"}')]

    result = maps_client.http_get("http://example.com", retries=3)

    assert result == {"status": "ok"}
    assert mock_urlopen.call_count == 2
    assert mock_sleep.call_count == 1
    mock_error_exit.assert_not_called()


def test_http_get_invalid_json(mocker, mock_error_exit, mock_sleep):
    mock_urlopen = mocker.patch("urllib.request.urlopen")
    mock_urlopen.side_effect = [MockResponse(b'invalid json'), MockResponse(b'{"status": "ok"}')]

    result = maps_client.http_get("http://example.com", retries=3)

    assert result == {"status": "ok"}
    assert mock_urlopen.call_count == 2
    assert mock_sleep.call_count == 1
    mock_error_exit.assert_not_called()


def test_http_get_all_retries_fail(mocker, mock_error_exit, mock_sleep):
    mock_urlopen = mocker.patch("urllib.request.urlopen")
    mock_urlopen.side_effect = urllib.error.URLError("timeout")

    with pytest.raises(SystemExit) as excinfo:
        maps_client.http_get("http://example.com", retries=3)

    assert "Request failed after 3 attempts" in str(excinfo.value)
    assert mock_urlopen.call_count == 3
    assert mock_sleep.call_count == 3
    mock_error_exit.assert_called_once()


def test_http_get_silent_failure(mocker, mock_sleep):
    mock_urlopen = mocker.patch("urllib.request.urlopen")
    mock_urlopen.side_effect = urllib.error.HTTPError(
        url="http://example.com", code=404, msg="Not Found", hdrs={}, fp=None
    )

    with pytest.raises(RuntimeError) as excinfo:
        maps_client.http_get("http://example.com", retries=3, silent=True)

    assert "HTTP 404: Not Found" in str(excinfo.value)


# Tests for http_get_text
def test_http_get_text_success(mocker):
    mock_urlopen = mocker.patch("urllib.request.urlopen")
    mock_response = MockResponse(b'some text data')
    mock_urlopen.return_value = mock_response

    result = maps_client.http_get_text("http://example.com", retries=1)

    assert result == "some text data"
    mock_urlopen.assert_called_once()


def test_http_get_text_http_error_retry(mocker, mock_error_exit, mock_sleep):
    mock_urlopen = mocker.patch("urllib.request.urlopen")
    error_502 = urllib.error.HTTPError(
        url="http://example.com", code=502, msg="Bad Gateway", hdrs={}, fp=None
    )
    mock_urlopen.side_effect = [error_502, MockResponse(b'success text')]

    result = maps_client.http_get_text("http://example.com", retries=3)

    assert result == "success text"
    assert mock_urlopen.call_count == 2
    assert mock_sleep.call_count == 1


# Tests for http_post
def test_http_post_success(mocker):
    mock_urlopen = mocker.patch("urllib.request.urlopen")
    mock_response = MockResponse(b'{"result": "created"}')
    mock_urlopen.return_value = mock_response

    result = maps_client.http_post("http://example.com", data_str="key=value", retries=1)

    assert result == {"result": "created"}
    mock_urlopen.assert_called_once()
    # verify that a POST request was made (data was provided)
    req = mock_urlopen.call_args[0][0]
    assert req.data == b"key=value"


def test_http_post_http_error_no_retry(mocker, mock_error_exit):
    mock_urlopen = mocker.patch("urllib.request.urlopen")
    mock_urlopen.side_effect = urllib.error.HTTPError(
        url="http://example.com", code=400, msg="Bad Request", hdrs={}, fp=None
    )

    with pytest.raises(SystemExit) as excinfo:
        maps_client.http_post("http://example.com", data_str="key=value", retries=3)

    assert "HTTP 400: Bad Request" in str(excinfo.value)
    mock_urlopen.assert_called_once()


def test_http_post_invalid_json_retry(mocker, mock_error_exit, mock_sleep):
    mock_urlopen = mocker.patch("urllib.request.urlopen")
    mock_urlopen.side_effect = [MockResponse(b'invalid'), MockResponse(b'{"result": "ok"}')]

    result = maps_client.http_post("http://example.com", data_str="key=value", retries=3)

    assert result == {"result": "ok"}
    assert mock_urlopen.call_count == 2
    assert mock_sleep.call_count == 1
