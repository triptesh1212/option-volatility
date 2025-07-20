import yfinance as yf 
import pandas as pd 

# EZU -> Eurozone ETF ~200 large and mid-cap EU companies

ticker = yf.Ticker("EZU")

expiries = ticker.options 

# todo : error handling if there is no option expiries

expiry = expiries[0]

option_chain = ticker.option_chain(expiry)

# new copy of the DataFrame
calls = option_chain.calls.copy() 
puts = option_chain.puts.copy()

calls["type"] = "call"
calls["type"] = "put"

df = pd.concat([calls, puts], ignore_index=True)
df['expiration'] = expiry 

# drops impliedVolatility from the data
df = df.drop(columns=["impliedVolatility"], errors='ignore')

# remove missing values
df = df.dropna(subset=["strike", "lastPrice", "bid", "ask"])

print(df.head())
