import yfinance as yf
import pandas as pd

def get_option_data(ticker_symbol):

    try:
        ticker = yf.Ticker(ticker_symbol)

        expiries = ticker.options

        if not expiries:
            raise Exception(f"no option expiries found for {ticker_symbol}")

        expiry = expiries[0] 

        option_chain = ticker.option_chain(expiry)

        # new copy of the DataFrame
        calls = option_chain.calls.copy()
        puts = option_chain.puts.copy()

        calls["option_type"] = "call"
        puts["option_type"] = "put"

        df = pd.concat([calls, puts], ignore_index=True)
        df["expiration"] = pd.to_datetime(expiry)

        # drops impliedVolatility from the data
        df = df.drop(columns=["impliedVolatility"], errors="ignore")

        # remove missing values
        df = df.dropna(subset=["strike", "lastPrice", "bid", "ask"])

        return df

    except Exception as e:
        print(f"failed to fetch option data for {ticker_symbol}: {e}")

        return pd.DataFrame() 
