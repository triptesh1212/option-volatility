import numpy as np
from scipy.stats import norm


# European Option Pricing using Black-Scholes Formula

# S	- Spot Price - The current price of the underlying asset

# K	- Strike Price	- The fixed price at which the option can be exercised

# T	- Time to Expiry -	Time until the option expires

# r	- Risk-Free Interest Rate - The annualized risk-free interest rate 

# sigma - IV -	The implied volatility of the underlying asset 

# option_type -	Option Type	"call" or "put" 

def calculate_price_bs(S, K, T, r, sigma, option_type):
    
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