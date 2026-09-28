import math
import time

import requests


class NotFoundError(Exception):
    """Город или валюта не найдены."""


class ExternalServiceError(Exception):
    """Внешний сервис недоступен или вернул неожиданный ответ."""


RETRY_STATUSES = {500, 502, 503, 504}
ATTEMPTS = 3  # Первая попытка + два повтора
TIMEOUT_SECONDS = 5  # На каждый отдельный запрос


def get_json(url, *, params=None, not_found_statuses=()):
    """Выполнить GET и вернуть JSON-объект (словарь)."""
    for attempt in range(ATTEMPTS):
        try:
            response = requests.get(
                url,
                params=params,
                timeout=TIMEOUT_SECONDS,
            )
        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        ) as exc:
            if attempt == ATTEMPTS - 1:
                raise ExternalServiceError(
                    f"Сервис недоступен после {ATTEMPTS} попыток"
                ) from exc
            time.sleep(0.5 * (2**attempt))
            continue
        except requests.exceptions.RequestException as exc:
            raise ExternalServiceError("Не удалось выполнить HTTP-запрос") from exc

        status = response.status_code

        if status in not_found_statuses:
            raise NotFoundError(f"Ресурс не найден: HTTP {status}")

        if status in RETRY_STATUSES or status == 429:
            if attempt == ATTEMPTS - 1:
                raise ExternalServiceError(
                    f"Сервис недоступен после {ATTEMPTS} попыток: HTTP {status}"
                )

            delay = 0.5 * (2**attempt)
            if status == 429:
                raw = response.headers.get("Retry-After", "")
                try:
                    value = float(raw)
                    if math.isfinite(value) and value >= 0:
                        delay = value
                except (TypeError, ValueError):
                    pass

            time.sleep(delay)
            continue

        if not 200 <= status < 300:
            raise ExternalServiceError(f"Внешний сервис вернул HTTP {status}")

        try:
            data = response.json()
        except (ValueError, requests.exceptions.RequestException) as exc:
            raise ExternalServiceError("Внешний сервис вернул невалидный JSON") from exc

        if not isinstance(data, dict):
            raise ExternalServiceError("Ожидался JSON-объект")
        return data

    raise ExternalServiceError("Не удалось получить ответ")
