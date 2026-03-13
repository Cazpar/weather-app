import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from app.utils import (
    get_weather_icon,
    get_condition_class,
    get_moon_phase,
    get_moon_illumination
)

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch_weather_by_coords(lat, lon, state=""):
    weather_response = requests.get(WEATHER_URL, params={
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "imperial"
    })

    if weather_response.status_code != 200:
        return None, f"Weather data unavailable. Error {weather_response.status_code}."

    return build_weather_data(weather_response.json(), state=state), None


def fetch_weather(city):
    geo_response = requests.get(GEO_URL, params={
        "q": city,
        "limit": 1,
        "appid": API_KEY
    })

    if geo_response.status_code != 200 or len(geo_response.json()) == 0:
        return None, f"Could not find '{city}'. Please check the city name and try again."

    geo_data = geo_response.json()[0]
    lat = geo_data["lat"]
    lon = geo_data["lon"]
    state = geo_data.get("state", "")

    return fetch_weather_by_coords(lat, lon, state=state)


def build_weather_data(data, state=""):
    weather_id = data["weather"][0]["id"]
    icon_code = data["weather"][0]["icon"]
    sunrise = data["sys"]["sunrise"]
    sunset = data["sys"]["sunset"]
    current_time = data["dt"]
    is_night = current_time < sunrise or current_time > sunset
    now_utc = datetime.now(timezone.utc)

    return {
        "city": data["name"],
        "state": state,
        "country": data["sys"]["country"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "description": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "icon": get_weather_icon(weather_id, icon_code),
        "condition": get_condition_class(weather_id),
        "is_night": is_night,
        "moon_phase": get_moon_phase(now_utc),
        "moon_illumination": get_moon_illumination(now_utc),
        "is_cloudy": 801 <= weather_id <= 804 or weather_id == 741
    }

def fetch_suggestions(query):
    response = requests.get(GEO_URL, params={
        "q": query,
        "limit": 5,
        "appid": API_KEY
    })

    if response.status_code != 200:
        return []

    results = []
    for item in response.json():
        city = item.get("name", "")
        state = item.get("state", "")
        country = item.get("country", "")
        lat = item.get("lat")
        lon = item.get("lon")

        label = city
        if state:
            label += f", {state}"
        if country:
            label += f", {country}"

        results.append({
            "label": label,
            "value": label,
            "lat": lat,
            "lon": lon,
            "state": state
        })

    return results