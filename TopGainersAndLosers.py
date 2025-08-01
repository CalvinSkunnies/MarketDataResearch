import requests
import pandas as pd
import time
from datetime import datetime

# 1. Fetch market data (with rate-limit retry)
def fetch_market_data(vs_currency="usd", per_page=250, page=1, retries=3):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": page,
        "sparkline": False,
        "price_change_percentage": "24h"
    }

    headers = {
        "Accept": "application/json",
        "User-Agent": "TopMoversBot/1.0"
    }

    for attempt in range(retries):
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            time.sleep(1.25)  # respect rate limit
            return response.json()

        elif response.status_code == 429:
            wait_time = 10 * (attempt + 1)
            print(f"⚠️ Rate limited (429). Retrying in {wait_time}s...")
            time.sleep(wait_time)

        else:
            print(f"❌ Request failed with {response.status_code}: {response.text}")
            break

    raise Exception("❌ Failed after retries due to rate limiting.")

# 2. Process and label gainers & losers
def get_combined_movers(data, top_n=10):
    df = pd.DataFrame(data)
    df = df[["id", "symbol", "name", "current_price", "price_change_percentage_24h"]].dropna()

    gainers = df.sort_values(by="price_change_percentage_24h", ascending=False).head(top_n)
    gainers["type"] = "gainer"

    losers = df.sort_values(by="price_change_percentage_24h", ascending=True).head(top_n)
    losers["type"] = "loser"

    combined = pd.concat([gainers, losers], ignore_index=True)
    return combined

# 3. Save to CSV
def save_to_csv(df, filename):
    df.to_csv(filename, index=False)
    print(f"✅ Combined movers saved to {filename}")

# 4. Main execution
if __name__ == "__main__":
    try:
        print("📡 Fetching CoinGecko market data...")
        data = fetch_market_data()

        movers = get_combined_movers(data)
        
        filename = f"TopGainersAndLosers.csv"

        save_to_csv(movers, filename)

    except Exception as e:
        print(f"❌ Error: {e}")
