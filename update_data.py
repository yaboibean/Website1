import requests
import json
from datetime import datetime, timedelta
import os

API_KEY = os.getenv("POLYGON_API_KEY", "0eRSRdku5AEEVsmIURHBd_32ztFEfsjZ")  # use env var if available

def fetch_market_data():
    date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    url = f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{date}?adjusted=true&include_otc=true&apiKey={API_KEY}"

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching market data: {response.status_code}")
        return []

    data = response.json().get("results", [])
    return sorted(data, key=lambda x: x.get("changePercent", 0), reverse=True)

def create_entry(stock, recommendation):
    percent = stock.get("changePercent", 0)
    return {
        "symbol": stock["T"],
        "price": f"${stock['c']} ({percent:+.2f}%)",
        "reason": "Based on overnight/pre-market activity.",
        "recommendation": recommendation
    }

def get_sample_data():
    return [
        {
            "symbol": "TEST",
            "price": "$10.00 (+5.00%)",
            "reason": "Sample pre-market data.",
            "recommendation": "Hold"
        }
    ]

def main():
    try:
        stocks = fetch_market_data()

        if not stocks:
            gainers = get_sample_data()
            losers = get_sample_data()
            tech = get_sample_data()
        else:
            gainers = [create_entry(s, "Buy") for s in stocks[:5]]
            losers = [create_entry(s, "Sell") for s in stocks[-5:]]
            tech = [create_entry(s, "Hold") for s in stocks[5:10]]

        output = {
            "gainers": gainers,
            "losers": losers,
            "tech": tech,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open("data.json", "w") as f:
            json.dump(output, f, indent=2)

        print("✅ data.json updated successfully.")

    except Exception as e:
        print("🚨 Error:", str(e))

if __name__ == "__main__":
    main()
