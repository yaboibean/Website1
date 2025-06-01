import yfinance as yf
import json

popular_tickers = ["MSFT", "AAPL", "NVDA", "GOOG", "AMZN"]

def get_info(symbol):
    t = yf.Ticker(symbol)
    hist = t.history(period="2d")
    try:
        price = round(hist["Close"].iloc[-1], 2)
        previous = round(hist["Close"].iloc[-2], 2)
        change = price - previous
        change_pct = f"{(change / previous) * 100:+.2f}%"
        return {
            "symbol": symbol,
            "price": str(price),
            "change": change_pct,
            "reason": "Live data from Yahoo Finance",
            "recommendation": "Hold"
        }
    except:
        return None

data = {
    "gainers": [
        {
            "symbol": "BMGL",
            "price": "6.08",
            "change": "+444.62%",
            "reason": "Cancer drug breakthrough drew investor interest.",
            "recommendation": "Put Option — likely overinflated."
        }
    ],
    "losers": [
        {
            "symbol": "MDCX",
            "price": "2.55",
            "change": "-29.85%",
            "reason": "Regulatory delay for key drug.",
            "recommendation": "Sell — facing headwinds."
        }
    ],
    "tech": list(filter(None, map(get_info, popular_tickers)))
}

with open("data.json", "w") as f:
    json.dump(data, f, indent=2)
