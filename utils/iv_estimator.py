import numpy as np
import pandas as pd 
from scipy.optimize import brentq     
from pricing_models.binomial_tree import calculate_price_bt

# Brent's Method to Estimate IV 
def implied_volatility_brent(market_price, S, K, T, r, option_type):
    
    if market_price <= 0 or T <= 0:
        return np.nan

    try:
        objective = lambda sigma: calculate_price_bt(S, K, T, r, sigma, 100, option_type) - market_price
        iv = brentq(objective, 1e-5, 5.0, maxiter=1500)
        return iv
    except Exception:
        return np.nan
    

def estimate_row_iv(row, spot_price, r):

    if row["time_to_expiry"] <= 0:
        return np.nan
    
    estimated_iv = implied_volatility_brent(row["mid_price"], spot_price, row["strike"], row["time_to_expiry"], 
                                            r, row["option_type"])
    
    return estimated_iv
    

def estimate_iv_from_live_data(option_df, spot_price, r):
    
    df = option_df.copy()

    # market price 
    df["mid_price"] = (df["bid"] + df["ask"]) / 2

    # time to expiry in years
    df["time_to_expiry"] = (df["expiration"] - pd.Timestamp.today()).dt.total_seconds() / (365 * 24 * 60 * 60)

    df["iv_brent"] = df.apply(lambda row: estimate_row_iv(row, spot_price, r), axis=1)

    return df

def estimate_iv_from_historical_data(option_df, r):
    
    df = option_df.copy()

    print("number of rows = ", len(df))

    # convert to numeric
    df['bid'] = pd.to_numeric(df['bid'], errors='coerce')
    df['ask'] = pd.to_numeric(df['ask'], errors='coerce')

    # market price 
    df["mid_price"] = (df["bid"] + df["ask"]) / 2

    # time to expiry in years
    df["time_to_expiry"] = (df["expiration"] - df["lastTradeDate"]).dt.total_seconds() / (365 * 24 * 60 * 60)

    df["iv_brent"] = df.apply(lambda row: estimate_row_iv(row, row['underlying_price'], r), axis=1)

    return df