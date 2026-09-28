import math

from clients.http import ExternalServiceError, get_json

RATE_URL = "https://api.frankfurter.dev/v2/rate"


def get_rate(currency):
    data = get_json(
        f"{RATE_URL}/{currency}/RUB",
        not_found_statuses=(404, 422),
    )

    rate = data.get("rate")
    if (
        not isinstance(rate, (int, float))
        or isinstance(rate, bool)
        or not math.isfinite(rate)
        or rate <= 0
        or data.get("base") != currency
        or data.get("quote") != "RUB"
    ):
        raise ExternalServiceError("Некорректные данные курса")

    return float(rate)
