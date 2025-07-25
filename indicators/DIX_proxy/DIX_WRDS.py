# -*- coding: utf-8 -*-
"""
Calculate the DIX (Dark Pool Index) using WRDS data
The Dark Pool Index (DIX) was originally constructed by SqueezeMetrics. 
It measures the percentage of off-exchange (dark pool) buying volume relative to total off-exchange volume.
The Millisecond Trade and Quote dataset includes several variables that 
allow you to construct a proxy for the Dark Pool Index (DIX), 
under the assumption that dark pool activity can be approximated by off-exchange trades, 
large institutional orders, and/or anonymously routed volume (as is often the case with TRF-reported transactions).
"""
import pandas as pd



#Obtain MSFT data from WRDS:
#Home>Get Data>TAQ>Millisecond Trade and Quote - "Daily Product". 2003 - present, updated daily.
#>TAQ Millisecond Tools>Millisecond Intraday Indicators by WRDS
#Download: total_vol_m	BuyVol_Retail	BuyVol_Inst20k	SellVol_Inst20k (or BuyVol_Inst50k	SellVol_Inst50k)

df = pd.read_csv("DIX_MillisecondIndicators_AAPL.csv")

# Step 1: Compute total institutional block volume
df['TotalInstVol'] = df['BuyVol_Inst20k'] + df['SellVol_Inst20k']

# Step 2: Compute the DIX proxy (institutional buy ratio)
df['DIX_proxy'] = df['BuyVol_Inst20k'] / df['TotalInstVol']

# Step 3: Institutional share of total market volume
df['InstVolShare'] = df['TotalInstVol'] / df['total_vol_m']

# Optional Step 4: Adjusted DIX proxy excluding retail volume
df['DIX_adj'] = (df['BuyVol_Inst20k'] - df['BuyVol_Retail']) / df['TotalInstVol']

# Display results
print(df[['DATE', 'DIX_proxy', 'InstVolShare', 'DIX_adj']])

df_out =  df[['DATE', 'DIX_proxy', 'InstVolShare', 'DIX_adj']]

df_out.to_csv("DIX_AAPL_out.csv")
