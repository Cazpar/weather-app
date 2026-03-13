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
    
    monkeypatch.setattr("app.routes.requests.get", mock_get)
    response = client.post("/weather", data={"city": "fakecityxyz"})
    assert b"Could not find" in response.data