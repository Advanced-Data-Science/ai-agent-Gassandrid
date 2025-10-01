import requests
import json
import logging
from datetime import datetime

# logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Make your first API call to get 5 random cat facts
def get_cat_facts(num_facts=5):
    url = "https://catfact.ninja/fact"
    facts = []
    logging.info(f"Starting to fetch {num_facts} cat facts")
    try:
        for i in range(num_facts):
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                fact = data.get("fact")
                if fact:
                    facts.append(fact)
                    logging.info(f"Successfully retrieved fact {i+1}")
                else:
                    logging.warning(f"No fact found in response for request {i+1}")
            else:
                logging.error(
                    f"API request {i+1} failed with status code: {response.status_code}"
                )

    except requests.exceptions.Timeout:
        logging.error("Request timed out")
    except requests.exceptions.ConnectionError:
        logging.error("Connection error occurred")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error occurred: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

    logging.info(
        f"Successfully retrieved {len(facts)} out of {num_facts} requested facts"
    )
    return facts


def save_facts_to_json(facts, filename="cat_facts.json"):
    try:
        data = {
            "facts": facts,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logging.info(f"Successfully saved {len(facts)} facts to {filename}")
        return True

    except Exception as e:
        logging.error(f"Failed to save facts to JSON file: {e}")
        return False


# Test your function
cat_facts = get_cat_facts()
for i, fact in enumerate(cat_facts, 1):
    print(f"Cat fact {i}: {fact}")

# Save facts to JSON file
if cat_facts:
    save_facts_to_json(cat_facts)
