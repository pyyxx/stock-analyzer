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