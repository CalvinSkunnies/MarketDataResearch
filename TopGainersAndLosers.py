import requests
import pandas as pd
from datetime import datetime

# 1. Fetch market data
def fetch_market_data(vs_currency="usd", per_page=250, page=1):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": page,
        "sparkline": False,
        "price_change_percentage": "24h"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    time.sleep(1.25)  # Respect rate limit: max 1 request per 1.2s
    return response.json()

# 2. Get top gainers & losers
def get_gainers_losers(data, top_n=10):
    df = pd.DataFrame(data)
    df = df[["id", "symbol", "name", "current_price", "price_change_percentage_24h"]].dropna()

    gainers = df.sort_values(by="price_change_percentage_24h", ascending=False).head(top_n)
    losers = df.sort_values(by="price_change_percentage_24h", ascending=True).head(top_n)
    return gainers, losers

# 3. Save to CSV
def save_to_csv(gainers, losers, filename):
    with open(filename, "w", encoding="utf-8", newline="") as f:
        f.write("Top 10 Gainers (24h)\n")
        gainers.to_csv(f, index=False)
        f.write("\nTop 10 Losers (24h)\n")
        losers.to_csv(f, index=False)
    print(f"✅ Data saved to {filename}")

# --- Run the script ---
if __name__ == "__main__":
    try:
        market_data = fetch_market_data()
        gainers, losers = get_gainers_losers(market_data)
        save_to_csv(gainers, losers, f"TopGainersLosers.csv")
    except Exception as e:
        print("❌ Error:", e)
