import os
import requests
from flask import Blueprint, render_template, request
from dotenv import load_dotenv

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

    print("Status code:", geo_response.status_code)
    print("Response:", geo_response.json())

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

    weather_data = {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "description": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"]
    }

    return render_template("index.html", weather=weather_data)