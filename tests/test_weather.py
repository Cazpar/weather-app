from datetime import datetime, timezone

import pytest

from app.weather import (
    build_weather_data,
    fetch_weather_by_coords,
    fetch_weather,
    fetch_suggestions,
)


def make_weather_payload(
    *,
    weather_id: int = 800,
    icon: str = "01d",
    sunrise: int = 1_700_000_000,
    sunset: int = 1_700_003_600,
    current_time: int = 1_700_002_000,
):
    """Helper to build a minimal OpenWeather payload."""
    return {
        "name": "Testville",
        "weather": [
            {
                "id": weather_id,
                "description": "clear sky",
                "icon": icon,
            }
        ],
        "sys": {
            "country": "US",
            "sunrise": sunrise,
            "sunset": sunset,
        },
        "main": {
            "temp": 72.5,
            "feels_like": 70.0,
            "humidity": 40,
        },
        "wind": {
            "speed": 5.5,
        },
        "dt": current_time,
    }


def test_build_weather_data_daytime_and_cloudiness_flags():
    payload = make_weather_payload(weather_id=802)  # scattered clouds

    result = build_weather_data(payload, state="CA")

    assert result["city"] == "Testville"
    assert result["state"] == "CA"
    assert result["country"] == "US"
    assert result["temperature"] == 72.5
    assert result["feels_like"] == 70.0
    assert result["humidity"] == 40
    assert result["wind_speed"] == 5.5

    # dt is between sunrise and sunset in helper -> should be daytime
    assert result["is_night"] is False

    # 802 falls in the cloud range
    assert result["condition"] == "clouds"
    assert result["is_cloudy"] is True

    # We don't assert exact moon fields because they depend on datetime.now
    assert "moon_phase" in result
    assert "moon_illumination" in result


def test_build_weather_data_night_time_flag():
    # Current time before sunrise -> should be night
    payload = make_weather_payload(
        sunrise=1_700_000_000,
        sunset=1_700_010_000,
        current_time=1_699_999_000,
    )

    result = build_weather_data(payload)
    assert result["is_night"] is True


def test_fetch_weather_by_coords_success(monkeypatch):
    payload = make_weather_payload()

    class MockResponse:
        status_code = 200

        def json(self):
            return payload

    def mock_get(url, params):
        return MockResponse()

    monkeypatch.setattr("app.weather.requests.get", mock_get)

    data, error = fetch_weather_by_coords(10.0, 20.0)

    assert error is None
    assert data is not None
    assert data["city"] == "Testville"


def test_fetch_weather_by_coords_error_status(monkeypatch):
    class MockResponse:
        status_code = 500

        def json(self):
            return {}

    def mock_get(url, params):
        return MockResponse()

    monkeypatch.setattr("app.weather.requests.get", mock_get)

    data, error = fetch_weather_by_coords(10.0, 20.0)

    assert data is None
    assert "Weather data unavailable" in error


def test_fetch_weather_geocoding_no_results(monkeypatch):
    """Directly exercise the 'no city found' branch."""

    class MockGeoResponse:
        status_code = 200

        def json(self):
            return []

    def mock_get(url, params):
        # First call (geocoding) returns empty list
        return MockGeoResponse()

    monkeypatch.setattr("app.weather.requests.get", mock_get)

    data, error = fetch_weather("Nowhereville")

    assert data is None
    assert "Could not find 'Nowhereville'" in error


def test_fetch_suggestions_success(monkeypatch):
    payload = [
        {
            "name": "Portland",
            "state": "Oregon",
            "country": "US",
            "lat": 45.5234,
            "lon": -122.6762,
        },
        {
            "name": "Portland",
            "state": "Maine",
            "country": "US",
            "lat": 43.6591,
            "lon": -70.2568,
        },
    ]

    class MockResponse:
        status_code = 200

        def json(self):
            return payload

    def mock_get(url, params):
        return MockResponse()

    monkeypatch.setattr("app.weather.requests.get", mock_get)

    results = fetch_suggestions("Port")

    assert len(results) == 2
    assert results[0]["label"] == "Portland, Oregon, US"
    assert results[0]["lat"] == 45.5234
    assert results[0]["lon"] == -122.6762


def test_fetch_suggestions_error_status(monkeypatch):
    class MockResponse:
        status_code = 500

        def json(self):
            return []

    def mock_get(url, params):
        return MockResponse()

    monkeypatch.setattr("app.weather.requests.get", mock_get)

    results = fetch_suggestions("Port")

    assert results == []

