from flask import Blueprint, render_template, request
from app.weather import fetch_weather, fetch_suggestions, fetch_weather_by_coords

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/weather", methods=["POST"])
def weather():
    city = request.form.get("city")
    weather_data, error = fetch_weather(city)

    if error:
        return render_template("index.html", error=error)

    return render_template("index.html", weather=weather_data)

@main.route("/suggest")
def suggest():
    query = request.args.get("q", "")
    if len(query) < 3:
        return {"suggestions": []}
    
    results = fetch_suggestions(query)
    return {"suggestions": results}

@main.route("/weather-by-coords", methods=["POST"])
def weather_by_coords():
    lat = request.form.get("lat")
    lon = request.form.get("lon")
    state = request.form.get("state", "")
    weather_data, error = fetch_weather_by_coords(lat, lon, state=state)

    if error:
        return render_template("index.html", error=error)

    return render_template("index.html", weather=weather_data)