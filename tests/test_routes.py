import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_homepage_loads(client):
    response = client.get("/")
    assert response.status_code == 200

def test_homepage_contains_form(client):
    response = client.get("/")
    assert b"city" in response.data

def test_weather_requires_city(client):
    response = client.post("/weather", data={"city": ""})
    assert response.status_code == 200
    
def test_invalid_city_returns_error(client, monkeypatch):
    def mock_get(url, params):
        class MockResponse:
            status_code = 200
            def json(self):
                return []
        return MockResponse()
    
    monkeypatch.setattr("app.weather.requests.get", mock_get)
    response = client.post("/weather", data={"city": "fakecityxyz"})
    assert b"Could not find" in response.data


def test_suggest_short_query_returns_empty_list(client):
    response = client.get("/suggest?q=ab")
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"suggestions": []}


def test_suggest_returns_results(client, monkeypatch):
    mock_results = [
        {
            "label": "Portland, Oregon, US",
            "value": "Portland, Oregon, US",
            "lat": 45.5234,
            "lon": -122.6762,
            "state": "Oregon",
        }
    ]

    def mock_fetch_suggestions(query):
        assert query == "Port"
        return mock_results

    monkeypatch.setattr("app.routes.fetch_suggestions", mock_fetch_suggestions)

    response = client.get("/suggest?q=Port")
    assert response.status_code == 200
    data = response.get_json()
    assert data["suggestions"] == mock_results


def test_weather_by_coords_success(client, monkeypatch):
    def mock_fetch_weather_by_coords(lat, lon, state=""):
        assert lat == "10.0"
        assert lon == "20.0"
        assert state == "CA"
        return (
            {
                "city": "Testville",
                "state": "CA",
                "country": "US",
                "temperature": 70.0,
                "feels_like": 68.0,
                "description": "clear sky",
                "humidity": 40,
                "wind_speed": 5.0,
                "icon": "clear-day.svg",
                "condition": "clear",
                "is_night": False,
                "moon_phase": "full",
                "moon_illumination": 100,
                "is_cloudy": False,
            },
            None,
        )

    monkeypatch.setattr("app.routes.fetch_weather_by_coords", mock_fetch_weather_by_coords)

    response = client.post(
        "/weather-by-coords",
        data={"lat": "10.0", "lon": "20.0", "state": "CA"},
    )

    assert response.status_code == 200
    assert b"Testville" in response.data


def test_weather_by_coords_error(client, monkeypatch):
    def mock_fetch_weather_by_coords(lat, lon, state=""):
        return None, "Weather data unavailable. Error 500."

    monkeypatch.setattr("app.routes.fetch_weather_by_coords", mock_fetch_weather_by_coords)

    response = client.post(
        "/weather-by-coords",
        data={"lat": "10.0", "lon": "20.0", "state": "CA"},
    )

    assert response.status_code == 200
    assert b"Weather data unavailable" in response.data