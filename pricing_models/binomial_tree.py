import numpy as np

# American Option Pricing using Binomial Tree Model

# S	- Spot Price - The current price of the underlying asset

# K	- Strike Price	- The fixed price at which the option can be exercised

# T	- Time to Expiry -	Time until the option expires

# r	- Risk-Free Interest Rate - The annualized risk-free interest rate 

# sigma - IV -	The implied volatility of the underlying asset 

# option_type -	Option Type	"call" or "put" 

def calculate_price_bt(S, K, T, r, sigma, steps, option_type):

    dt = T / steps
    u = np.exp(sigma * np.sqrt(dt))        # up factor
    d = 1 / u                              # down factor
    q = (np.exp(r * dt) - d) / (u - d)     # risk-neutral probability
    disc = np.exp(-r * dt)                 # discount per step

    asset_prices = np.array([S * (u ** j) * (d ** (steps - j)) for j in range(steps + 1)])

    if option_type == 'call':
        option_values = np.maximum(asset_prices - K, 0)
    elif option_type == "put":
        option_values = np.maximum(K - asset_prices, 0)
    else:
        raise Exception("option_type must be 'call' or 'put'")

    for i in range(steps - 1, -1, -1):
        asset_prices = asset_prices[:-1] / u  
        option_values = disc * (q * option_values[1:] + (1 - q) * option_values[:-1])

        if option_type == 'call':
            exercise = np.maximum(asset_prices - K, 0)
        else:
            exercise = np.maximum(K - asset_prices, 0)

        option_values = np.maximum(option_values, exercise)

    return option_values[0]