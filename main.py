import yfinance as yf
import sys

ticker = input("Enter a ticker: ").upper()
data = yf.download(ticker, period ="1y")
if data.empty:
    print(f"No data found for {ticker}")
    sys.exit()


data.columns = data.columns.get_level_values(0)

print(data.head())
print(data.tail())
print(data.shape)

print(data.columns)
print(data.dtypes)
print(data["Close"].head())

data["Daily Return"] = data["Close"].pct_change()
print(data[["Close", "Daily Return"]].head())

data["MA20"] = data["Close"].rolling(20).mean()
data["MA50"] = data["Close"].rolling(50).mean()
print(data[["Close", "MA20", "MA50"]].iloc[[0, 19, 20, 49, 50]])