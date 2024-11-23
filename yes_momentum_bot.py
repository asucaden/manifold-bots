import requests
from tinydb import Query, TinyDB

from fetch import paginated_and_filtered_fetch, place_bet

if __name__ == "__main__":
    yes_db = TinyDB("persistence/yes_momentum_bets_db.json")
    markets_db = TinyDB("persistence/markets_db.json")

    # Get all the markets from manifold
    markets = paginated_and_filtered_fetch()

    if markets:
        print("Length fetched, before filtering:", len(markets))

        # Filter markets to only be the ones i already have
        markets_from_markets_db = {
            market["id"]: market for market in markets_db.all() if "id" in market
        }
        markets = [
            market for market in markets if market["id"] in markets_from_markets_db
        ]
        print(
            "Length after filtering to only include markets already tracked in markets_db:",
            len(markets),
        )

        # filter markets that had previous odds under 94%
        markets = [
            market
            for market in markets
            if markets_from_markets_db[market["id"]]["probability"] < 0.94
        ]
        print(
            "Length after filtering to only include markets that market_db tracked at under 94%",
            len(markets),
        )

        # filter markets that have current odds between 94 and 97.5% chance
        markets = [
            market for market in markets if 0.94 < market.get("probability", 0) < 0.975
        ]
        print(
            "Length after filtering to only include markets with current probability between 94 and 97.5%:",
            len(markets),
        )

        # filter to markets i have not yet bet on
        market_ids_already_bet_on = {
            bet["contractId"]
            for bet in yes_db.all()
            if "contractId" in bet  # contractId is same as marketId
        }

        if market_ids_already_bet_on:
            markets = [
                market
                for market in markets
                if market["id"] not in market_ids_already_bet_on
            ]
        print(
            "Length after filtering to only include markets not bet on yet",
            len(markets),
        )

        # bet on these and persist the results
        bet_counter = 0
        for market in markets:
            if len(market_ids_already_bet_on) + bet_counter >= 200:
                break  # don't want to go overboard, for now!
            if market["id"]:
                bet = place_bet(market["id"], "YES", 5)
                if bet:
                    yes_db.insert(bet)
                    bet_counter += 1
                else:
                    print("Failed to place bet!")
        print(f"Placed {bet_counter} bets!")
