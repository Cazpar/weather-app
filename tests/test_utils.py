import math
from datetime import datetime, timedelta, timezone

from app.utils import (
    get_weather_icon,
    get_condition_class,
    get_moon_phase,
    get_moon_illumination,
)


def test_get_weather_icon_clear_day_and_night():
    assert get_weather_icon(800, "01d") == "clear-day.svg"
    assert get_weather_icon(800, "01n") == "clear-night.svg"


def test_get_weather_icon_cloud_ranges_and_fallback():
    # Specific cloud codes
    assert get_weather_icon(801, "02d") == "cloudy-1-day.svg"
    assert get_weather_icon(802, "03d") == "cloudy-2-day.svg"
    assert get_weather_icon(803, "04d") == "cloudy-3-day.svg"

    # Fallback for unknown ids
    assert get_weather_icon(999, "01d") == "cloudy.svg"


def test_get_condition_class_basic_ranges():
    assert get_condition_class(800) == "clear"
    assert get_condition_class(801) == "clouds"
    assert get_condition_class(804) == "clouds"
    assert get_condition_class(201) == "thunder"
    assert get_condition_class(500) == "rain"
    assert get_condition_class(620) == "snow"


def test_get_moon_phase_known_new_moon():
    # This is the anchor date used in the implementation
    known_new_moon = datetime(2000, 1, 6, tzinfo=timezone.utc)
    assert get_moon_phase(known_new_moon) == "new"
    assert get_moon_illumination(known_new_moon) == 0


def test_get_moon_phase_full_moon_and_illumination_close_to_100():
    known_new_moon = datetime(2000, 1, 6, tzinfo=timezone.utc)
    half_cycle_days = 29.53058867 / 2
    approx_full_moon = known_new_moon + timedelta(days=half_cycle_days)

    phase = get_moon_phase(approx_full_moon)
    illumination = get_moon_illumination(approx_full_moon)

    assert phase == "full"
    # Allow a tiny tolerance in case of floating point rounding
    assert 99 <= illumination <= 100

