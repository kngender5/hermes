import pytest
from unittest.mock import patch
import urllib.error
import socket
import json

import maps_client

@patch('maps_client.time.sleep')
@patch('maps_client.urllib.request.urlopen')
def test_http_get_http_error(mock_urlopen, mock_sleep, capsys):
    mock_urlopen.side_effect = urllib.error.HTTPError(
        url="http://example.com",
        code=503,
        msg="Service Unavailable",
        hdrs={},
        fp=None
    )

    with pytest.raises(SystemExit):
        maps_client.http_get("http://example.com", retries=2)

    assert mock_sleep.call_count == 2
    captured = capsys.readouterr()
    assert "HTTP 503: Service Unavailable for http://example.com" in captured.out

@patch('maps_client.time.sleep')
@patch('maps_client.urllib.request.urlopen')
def test_http_get_url_error(mock_urlopen, mock_sleep, capsys):
    mock_urlopen.side_effect = urllib.error.URLError(reason="Name or service not known")

    with pytest.raises(SystemExit):
        maps_client.http_get("http://example.com", retries=2)

    assert mock_sleep.call_count == 2
    captured = capsys.readouterr()
    assert "URL error: Name or service not known" in captured.out

@patch('maps_client.time.sleep')
@patch('maps_client.urllib.request.urlopen')
def test_http_get_socket_timeout(mock_urlopen, mock_sleep, capsys):
    mock_urlopen.side_effect = socket.timeout("timed out")

    with pytest.raises(SystemExit):
        maps_client.http_get("http://example.com", retries=2)

    assert mock_sleep.call_count == 2
    captured = capsys.readouterr()
    assert "Connection error: timed out" in captured.out

@patch('maps_client.time.sleep')
@patch('maps_client.urllib.request.urlopen')
def test_http_get_connection_error(mock_urlopen, mock_sleep, capsys):
    mock_urlopen.side_effect = ConnectionError("Connection refused")

    with pytest.raises(SystemExit):
        maps_client.http_get("http://example.com", retries=2)

    assert mock_sleep.call_count == 2
    captured = capsys.readouterr()
    assert "Connection error: Connection refused" in captured.out

@patch('maps_client.time.sleep')
@patch('maps_client.urllib.request.urlopen')
def test_http_get_json_decode_error(mock_urlopen, mock_sleep, capsys):
    # Setup mock response to return invalid json
    mock_response = mock_urlopen.return_value.__enter__.return_value
    mock_response.read.return_value = b"invalid json"

    with pytest.raises(SystemExit):
        maps_client.http_get("http://example.com", retries=2)

    assert mock_sleep.call_count == 2
    captured = capsys.readouterr()
    assert "JSON parse error" in captured.out
