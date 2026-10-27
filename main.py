import yfinance as yf
import sys
import matplotlib.pyplot as plt

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

cumulative_return = data["Close"].iloc[-1] / data["Close"].iloc[0] - 1
volatility = data["Daily Return"].std() * 252 ** 0.5
avg_daily_return = data["Daily Return"].mean()
best_day = data["Daily Return"].idxmax()
worst_day = data["Daily Return"].idxmin()

print(f"--- {ticker} Summary ---")
print(f"Cumulative return: {cumulative_return:.2%}")
print(f"Average daily return: {avg_daily_return:.3%}")
print(f"Annualized volatility: {volatility:.2%}")
print(f"Best day: {best_day.date()} ({data['Daily Return'].max():.2%})")
print(f"Worst day: {worst_day.date()} ({data['Daily Return'].min():.2%})")

plt.figure(figsize=(10, 5))
plt.plot(data.index, data["Close"], label="Close")
plt.plot(data.index, data["MA20"], label="20-day MA")
plt.plot(data.index, data["MA50"], label="50-day MA")
plt.title(f"{ticker} Price and Moving Averages")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.legend()
plt.grid(alpha=0.3)
plt.savefig(f"{ticker}_price.png", dpi=150, bbox_inches="tight")
plt.show()

plt.figure(figsize=(10, 5))
plt.hist(data["Daily Return"].dropna(), bins=40)
plt.title(f"{ticker} Distribution of Daily Returns")
plt.xlabel("Daily return")
plt.ylabel("Number of days")
plt.savefig(f"{ticker}_returns_hist.png", dpi=150, bbox_inches="tight")
plt.show()