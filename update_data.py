import requests
import json
from datetime import datetime, timedelta
import os

# Load API key from environment or fallback to hardcoded key
API_KEY = os.getenv("POLYGON_API_KEY", "0eRSRdku5AEEVsmIURHBd_32ztFEfsjZ")  # Replace if needed

# Get the most recent weekday (Mon–Fri)
def get_last_market_date():
    date = datetime.now()
    while date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        date -= timedelta(days=1)
    return date.strftime("%Y-%m-%d")

# Fetch grouped market data from Polygon
def fetch_market_data():
    date = get_last_market_date()
    url = f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{date}?adjusted=true&include_otc=true&apiKey={API_KEY}"

    print(f"📅 Fetching market data for: {date}")

    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ Error fetching market data: {response.status_code}")
        return []

    data = response.json().get("results", [])
    return sorted(data, key=lambda x: x.get("changePercent", 0), reverse=True)

# Format each stock entry for display
def create_entry(stock, recommendation):
    percent = stock.get("changePercent", 0)
    return {
        "symbol": stock["T"],
        "price": f"${stock['c']} ({percent:+.2f}%)",
        "reason": "Based on most recent trading day.",
        "recommendation": recommendation
    }

# Main function to generate data.json
def main():
    try:
        stocks = fetch_market_data()

        if not stocks:
            print("⚠️ No stock data returned.")
            return

        gainers = [create_entry(s, "Buy") for s in stocks[:5]]
        losers = [create_entry(s, "Sell") for s in stocks[-5:]]
        tech = [create_entry(s, "Hold") for s in stocks[5:10]]

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        output = {
            "gainers": gainers,
            "losers": losers,
            "tech": tech,
            "last_updated": now_str
        }

        with open("data.json", "w") as f:
            json.dump(output, f, indent=2)

        print("✅ data.json updated successfully.")

    except Exception as e:
        print("🚨 Error:", str(e))

if __name__ == "__main__":
    main()
