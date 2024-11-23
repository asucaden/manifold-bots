from datetime import datetime

from tinydb import TinyDB

from db import upsert_objects
from fetch import paginated_and_filtered_fetch

if __name__ == "__main__":
    print("\n\nRunning script at: ")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    db = TinyDB("persistence/markets_db.json")
    markets = paginated_and_filtered_fetch()

    if markets:
        new_markets, updated_markets = upsert_objects(db, markets)

        print(f"Fetched a total of {len(markets)} markets.")
        print(f"Saved a total of {new_markets} new markets.")
        print(f"Updated a total of {updated_markets} existing markets.")
    else:
        print("Failed to fetch markets")
