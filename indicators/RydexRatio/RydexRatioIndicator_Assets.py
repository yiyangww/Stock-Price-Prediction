
"""

Get data from WRDS: Home>Get Data>ETF Global>Fund Flow
This program calculates a proxy for the leveraged Rydex bull-bear asset ratio using the formula: 
(Bear Funds Assets + Money Market Assets) ÷ Bull Funds Assets 
But we are multiplying Money Market by 0.

The csv file has the following column headers: 
as_of_date, composite_ticker, shares_outstanding,	nav,	fundflow.  as_of_date is the date, composite_ticker is the ETF ticker,	fundflow is the cash flow. 
The dates are daily in frequency.  The composite_ticker contains the following tickers: 

See LeveragedETFs.txt

Originally:
if "rydex_ratio" < 1 = bullish
if "rydex_ratio" ≈  1 = neutral
if "rydex_ratio" > 1 = bearish



"""

import pandas as pd

# Load the data
df = pd.read_csv("Data.csv")

# Parse date
df["as_of_date"] = pd.to_datetime(df["as_of_date"])

# Define ticker groups

bull_funds = {"TQQQ", "UDOW", "UPRO", "UWM", "URTY","UCC", "UGE", "URE", "UPW", "UXI", "USD", "UCYB", "UCO", "UGL" ,"SOXL", "TECL", "MIDU", "SPX", "TNA","TSLR", "AMDL", "AMZZ","MSFL", "PTIR","TBF", "TBT", "TTT", "TBX", "TMV", "SJB"} 
bear_funds = {"SH", "SDS", "SPXU", "PSQ", "SQQQ", "SDOW", "TWM", "SRTY","SZK", "SCC", "BIS", "SSG", "SRS", "TECS", "SOXS", "FAZ","BITI"} 
money_market_funds = {"BIL", "SGOV", "SHV", "USFR"}

#Better results:
bull_funds = {"TQQQ"} 
bear_funds = {"SQQQ"} 
money_market_funds = {"BIL"}

# Compute total assets per row
df["assets"] = df["nav"] * df["shares_outstanding"]

# Classify the fund type
def classify(ticker):
    if ticker in bull_funds:
        return "Bull"
    elif ticker in bear_funds:
        return "Bear"
    elif ticker in money_market_funds:
        return "MM"
    else:
        return "Other"

df["fund_type"] = df["composite_ticker"].apply(classify)

# Pivot the data to get total assets per category per date
pivot = (
    df.pivot_table(index="as_of_date", columns="fund_type", values="assets", aggfunc="sum")
    .fillna(0)
)

# Ensure all required columns exist
for col in ["Bear", "Bull", "MM"]:
    if col not in pivot.columns:
        pivot[col] = 0

# Calculate the Rydex Ratio
pivot["rydex_ratio"] = (pivot["Bear"] + 1*pivot["MM"]) / pivot["Bull"]

# Output result
rydex_ratio = pivot[["rydex_ratio"]]
print(rydex_ratio.tail())

rydex_ratio.to_csv("rydex_ratio_assets_output.csv", index=True)


#plot
rydex_ratio.plot()

rydex_ratio.tail(300).plot()


# Load the CSV file
df_SPY = pd.read_csv("SPY.csv", parse_dates=["date"])
# Ensure correct sorting
df_SPY = df_SPY.sort_values(by=["TICKER", "date"])
df_SPY["FutDiff"] = df_SPY["PRC"].shift(-10)-df_SPY["PRC"]
df_SPY.set_index("date", inplace=True)
joined = df_SPY.join(rydex_ratio)
joined.dropna(inplace=True)
import scipy
sc = scipy.stats.spearmanr(joined["rydex_ratio"],joined["FutDiff"])
print("spearman corr statistic", sc[0])
print("spearman corr pvalue", sc[1])


