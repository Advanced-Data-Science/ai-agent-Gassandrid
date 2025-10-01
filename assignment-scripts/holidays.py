import requests
import json
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_public_holidays(country_code="US", year=2024):
    url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}"
    logging.info(f"Fetching holidays for {country_code} in {year}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        holidays = response.json()
        logging.info(
            f"Successfully retrieved {len(holidays)} holidays for {country_code}"
        )
        return holidays

    except requests.exceptions.Timeout:
        logging.error(f"Request timeout for {country_code}")
        return None
    except requests.exceptions.ConnectionError:
        logging.error(f"Connection error for {country_code}")
        return None
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error for {country_code}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed for {country_code}: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error for {country_code}: {e}")
        return None


def print_holiday_details(holidays, country_code):
    if not holidays:
        logging.warning(f"No holidays to display for {country_code}")
        return

    print(f"\n - Holidays for {country_code} -")
    for holiday in holidays:
        name = holiday.get("name", "Unknown")
        date = holiday.get("date", "Unknown")
        print(f"{date}: {name}")


def create_holiday_summary(countries_data):
    summary = {"countries": countries_data, "statistics": {}}

    if countries_data:
        max_country = max(countries_data, key=countries_data.get)
        min_country = min(countries_data, key=countries_data.get)

        summary["statistics"] = {
            "most_holidays": {
                "country": max_country,
                "count": countries_data[max_country],
            },
            "least_holidays": {
                "country": min_country,
                "count": countries_data[min_country],
            },
        }

    print(json.dumps(summary, indent=2))

    # save to holidays_summary.json
    try:
        data = {
            "holiday_summary": summary,
        }

        with open("holidays_summary.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logging.info(f"Successfully saved holiday summary to holidays_summary.json")
        return True

    except Exception as e:
        logging.error(f"Failed to save holiday summary to JSON file: {e}")
        return False


# Test with 3 different countries
countries = ["US", "CA", "GB"]
countries_summary = {}

for country in countries:
    holidays = get_public_holidays(country)
    if holidays:
        countries_summary[country] = len(holidays)
        print_holiday_details(holidays, country)
    else:
        countries_summary[country] = 0
        print(f"Failed to get holidays for {country}")

create_holiday_summary(countries_summary)
