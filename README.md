# Stock Analyzer

A command-line tool that downloads daily price data for any stock, reports
return and risk statistics, and backtests a moving-average crossover
strategy against buy-and-hold.

## Features
- Downloads price history with yfinance
- Daily returns, 20/50-day moving averages, cumulative return
- Annualized volatility, Sharpe ratio, maximum drawdown
- Best and worst trading days
- Optional backtest of a 20/50-day MA crossover strategy
  (0.1% cost per trade, signals lagged one day to avoid look-ahead bias)
- Saves charts as PNGs

## Setup
```bash
git clone https://github.com/pyyxx/stock-analyzer.git
cd stock-analyzer
python3 -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage
```bash
python3 main.py AAPL
python3 main.py MSFT --period 5y
python3 main.py SPY --period 5y --backtest
python3 main.py TSLA --period 6mo --no-show
```
Run `python3 main.py --help` for all options.

## What I learned
This was my first time using pandas and different libraries in general.
It was a very interesting and challenging process to go through everything
but I learned a lot. Hopefully this is the first of many projects.

## Limitations
- Single asset per run, over one time period
- No comparisons availible
- Past performance does not predict future results