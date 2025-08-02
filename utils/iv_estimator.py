import numpy as np
import pandas as pd 
from scipy.stats import norm
from scipy.optimize import brentq 


# Black-Scholes Pricing Formula

# S	- Spot Price - The current price of the underlying asset

# K	- Strike Price	- The fixed price at which the option can be exercised

# T	- Time to Expiry -	Time until the option expires

# r	- Risk-Free Interest Rate - The annualized risk-free interest rate 

# sigma - IV -	The implied volatility of the underlying asset 

# option_type -	Option Type	"call" or "put" 

def calculate_price(S, K, T, r, sigma, option_type):
    
    if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
        return 0.0

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == "put":
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise Exception("option_type must be 'call' or 'put'")
    

# Brent's Method to Estimate IV 
def implied_volatility_brent(market_price, S, K, T, r, option_type):
    
    if market_price <= 0 or T <= 0:
        return np.nan

    try:
        objective = lambda sigma: calculate_price(S, K, T, r, sigma, option_type) - market_price
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
    

def estimate_iv(option_df, spot_price, r):
    
    df = option_df.copy()

    # market price 
    df["mid_price"] = (df["bid"] + df["ask"]) / 2

    # time to expiry in years
    df["time_to_expiry"] = (df["expiration"] - pd.Timestamp.today()).dt.total_seconds() / (365 * 24 * 60 * 60)

    df["iv_brent"] = df.apply(lambda row: estimate_row_iv(row, spot_price, r), axis=1)

    return df