from flask import Blueprint, render_template, request
from app.weather import fetch_weather

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