import yfinance as yf
import pandas as pd

tickers = ["AAPL", "SPY", "^VIX"]
start_date = "2015-01-01"
end_date = "2024-12-31"

for ticker in tickers:
    df = yf.download(ticker, start=start_date, end=end_date, interval="1d")
    if not df.empty:
        clean_name = ticker.replace("^", "")  
        df.to_csv(f"data/{clean_name}.csv")
        print(f"{clean_name}.csv saved with {len(df)} rows.")
    else:
        print(f"{ticker} has no data.")
