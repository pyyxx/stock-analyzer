import yfinance as yf
import sys
import argparse
import matplotlib.pyplot as plt
from pathlib import Path



CHART_DIR = Path("charts")
TRADING_DAYS = 252
RISK_FREE_RATE = 0.0
TRADE_COST = 0.001

def compute_metrics(data):
    """Return a copy of the data with daily returns and moving averages added."""
    data = data.copy()
    data["Daily Return"] = data["Close"].pct_change()
    data["MA20"] = data["Close"].rolling(20).mean()
    data["MA50"] = data["Close"].rolling(50).mean()
    return data

def sharpe_ratio(returns):
    excess_returns = returns - RISK_FREE_RATE / TRADING_DAYS
    return excess_returns.mean() / returns.std() * TRADING_DAYS ** 0.5


def max_drawdown(returns):
    growth = (1 + returns.fillna(0)).cumprod()
    return (growth / growth.cummax() - 1).min()


def summarize(data):
    """Compute summary statistics and return them as a dictionary."""
    returns = data["Daily Return"]

    sharpe = sharpe_ratio(returns)

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

def backtest(data, cost=TRADE_COST):
    df = data.copy()

    # 1. Signal: 1 when the short average is above the long one
    signal = (df["MA20"] > df["MA50"]).astype(int)

    # 2. Position: trade on YESTERDAY's signal (avoids look-ahead bias)
    df["Position"] = signal.shift(1).fillna(0)

    # Start both strategies on the first day the 50-day MA exists
    df = df[df["MA50"].notna()].copy()

    # 3. Strategy return = position x market return, minus trading costs
    trades = df["Position"].diff().abs().fillna(0)
    df["Strategy Return"] = df["Position"] * df["Daily Return"] - trades * cost

    # 4. Growth of $1 for each approach
    df["Strategy Growth"] = (1 + df["Strategy Return"]).cumprod()
    df["Buy & Hold Growth"] = (1 + df["Daily Return"]).cumprod()

    return df, int(trades.sum())


def print_backtest(df, trades):
    print("\n--- Backtest: 20/50-day MA crossover ---")
    print(f"{'':<12}{'Return':>10}{'Sharpe':>10}{'Max DD':>10}")
    for name, returns in [
        ("Strategy", df["Strategy Return"]),
        ("Buy & hold", df["Daily Return"]),
    ]:
        total = (1 + returns).prod() - 1
        print(f"{name:<12}{total:>10.2%}{sharpe_ratio(returns):>10.2f}"
              f"{max_drawdown(returns):>10.2%}")
    print(f"Trades: {trades} (cost per trade: {TRADE_COST:.2%})")


def plot_backtest(df, ticker):
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df["Strategy Growth"], label="MA crossover strategy")
    plt.plot(df.index, df["Buy & Hold Growth"], label="Buy & hold")
    plt.title(f"{ticker}: Strategy vs Buy & Hold")
    plt.xlabel("Date")
    plt.ylabel("Growth of $1")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.savefig(CHART_DIR / f"{ticker}_backtest.png", dpi=150, bbox_inches="tight")

def get_data(ticker, period="1y"):
    """Download daily price data. Returns None if the download fails or is empty."""
    try:
        data = yf.download(ticker, period=period, progress=False)
    except Exception as error:
        print(f"Download failed: {error}")
        return None

    if data.empty:
        return None

    data.columns = data.columns.get_level_values(0)
    return data

def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyze a stock's price history, returns, and risk."
    )
    parser.add_argument("ticker", help="ticker symbol, e.g. AAPL")
    parser.add_argument(
        "--period",
        default="1y",
        choices=["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"],
        help="how far back to look (default: 1y)",
    )
    parser.add_argument(
        "--backtest",
        action="store_true",
        help="compare a 20/50-day MA crossover strategy with buy & hold",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="save charts without opening windows",
    )
    return parser.parse_args()

def main():
    args = parse_args()
    ticker = args.ticker.upper().strip()

    data = get_data(ticker, args.period)
    if data is None:
        print(f"No data found for {ticker} (period: {args.period}). "
              "Check the ticker and your connection.")
        sys.exit(1)

    data = compute_metrics(data)
    stats = summarize(data)
    print_summary(ticker, stats)

    CHART_DIR.mkdir(exist_ok=True)
    plot_price(data, ticker)
    plot_returns(data, ticker)
    if args.backtest:
        bt, trades = backtest(data)
        if bt.empty:
            print("Not enough data to backtest. Try a longer --period.")
        else:
            print_backtest(bt, trades)
            plot_backtest(bt, ticker)
    if not args.no_show:
        plt.show()


if __name__ == "__main__":
    main()