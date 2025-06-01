import requests
import json
from datetime import datetime, timedelta
import os

API_KEY = os.getenv("POLYGON_API_KEY", "YOUR_API_KEY")  # Replace with your actual API key

# Get the most recent weekday (Mon–Fri)
def get_last_market_date():
    date = datetime.now()
    while date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        date -= timedelta(days=1)
    return date.strftime("%Y-%m-%d")

# Fetch grouped market data from Polygon
def fetch_grouped_market_data(date):
    url = f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{date}?adjusted=true&include_otc=false&apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching market data: {response.status_code}")
        return []
    data = response.json().get("results", [])
    return data

# Fetch data for specific tickers
def fetch_specific_tickers_data(tickers, date):
    data = []
    for ticker in tickers:
        url = f"https://api.polygon.io/v1/open-close/{ticker}/{date}?adjusted=true&apiKey={API_KEY}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching data for {ticker}: {response.status_code}")
            continue
        result = response.json()
        if 'status' in result and result['status'] == 'NOT_FOUND':
            print(f"No data found for {ticker} on {date}")
            continue
        result['T'] = ticker  # Add ticker symbol to the result
        data.append(result)
    return data

# Assign recommendation based on percentage change
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

# Assign reason based on ticker
def assign_reason(ticker):
    reasons = {
        "TSLA": "Recent developments in electric vehicle market.",
        "GOOG": "Alphabet's latest earnings report exceeded expectations.",
        "AAPL": "Apple's new product launch generated positive market response.",
        "MSFT": "Microsoft announced strategic partnerships in AI sector.",
        "NVDA": "NVIDIA's advancements in GPU technology boosted investor confidence."
    }
    return reasons.get(ticker, "Significant price movement observed.")

# Format each stock entry for display
def create_entry(stock, recommendation, reason):
    percent = stock.get("changePercent", 0)
    return {
        "symbol": stock["T"],
        "price": f"${stock['c']:.2f} ({percent:+.2f}%)",
        "reason": reason,
        "recommendation": recommendation
    }

def main():
    try:
        date = get_last_market_date()
        grouped_data = fetch_grouped_market_data(date)

        # Calculate changePercent for each stock
        for stock in grouped_data:
            open_price = stock.get("o", 0)
            close_price = stock.get("c", 0)
            if open_price > 0:
                change_percent = ((close_price - open_price) / open_price) * 100
            else:
                change_percent = 0
            stock["changePercent"] = change_percent

        # Sort stocks by changePercent
        sorted_stocks = sorted(grouped_data, key=lambda x: x["changePercent"], reverse=True)

        # Get top 5 gainers and losers
        gainers = sorted_stocks[:5]
        losers = sorted_stocks[-5:]

        # Fetch data for major tech stocks
        tech_tickers = ["TSLA", "GOOG", "AAPL", "MSFT", "NVDA"]
        tech_data = fetch_specific_tickers_data(tech_tickers, date)

        # Calculate changePercent for tech stocks
        for stock in tech_data:
            open_price = stock.get("open", 0)
            close_price = stock.get("close", 0)
            if open_price > 0:
                change_percent = ((close_price - open_price) / open_price) * 100
            else:
                change_percent = 0
            stock["o"] = open_price
            stock["c"] = close_price
            stock["changePercent"] = change_percent

        # Create entries
        gainers_entries = [create_entry(s, assign_recommendation(s["changePercent"]), assign_reason(s["T"])) for s in gainers]
        losers_entries = [create_entry(s, assign_recommendation(s["changePercent"]), assign_reason(s["T"])) for s in losers]
        tech_entries = [create_entry(s, assign_recommendation(s["changePercent"]), assign_reason(s["T"])) for s in tech_data]

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        output = {
            "gainers": gainers_entries,
            "losers": losers_entries,
            "tech": tech_entries,
            "last_updated": now_str
        }

        with open("data.json", "w") as f:
            json.dump(output, f, indent=2)

        print("✅ data.json updated successfully.")

    except Exception as e:
        print("🚨 Error:", str(e))

if __name__ == "__main__":
    main()
