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
def assign_reason(ticker, change_percent):
    reasons = {
        "TSLA": "Tesla's recent developments in the electric vehicle market.",
        "GOOG": "Alphabet's latest earnings report exceeded expectations.",
        "AAPL": "Apple's new product launch generated positive market response.",
        "MSFT": "Microsoft announced strategic partnerships in the AI sector.",
        "NVDA": "NVIDIA's advancements in GPU technology boosted investor confidence."
    }
    return reasons.get(ticker, f"Stock moved {change_percent:+.2f}% on the most recent trading day.")

# Format each stock entry for display
def create_entry(stock, recommendation, reason):
    percent = stock.get("changePercent", 0)
    return {
        "symbol": stock["T"],
        "price": f"${stock['c']:.2f} ({percent:+.2f}%)",
        "reason": reason,
        "recommendation": recommendation
    }

# ✅ Updated MAIN with logging and robust filtering
def main():
    try:
        date = get_last_market_date()
        print(f"📅 Using market date: {date}")
        
        grouped_data = fetch_grouped_market_data(date)
        print(f"📦 Total stocks retrieved: {len(grouped_data)}")

        filtered_stocks = []
        skipped_missing = 0
        skipped_low_price = 0

        for stock in grouped_data:
            open_price = stock.get("o")
            close_price = stock.get("c")
            if open_price is None or close_price is None:
                skipped_missing += 1
                continue
            if close_price < 2:
                skipped_low_price += 1
                continue
            change_percent = ((close_price - open_price) / open_price) * 100
            stock["changePercent"] = change_percent
            filtered_stocks.append(stock)

        print(f"➖ Skipped (missing o/c): {skipped_missing}")
        print(f"➖ Skipped (under $2): {skipped_low_price}")
        print(f"✅ Stocks after filter: {len(filtered_stocks)}")

        sorted_stocks = sorted(filtered_stocks, key=lambda x: x["changePercent"], reverse=True)
        gainers = sorted_stocks[:5]
        losers = sorted_stocks[-5:]

        print(f"📈 Top Gainers Count: {len(gainers)}")
        print(f"📉 Top Losers Count: {len(losers)}")

        tech_tickers = ["TSLA", "GOOG", "AAPL", "MSFT", "NVDA"]
        tech_data = fetch_specific_tickers_data(tech_tickers, date)

        clean_tech_data = []
        for stock in tech_data:
            open_price = stock.get("open")
            close_price = stock.get("close")
            if open_price is None or close_price is None:
                continue
            change_percent = ((close_price - open_price) / open_price) * 100
            stock["o"] = open_price
            stock["c"] = close_price
            stock["changePercent"] = change_percent
            clean_tech_data.append(stock)

        print(f"🧠 Tech stocks retrieved: {len(clean_tech_data)}")

        gainers_entries = [create_entry(s, assign_recommendation(s["changePercent"]), assign_reason(s["T"], s["changePercent"])) for s in gainers]
        losers_entries = [create_entry(s, assign_recommendation(s["changePercent"]), assign_reason(s["T"], s["changePercent"])) for s in losers]
        tech_entries = [create_entry(s, assign_recommendation(s["changePercent"]), assign_reason(s["T"], s["changePercent"])) for s in clean_tech_data]

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        output = {
            "gainers": gainers_entries,
            "losers": losers_entries,
            "tech": tech_entries,
            "last_updated": now_str
        }

        print(f"📦 Final output -> gainers: {len(gainers_entries)}, losers: {len(losers_entries)}, tech: {len(tech_entries)}")

        with open("data.json", "w") as f:
            json.dump(output, f, indent=2)

        print("✅ data.json updated successfully.")

    except Exception as e:
        print("🚨 Error:", str(e))

if __name__ == "__main__":
    main()
