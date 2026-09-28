import argparse
import json
import re
import sys

from clients.http import ExternalServiceError, NotFoundError
from processing.service import build_city_summary


def currency_code(value):
    code = value.upper()
    if not re.fullmatch(r"[A-Z]{3}", code):
        raise argparse.ArgumentTypeError(
            "валюта должна быть трёхбуквенным ISO-кодом, например USD"
        )
    return code


def nonempty_city(value):
    city = value.strip()
    if not city:
        raise argparse.ArgumentTypeError("название города не может быть пустым")
    return city


def main(argv=None):
    parser = argparse.ArgumentParser(description="Сводка по городу")
    parser.add_argument("--city", required=True, type=nonempty_city)
    parser.add_argument("--currency", type=currency_code, default="USD")
    parser.add_argument("--json", action="store_true", help="вывести JSON")
    args = parser.parse_args(argv)

    try:
        summary = build_city_summary(args.city, args.currency)
    except NotFoundError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 3
    except ExternalServiceError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 4

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        weather = summary["weather"]
        rates = summary["rates"]
        print(f"Город: {summary['city']}")
        print(f"Погода: {weather['temp_c']:.1f}°C, {weather['description']}")
        print(f"Тёплая одежда: {'да' if weather['warm_clothes'] else 'нет'}")
        print(f"{rates['currency']}→RUB: {rates['rate_to_rub']:.2f}")
        print(f"Дорогой курс: {'да' if rates['expensive'] else 'нет'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
