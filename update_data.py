import requests
import json

API_KEY = idEz43jpOmCkSZ5eq5niptvxEHxPJi64  # Replace with your actual Polygon.io API key

def fetch_top_movers(direction):
    url = f'https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/{direction}?apiKey={API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        movers = []
        for item in data.get('tickers', [])[:5]:  # Get top 3 movers
            movers.append({
                'symbol': item['ticker'],
                'price': f"{item['lastTrade']['p']:.2f}",
                'change': f"{item['todaysChangePerc']:+.2f}%",
                'reason': 'Live data from Polygon.io',
                'recommendation': 'Hold'
            })
        return movers
    else:
        print(f"Error fetching {direction}: {response.status_code}")
        return []

def main():
    gainers = fetch_top_movers('gainers')
    losers = fetch_top_movers('losers')
    tech = []  # You can later fill this with hand-picked tickers or tech-based filters

    data = {
        'gainers': gainers,
        'losers': losers,
        'tech': tech
    }

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()
