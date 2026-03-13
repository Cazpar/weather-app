import os
import requests
from flask import Blueprint, render_template, request
from dotenv import load_dotenv
import math
from datetime import datetime, timezone

load_dotenv()

main = Blueprint("main", __name__)

API_KEY = os.getenv("OPENWEATHER_API_KEY")
GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/weather", methods=["POST"])
def weather():
    city = request.form.get("city")

    # Step 1: Convert city name to coordinates
    geo_response = requests.get(GEO_URL, params={
        "q": city,
        "limit": 1,
        "appid": API_KEY
    })


    if geo_response.status_code != 200 or len(geo_response.json()) == 0:
        error = f"Could not find '{city}'. Please check the city name and try again."
        return render_template("index.html", error=error)

    geo_data = geo_response.json()[0]
    lat = geo_data["lat"]
    lon = geo_data["lon"]

    # Step 2: Get weather using coordinates
    weather_response = requests.get(WEATHER_URL, params={
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "imperial"
    })

    if weather_response.status_code != 200:
        error = f"Weather data unavailable. Error {weather_response.status_code}."
        return render_template("index.html", error=error)

    data = weather_response.json()

    weather_id = data["weather"][0]["id"]
    icon_code = data["weather"][0]["icon"]
    sunrise = data["sys"]["sunrise"]
    sunset = data["sys"]["sunset"]
    current_time = data["dt"]
    is_night = current_time < sunrise or current_time > sunset

    now_utc = datetime.now(timezone.utc)
    moon_phase = get_moon_phase(now_utc)
    moon_illumination = get_moon_illumination(now_utc)

    weather_data = {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "description": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "icon": get_weather_icon(weather_id, icon_code),
        "condition": get_condition_class(weather_id),
        "is_night": is_night,
        "moon_phase": moon_phase,
        "moon_illumination": moon_illumination,
        "is_cloudy": 801 <= weather_id <= 804 or weather_id == 741
    }

    return render_template("index.html", weather=weather_data)

def get_weather_icon(weather_id, icon_code):
    is_night = icon_code.endswith("n")
    
    if weather_id == 800:
        return "clear-night.svg" if is_night else "clear-day.svg"
    elif weather_id == 801:
        return "cloudy-1-day.svg"
    elif weather_id == 802:
        return "cloudy-2-day.svg"
    elif weather_id in (803, 804):
        return "cloudy-3-day.svg"
    elif 200 <= weather_id <= 232:
        return "thunderstorms.svg"
    elif 300 <= weather_id <= 321:
        return "rainy-1.svg"
    elif 500 <= weather_id <= 501:
        return "rainy-2.svg"
    elif 502 <= weather_id <= 531:
        return "rainy-3.svg"
    elif 600 <= weather_id <= 601:
        return "snowy-1.svg"
    elif 602 <= weather_id <= 622:
        return "snowy-3.svg"
    elif 700 <= weather_id <= 741:
        return "fog.svg"
    elif weather_id == 751 or weather_id == 761:
        return "haze.svg"
    elif weather_id == 771 or weather_id == 781:
        return "wind.svg"
    else:
        return "cloudy.svg"

def get_condition_class(weather_id):
    if weather_id == 800:
        return "clear"
    elif 801 <= weather_id <= 804:
        return "clouds"
    elif 200 <= weather_id <= 232:
        return "thunder"
    elif 300 <= weather_id <= 531:
        return "rain"
    elif 600 <= weather_id <= 622:
        return "snow"
    else:
        return "clear"

def get_moon_phase(date):
    # Known new moon reference date
    known_new_moon = datetime(2000, 1, 6, tzinfo=timezone.utc)
    lunar_cycle = 29.53058867
    days_since = (date - known_new_moon).total_seconds() / 86400
    phase_position = (days_since % lunar_cycle) / lunar_cycle

    if phase_position < 0.0625:
        return "new"
    elif phase_position < 0.1875:
        return "waxing-crescent"
    elif phase_position < 0.3125:
        return "first-quarter"
    elif phase_position < 0.4375:
        return "waxing-gibbous"
    elif phase_position < 0.5625:
        return "full"
    elif phase_position < 0.6875:
        return "waning-gibbous"
    elif phase_position < 0.8125:
        return "last-quarter"
    elif phase_position < 0.9375:
        return "waning-crescent"
    else:
        return "new"

def get_moon_illumination(date):
    known_new_moon = datetime(2000, 1, 6, tzinfo=timezone.utc)
    lunar_cycle = 29.53058867
    days_since = (date - known_new_moon).total_seconds() / 86400
    phase_position = (days_since % lunar_cycle) / lunar_cycle
    # Illumination follows a sine curve peaking at full moon
    return round(abs(math.sin(phase_position * math.pi)) * 100)