import json
from unittest.mock import patch, MagicMock

import pytest
from django.test import RequestFactory

from .views import weather


FAKE_WEATHER = {
    "name": "Krommenie",
    "main": {"temp": 12.3},
    "weather": [{"description": "light rain"}],
}
FAKE_FORECAST = {"list": [{"pop": 0.4}]}


def fake_get(url, *args, **kwargs):
    """Return a different fake response depending on which endpoint is called."""
    mock = MagicMock()
    mock.json.return_value = FAKE_FORECAST if "/forecast" in url else dict(FAKE_WEATHER)
    return mock


@pytest.fixture
def rf():
    return RequestFactory()


@pytest.fixture(autouse=True)
def api_key(settings):
    settings.OPENWEATHER_API_KEY = "test-key"


@patch("requests.get", side_effect=fake_get)
def test_weather_returns_data_with_pop(mock_get, rf):
    response = weather(rf.get("/weather/"))
    data = json.loads(response.content)

    assert response.status_code == 200
    assert data["name"] == "Krommenie"
    assert data["main"]["temp"] == 12.3
    assert data["pop"] == 0.4  # merged in from the forecast call


@patch("requests.get", side_effect=fake_get)
def test_weather_uses_default_city(mock_get, rf):
    weather(rf.get("/weather/"))

    called_urls = [call.args[0] for call in mock_get.call_args_list]
    assert all("q=Krommenie" in url for url in called_urls)


@patch("requests.get", side_effect=fake_get)
def test_weather_uses_city_from_query_param(mock_get, rf):
    weather(rf.get("/weather/", {"city": "Amsterdam"}))

    called_urls = [call.args[0] for call in mock_get.call_args_list]
    assert all("q=Amsterdam" in url for url in called_urls)


@patch("requests.get", side_effect=fake_get)
def test_weather_calls_both_endpoints_with_api_key(mock_get, rf):
    weather(rf.get("/weather/"))

    called_urls = [call.args[0] for call in mock_get.call_args_list]
    assert mock_get.call_count == 2
    assert any("/data/2.5/weather" in url for url in called_urls)
    assert any("/data/2.5/forecast" in url for url in called_urls)
    assert all("appid=test-key" in url for url in called_urls)
    assert all("units=metric" in url for url in called_urls)