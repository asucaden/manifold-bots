import os

import requests
from dotenv import load_dotenv

# Load environment variables (e.g., API Key)
load_dotenv()
API_KEY = os.getenv("MANIFOLD_API_KEY")  # Set your API key here if not using .env
BASE_URL = "https://api.manifold.markets/v0"


def filter_fields(data, fields_to_keep):
    """
    Filters the given data to include only specific fields.

    Args:
        data (list[dict]): The response object.
        fields_to_keep (list): List of keys to keep in each object.

    Returns:
        list[dict]: Filtered list of dictionaries.
    """
    return [{key: item[key] for key in fields_to_keep if key in item} for item in data]


def search_markets(
    term="",
    sort="score",
    filter_param="open",  # 'filter' is a keyword
    contract_type="BINARY",
    limit=100,
    offset=0,
):
    """
    Gets a filtered list of potential markets from the Manifold Markets API.

    Returns:
        list: A list of markets or None if the request fails.
    """

    url = f"{BASE_URL}/search-markets"
    params = {
        "term": term,
        "sort": sort,
        "filter": filter_param,
        "contractType": contract_type,
        "limit": limit,
        "offset": offset,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
        markets_response = response.json()  # Parse JSON response into Python objects
        return markets_response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def paginated_and_filtered_fetch(num_markets_to_fetch=30_000, page_size=1000):
    page_size = min(page_size, num_markets_to_fetch)
    fetched_markets = []

    for i in range(num_markets_to_fetch // page_size):
        print(f"Getting markets {i * page_size} thru {i * page_size + page_size - 1}")
        markets = search_markets(limit=page_size, offset=i * page_size)

        fields_to_keep = [
            "id",
            "createdTime",
            "closeTime",
            "question",
            "probability",
            "totalLiquidity",
            "outcomeType",
            "isResolved",
            "resolution",
            "resolutionTime",
            "token",
        ]
        markets = filter_fields(markets, fields_to_keep)

        if markets:
            markets = [
                market
                for market in markets
                if market.get("totalLiquidity", 0) > 600
                and not market.get("isResolved", True)
                and market.get("token", "neither") == "MANA"
            ]
            fetched_markets.extend(markets)

    return fetched_markets


def place_bet(contract_id, outcome, amount=1):
    """
    Places a bet on a specified market using the Manifold Markets API.

    Args:
        contract_id (str): The unique ID of the market to bet on.
        outcome (str): The outcome to bet on (e.g., "YES" or "NO").
        amount (float): The amount of money to bet.

    Returns:
        dict: API response as a dictionary, or None if the request fails.
    """

    if not API_KEY:
        raise ValueError("API Key is missing. Set it in your environment variables.")

    # API endpoint and headers
    url = f"{BASE_URL}/bet"
    headers = {"Authorization": f"Key {API_KEY}"}

    # Payload for the API request
    payload = {"contractId": contract_id, "outcome": outcome, "amount": amount}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors (4xx, 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to place bet: {e}")
        return None
