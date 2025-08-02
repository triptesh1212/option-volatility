import yfinance as yf
import pandas as pd

import yfinance as yf
import pandas as pd

def get_option_data(ticker_symbol, num_expiries):
    try:
        ticker = yf.Ticker(ticker_symbol)
        expiries = ticker.options

        if not expiries:
            raise Exception(f"no option expiries found for {ticker_symbol}")

        df_list = []

        for expiry in expiries[:num_expiries]:
            try:
                option_chain = ticker.option_chain(expiry)

                calls = option_chain.calls.copy()
                puts = option_chain.puts.copy()

                calls["option_type"] = "call"
                puts["option_type"] = "put"

                current_df = pd.concat([calls, puts], ignore_index=True)
                current_df["expiration"] = pd.to_datetime(expiry)

                # drop rows with missing price data
                current_df = current_df.dropna(subset=["strike", "lastPrice", "bid", "ask"])

                df_list.append(current_df)

            except Exception as e:
                print(f"skipping expiry {expiry} due to error: {e}")
                continue

        if not df_list:
            raise Exception("no valid option data found for any expiry")

        df = pd.concat(df_list, ignore_index=True)
        return df

    except Exception as e:
        print(f"failed to fetch option data for {ticker_symbol}: {e}")
        return pd.DataFrame()
