import requests
import json
from datetime import datetime

API_KEY = "YOUR_POLYGON_API_KEY"  # ← Replace with your real key
BASE_URL = "https://api.polygon.io/v2/snapshot/locale/us/markets/stocks"

def fetch_movers(endpoint):
    url = f"{BASE_URL}/{endpoint}?apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching {endpoint}: {response.status_code}")
        return []
    
    tickers = response.json().get("tickers", [])[:5]
    movers = []
    for t in tickers:
        ticker = t["ticker"]
        price = t["lastTrade"]["p"]
        change = t["todaysChangePerc"]
        reason = t.get("day", {}).get("change", "N/A")
        recommendation = "Buy" if change > 0 else "Sell"
        movers.append({
            "symbol": ticker,
            "price": f"${price:.2f} ({change:+.2f}%)",
            "reason": f"Price movement of {change:+.2f}%",
            "recommendation": recommendation
        })
    return movers

data = {
    "gainers": fetch_movers("gainers"),
    "losers": fetch_movers("losers"),
    "tech": []  # Optional: add separate logic for tech if needed
}

# Write to data.json
with open("data.json", "w") as f:
    json.dump(data, f, indent=2)

print("Market data updated at", datetime.now())
