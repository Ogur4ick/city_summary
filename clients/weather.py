import math

from clients.http import ExternalServiceError, NotFoundError, get_json

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_DESCRIPTIONS = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    56: "light freezing drizzle",
    57: "dense freezing drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    66: "light freezing rain",
    67: "heavy freezing rain",
    71: "slight snowfall",
    73: "moderate snowfall",
    75: "heavy snowfall",
    77: "snow grains",
    80: "slight rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    85: "slight snow showers",
    86: "heavy snow showers",
    95: "thunderstorm",
    96: "thunderstorm with slight hail",
    97: "heavy thunderstorm",
    99: "thunderstorm with heavy hail",
}


def _valid_number(value, minimum, maximum):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and minimum <= value <= maximum
    )


def get_weather(city):
    locations = get_json(
        GEOCODING_URL,
        params={"name": city, "count": 1},
    )

    results = locations.get("results")
    if results is None:
        raise NotFoundError(f"Город не найден: {city}")
    if not isinstance(results, list):
        raise ExternalServiceError("Некорректный список городов")
    if not results:
        raise NotFoundError(f"Город не найден: {city}")

    location = results[0]
    if not isinstance(location, dict):
        raise ExternalServiceError("Некорректные данные города")

    latitude = location.get("latitude")
    longitude = location.get("longitude")
    if not _valid_number(latitude, -90, 90) or not _valid_number(longitude, -180, 180):
        raise ExternalServiceError("Некорректные координаты города")

    forecast = get_json(
        FORECAST_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,weather_code",
            "temperature_unit": "celsius",
        },
    )

    current = forecast.get("current")
    if not isinstance(current, dict):
        raise ExternalServiceError("В ответе погоды отсутствует current")

    temperature = current.get("temperature_2m")
    code = current.get("weather_code")
    if not _valid_number(temperature, -100, 70):
        raise ExternalServiceError("Некорректная температура")
    if type(code) is not int or code not in WEATHER_DESCRIPTIONS:
        raise ExternalServiceError("Некорректный код погоды")

    return {
        "temp_c": float(temperature),
        "description": WEATHER_DESCRIPTIONS[code],
    }
