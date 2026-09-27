import requests
import pandas as pd

BASE_URL = "https://api.mexc.com"


def get_symbols():
    url = f"{BASE_URL}/api/v3/exchangeInfo"
    data = requests.get(url).json()

    symbols = []

    for s in data["symbols"]:
        if (
            s["quoteAsset"] == "USDT"
            and s["status"] == "1"
            and s["isSpotTradingAllowed"]
        ):
            symbols.append(s["symbol"])

    return symbols


def get_klines(symbol):
    url = f"{BASE_URL}/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": "1W",
        "limit": 100
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return None

    return response.json()


def calculate_macd(klines):
    closes = [float(k[4]) for k in klines]

    df = pd.DataFrame({"close": closes})

    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()

    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()

    return macd, signal


def find_crosses():
    symbols = get_symbols()
    results = []

    for symbol in symbols:
        try:
            klines = get_klines(symbol)

            if not klines or len(klines) < 35:
                continue

            macd, signal = calculate_macd(klines)

            previous = macd.iloc[-2]
            current = macd.iloc[-1]

            if previous <= 0 and current > 0:
                price = float(klines[-1][4])

                results.append({
                    "symbol": symbol,
                    "macd": round(current, 8),
                    "price": price
                })

        except Exception:
            continue

    return results


import json

if __name__ == "__main__":
    crosses = find_crosses()

    with open("signals.json", "w") as f:
        json.dump(crosses, f, indent=2)

    print("\n=== WEEKLY MACD ZERO CROSS ===\n")

    for coin in crosses:
        print(
            f"{coin['symbol']}  "
            f"MACD: {coin['macd']}  "
            f"PRICE: {coin['price']}"
        )

    print(f"\nTotale segnali: {len(crosses)}")
