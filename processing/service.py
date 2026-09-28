from clients.rates import get_rate
from clients.weather import get_weather
from processing.preprocessing import is_expensive, needs_warm_clothes


def build_city_summary(city, currency="USD"):
    weather = get_weather(city)
    rate = get_rate(currency)

    return {
        "city": city,
        "weather": {
            **weather,
            "warm_clothes": needs_warm_clothes(weather["temp_c"]),
        },
        "rates": {
            "currency": currency,
            "rate_to_rub": rate,
            "expensive": is_expensive(rate),
        },
    }
