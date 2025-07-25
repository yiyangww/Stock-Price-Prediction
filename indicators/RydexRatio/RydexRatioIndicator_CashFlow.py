"""
Get data from WRDS: Home>Get Data>ETF Global>Fund Flow
This program calculates a proxy for the leveraged Rydex bull-bear asset ratio using the formula: 
(Bear Funds CCFL + Money Market CCFL) ÷ Bull Funds CCFL (CCFL = cumulative net cash flow, not market gains/losses).  
But we are multiplying Money Market by 0.
Uses a window of rolling_w days to accumulate the cash flows.
The csv file has the following column headers: 
as_of_date, composite_ticker, shares_outstanding,	nav,	fundflow.  as_of_date is the date, composite_ticker is the ETF ticker,	fundflow is the cash flow. 
The dates are daily in frequency.  The composite_ticker contains the following tickers: 
    
See LeveragedETFs.txt

Originally:
if "rydex_ratio" < 0  = extremely bullish
if "rydex_ratio" < 1 = bullish
if "rydex_ratio" ≈  1 = neutral
if "rydex_ratio" > 1 = bearish
if "rydex_ratio" >> 1  = extremely bearish

  
"""
import pandas as pd
import numpy as np


# Load the CSV file
df = pd.read_csv("Data.csv", parse_dates=["as_of_date"])

# Ensure correct sorting
df = df.sort_values(by=["composite_ticker", "as_of_date"])

# Define ticker categories

bull_funds = {"TQQQ", "UDOW", "UPRO", "UWM", "URTY","UCC", "UGE", "URE", "UPW", "UXI", "USD", "UCYB", "UCO", "UGL" ,"SOXL", "TECL", "MIDU", "SPX", "TNA","TSLR", "AMDL", "AMZZ","MSFL", "PTIR","TBF", "TBT", "TTT", "TBX", "TMV", "SJB"} 
bear_funds = {"SH", "SDS", "SPXU", "PSQ", "SQQQ", "SDOW", "TWM", "SRTY","SZK", "SCC", "BIS", "SSG", "SRS", "TECS", "SOXS", "FAZ","BITI"} 
money_market_funds = {"BIL", "SGOV", "SHV", "USFR"}


#Better results
bull_funds = {"TQQQ"} 
bear_funds = {"SQQQ"} 
money_market_funds = {"BIL"}



# Add a category column
def categorize(ticker):
    if ticker in bull_funds:
        return "bull"
    elif ticker in bear_funds:
        return "bear"
    elif ticker in money_market_funds:
        return "money"
    else:
        return "other"

df["category"] = df["composite_ticker"].apply(categorize)

# Pivot table to group cash flows by date and category
pivot = (
    df.pivot_table(index="as_of_date", columns="category", values="fundflow", aggfunc="sum")
    .fillna(0)
)

rolling_w = 252*2

# Compute rolling cumulative rolling_w-day cash flows
pivot["ccfl_bull"] = pivot["bull"].rolling(window=rolling_w, min_periods=1).sum()
pivot["ccfl_bear"] = pivot["bear"].rolling(window=rolling_w, min_periods=1).sum()
pivot["ccfl_money"] = pivot["money"].rolling(window=rolling_w, min_periods=1).sum()


numerator = pivot["ccfl_bear"] + 0*pivot["ccfl_money"]
denominator = pivot["ccfl_bull"]


epsilon = 1
# Fix zero denominators
denominator = denominator.replace(0, epsilon)


# Default assignment
rydex_ratio = np.full_like(denominator, fill_value=np.nan, dtype=np.float64)
rydex_ratio_temp = numerator / denominator
rydex_ratio_temp = rydex_ratio_temp.iloc[1:]


# Case 1: denom > 0 and num > 0
mask1 = (denominator > 0) & (numerator > 0)
rydex_ratio[mask1] = numerator[mask1] / denominator[mask1]

# Case 2: denom < 0 and num < 0 → set to 1.0  (undefined, neutral)
mask2 = (denominator < 0) & (numerator < 0)
rydex_ratio[mask2] = 1.0

# Case 3: denom > 0 and num < 0 → very bullish
mask3 = (denominator > 0) & (numerator < 0)
rydex_ratio[mask3] = -1*abs(denominator[mask3])*abs(numerator[mask3])/(abs(denominator[mask3])+abs(numerator[mask3]))

# Case 4: denom < 0 and num > 0 → very bearish
mask4 = (denominator < 0) & (numerator > 0)
rydex_ratio[mask4] = abs(denominator[mask4])*abs(numerator[mask4])/(abs(denominator[mask4])+abs(numerator[mask4]))

rydex_ratio = pd.Series(rydex_ratio)
#Clip extreme values
lower = rydex_ratio.quantile(0.02)
upper = rydex_ratio.quantile(0.98)

rydex_ratio = rydex_ratio.clip(lower=lower, upper=upper)

# Assign to DataFrame
pivot["rydex_ratio"] = rydex_ratio.values

from sklearn.preprocessing import MinMaxScaler

# Reshape for sklearn (expects 2D input)
scaler = MinMaxScaler(feature_range=(-1, 2))
scaled_values = scaler.fit_transform(pivot[["rydex_ratio"]])

# Assign scaled values to new column
pivot["rydex_ratio_scaled"] = scaled_values

# Optional: drop intermediate columns if only ratio is desired
result = pivot[["rydex_ratio_scaled"]].reset_index()



# Save or inspect result
print(result.tail())  # last few rows
result.to_csv("rydex_ratio_cashflow_output.csv", index=False)


#plot
result.set_index("as_of_date", inplace=True)
result.plot()

result.tail(300).plot()


# Load the CSV file
df_SPY = pd.read_csv("SPY.csv", parse_dates=["date"])
# Ensure correct sorting
df_SPY = df_SPY.sort_values(by=["TICKER", "date"])
df_SPY["FutDiff"] = df_SPY["PRC"].shift(-1)-df_SPY["PRC"]
df_SPY.set_index("date", inplace=True)
joined = df_SPY.join(result)
joined.dropna(inplace=True)
import scipy
sc = scipy.stats.spearmanr(joined["rydex_ratio_scaled"],joined["FutDiff"])
print("spearman corr statistic", sc[0])
print("spearman corr pvalue", sc[1])



