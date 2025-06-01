import requests
import json
from datetime import datetime, timedelta
import os

API_KEY = os.getenv("POLYGON_API_KEY", "YOUR_API_KEY")  # Replace with your actual key

def get_last_market_date():
    date = datetime.now()
    while date.weekday() >= 5:  # Weekend
        date -= timedelta(days=1)
    return date.strftime("%Y-%m-%d")

def fetch_grouped_market_data(date):
    url = f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{date}?adjusted=true&include_otc=false&apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Error:", response.status_code)
        return []
    return response.json().get("results", [])

def fetch_specific_tickers_data(tickers, date):
    data = []
    for ticker in tickers:
        url = f"https://api.polygon.io/v1/open-close/{ticker}/{date}?adjusted=true&apiKey={API_KEY}"
        response = requests.get(url)
        if response.status_code != 200:
            continue
        result = response.json()
        if 'status' in result and result['status'] == 'NOT_FOUND':
            continue
        result['T'] = ticker
        data.append(result)
    return data

def assign_recommendation(change_percent):
    if change_percent >= 5:
        return "Strong Buy"
    elif change_percent >= 2:
        return "Buy"
    elif change_percent >= -2:
        return "Hold"
    elif change_percent >= -5:
        return "Sell"
    else:
        return "Put Option"

def assign_reason(ticker, change_percent):
    reasons = {
        "TSLA": "Tesla's EV outlook remains strong.",
        "GOOG": "Alphabet's AI lead continues.",
        "AAPL": "Apple's product cycle supports stock.",
        "MSFT": "Microsoft pushes deeper into AI.",
        "NVDA": "NVIDIA benefits from AI hardware boom."
    }
    return reasons.get(ticker, f"Stock moved {change_percent:+.2f}% on the most recent trading day.")

def create_entry(stock, recommendation, reason):
    percent = stock.get("changePercent", 0)
    price = stock.get("c") or stock.get("close", 0)
    return {
        "symbol": stock["T"],
        "price": f"${price:.2f} ({percent:+.2f}%)",
        "reason": reason,
        "recommendation": recommendation
    }

def main():
    try:
        date = get_last_market_date()
        grouped = fetch_grouped_market_data(date)
        tech_symbols = ["TSLA", "GOOG", "AAPL", "MSFT", "NVDA"]
        tech_data = fetch_specific_tickers_data(tech_symbols, date)

        # Save raw data for debugging
        with open("raw_polygon_data.json", "w") as f:
            json.dump(grouped, f, indent=2)
        with open("raw_tech_data.json", "w") as f:
            json.dump(tech_data, f, indent=2)

        stocks = []
        for stock in grouped:
            if stock.get("o") and stock.get("c") and stock["c"] > 0:
                cp = ((stock["c"] - stock["o"]) / stock["o"]) * 100
                stock["changePercent"] = cp
                stocks.append(stock)

        sorted_stocks = sorted(stocks, key=lambda x: x["changePercent"], reverse=True)
        gainers = sorted_stocks[:5]
        losers = sorted_stocks[-5:]

        clean_tech = []
        for s in tech_data:
            if s.get("open") and s.get("close"):
                cp = ((s["close"] - s["open"]) / s["open"]) * 100
                s["changePercent"] = cp
                s["c"] = s["close"]
                clean_tech.append(s)

        output = {
            "gainers": [create_entry(s, assign_recommendation(s["changePercent"]), assign_reason(s["T"], s["changePercent"])) for s in gainers],
            "losers": [create_entry(s, assign_recommendation(s["changePercent"]), assign_reason(s["T"], s["changePercent"])) for s in losers],
            "tech": [create_entry(s, assign_recommendation(s["changePercent"]), assign_reason(s["T"], s["changePercent"])) for s in clean_tech],
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open("data.json", "w") as f:
            json.dump(output, f, indent=2)

        print("✅ Script finished successfully.")

    except Exception as e:
        print("❌ Error:", str(e))

if __name__ == "__main__":
    main()
