import math
from datetime import datetime, timezone


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
    elif weather_id in (751, 761):
        return "haze.svg"
    elif weather_id in (771, 781):
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
    return round(abs(math.sin(phase_position * math.pi)) * 100)