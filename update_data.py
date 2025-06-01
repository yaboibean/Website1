import requests
import json
from datetime import datetime

API_KEY = "YOUR_POLYGON_API_KEY"
BASE_URL = "https://api.polygon.io/v2/snapshot/locale/us/markets/stocks"

def fetch_movers(endpoint):
    url = f"{BASE_URL}/{endpoint}?apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching {endpoint}: {response.status_code}")
        return []

    tickers = response.json().get("tickers", [])
    if not tickers:
        print(f"No data returned for {endpoint}, using fallback.")
        return [
            {
                "symbol": f"FAKE-{endpoint[:3].upper()}",
                "price": "$123.45 (+4.56%)",
                "reason": f"Example data for {endpoint}",
                "recommendation": "Hold"
            }
        ]
    
    movers = []
    for t in tickers[:5]:
        ticker = t["ticker"]
        price = t["lastTrade"]["p"]
        change = t["todaysChangePerc"]
        movers.append({
            "symbol": ticker,
            "price": f"${price:.2f} ({change:+.2f}%)",
            "reason": f"Price moved {change:+.2f}%",
            "recommendation": "Buy" if change > 0 else "Sell"
        })
    return movers

data = {
    "gainers": fetch_movers("gainers"),
    "losers": fetch_movers("losers"),
    "tech": []
}

# Save to file
with open("data.json", "w") as f:
    json.dump(data, f, indent=2)

print("Update complete at", datetime.now())
