import yfinance as yf
import sys
import matplotlib.pyplot as plt
from pathlib import Path


CHART_DIR = Path("charts")
TRADING_DAYS = 252
RISK_FREE_RATE = 0.0


def get_data(ticker, period="1y"):
    """Download daily price data. Returns None if the ticker has no data."""
    data = yf.download(ticker, period=period, progress=False)
    if data.empty:
        return None
    data.columns = data.columns.get_level_values(0)
    return data


def compute_metrics(data):
    """Return a copy of the data with daily returns and moving averages added."""
    data = data.copy()
    data["Daily Return"] = data["Close"].pct_change()
    data["MA20"] = data["Close"].rolling(20).mean()
    data["MA50"] = data["Close"].rolling(50).mean()
    return data


def summarize(data):
    """Compute summary statistics and return them as a dictionary."""
    returns = data["Daily Return"]

    excess_returns = returns - RISK_FREE_RATE / TRADING_DAYS
    sharpe = excess_returns.mean() / returns.std() * TRADING_DAYS ** .5

    running_peak = data["Close"].cummax()
    drawdown = data["Close"] / running_peak - 1
    return {
        "cumulative_return": data["Close"].iloc[-1] / data["Close"].iloc[0] - 1,
        "avg_daily_return": returns.mean(),
        "volatility": returns.std() * TRADING_DAYS ** 0.5,
        "sharpe": sharpe,
        "max_drawdown": drawdown.min(),
        "max_drawdown_date": drawdown.idxmin(),
        "best_day": returns.idxmax(),
        "best_return": returns.max(),
        "worst_day": returns.idxmin(),
        "worst_return": returns.min(),
    }


def print_summary(ticker, stats):
    print(f"\n--- {ticker} Summary ---")
    print(f"Cumulative return:     {stats['cumulative_return']:.2%}")
    print(f"Average daily return:  {stats['avg_daily_return']:.3%}")
    print(f"Annualized volatility: {stats['volatility']:.2%}")
    print(f"Sharpe ratio:          {stats['sharpe']:.2f}")
    print(f"Max drawdown:          {stats['max_drawdown']:.2%} "
          f"(on {stats['max_drawdown_date'].date()})")
    print(f"Best day:  {stats['best_day'].date()} ({stats['best_return']:.2%})")
    print(f"Worst day: {stats['worst_day'].date()} ({stats['worst_return']:.2%})")


def plot_price(data, ticker):
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data["Close"], label="Close")
    plt.plot(data.index, data["MA20"], label="20-day MA")
    plt.plot(data.index, data["MA50"], label="50-day MA")
    plt.title(f"{ticker} Price and Moving Averages")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.savefig(CHART_DIR / f"{ticker}_price.png", dpi=150, bbox_inches="tight")


def plot_returns(data, ticker):
    plt.figure(figsize=(10, 5))
    plt.hist(data["Daily Return"].dropna(), bins=40)
    plt.title(f"{ticker} Distribution of Daily Returns")
    plt.xlabel("Daily return")
    plt.ylabel("Number of days")
    plt.savefig(CHART_DIR / f"{ticker}_returns_hist.png", dpi=150, bbox_inches="tight")


def main():
    ticker = input("Enter a ticker: ").upper().strip()

    data = get_data(ticker)
    if data is None:
        print(f"No data found for {ticker}")
        sys.exit(1)

    data = compute_metrics(data)
    stats = summarize(data)
    print_summary(ticker, stats)

    CHART_DIR.mkdir(exist_ok=True)
    plot_price(data, ticker)
    plot_returns(data, ticker)
    plt.show()


if __name__ == "__main__":
    main()