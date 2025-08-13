import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from pricing_models.binomial_tree import calculate_price_bt

def calculate_vega_bt(S, K, T, r, sigma, steps=100, option_type="call", eps=1e-4):
   
    if T <= 0 or sigma <= 0:
        return 0.0

    # Price with slightly higher IV
    price_up = calculate_price_bt(S, K, T, r, sigma + eps, steps, option_type)

    # Price with slightly lower IV
    price_down = calculate_price_bt(S, K, T, r, sigma - eps, steps, option_type)

    vega = (price_up - price_down) / (2 * eps)

    return vega 

# Pair short-term and long-term options with same strike
def pair_short_long(df, short_dte_range, long_dte_range, option_type_filter):

    df2 = df.copy()
    df2['lastTradeDate'] = pd.to_datetime(df2['lastTradeDate'])

    if option_type_filter:
        df2 = df2[df2['option_type'].str.lower() == option_type_filter.lower()]

    short_options = df2[(df2['days_to_expiry'] >= short_dte_range[0]) & 
                     (df2['days_to_expiry'] <= short_dte_range[1])].copy()
    long_options  = df2[(df2['days_to_expiry'] >= long_dte_range[0])  & 
                     (df2['days_to_expiry'] <= long_dte_range[1])].copy()

    pairs = pd.merge(
        short_options,
        long_options,
        on=['lastTradeDate', 'strike', 'option_type'],
        suffixes=('_short', '_long'),
        how='inner'
    )

    if 'mid_price_short' in pairs.columns and 'mid_price_long' in pairs.columns:
        pairs = pairs.dropna(subset=['mid_price_short', 'mid_price_long'])
    else:
        raise KeyError("expected columns mid_price_short & mid_price_long not found after merge")

    return pairs.sort_values('lastTradeDate').reset_index(drop=True)


def backtest_calendar_spread(df, short_dte_range, long_dte_range, option_type_filter, plot=True):
    
    RISK_FREE_RATE = 0.05  

    pairs = pair_short_long(df, short_dte_range, long_dte_range, option_type_filter)

    # calculate vega for each leg
    pairs['vega_short'] = pairs.apply(
        lambda row: calculate_vega_bt(row['underlying_price_short'], row['strike'],
                            row['days_to_expiry_short'] / 365,
                            RISK_FREE_RATE, row['iv_brent_short']), axis=1)
    pairs['vega_long'] = pairs.apply(
        lambda row: calculate_vega_bt(row['underlying_price_long'], row['strike'],
                            row['days_to_expiry_long'] / 365,
                            RISK_FREE_RATE, row['iv_brent_long']), axis=1)

    pairs = pairs[(pairs['vega_short'] > 0.01) & (pairs['vega_long'] > 0.01)]

    pairs['spread_price'] = pairs['mid_price_long'] - pairs['mid_price_short']
    pairs['spread_change'] = pairs.groupby('lastTradeDate')['spread_price'].transform(lambda x: x - x.shift(1))

    daily = pairs.groupby('lastTradeDate').agg({'spread_change': 'sum'}).dropna().reset_index()
    daily['cum_pnl'] = daily['spread_change'].cumsum()

    returns = daily['spread_change']
    mean_ret, std_ret = returns.mean(), returns.std(ddof=0)
    sharpe_ratio = (mean_ret / (std_ret + 1e-12)) * np.sqrt(252) if std_ret > 0 else np.nan
    cumulative_pnl = daily['cum_pnl'].iloc[-1]
    max_drawdown = (daily['cum_pnl'].cummax() - daily['cum_pnl']).max()
    win_rate = (daily['spread_change'] > 0).sum() / len(daily) if len(daily) > 0 else np.nan
    
    # Print results
    print(f"Sharpe Ratio:   {sharpe_ratio:.2f}")
    print(f"Cumulative P&L: {cumulative_pnl:.2f}")
    print(f"Max Drawdown:   {max_drawdown:.2f}")
    print(f"Total Trades:   {len(pairs)}")
    print(f"Win Rate:       {win_rate*100:.2f}%")

    if plot:
        plt.figure(figsize=(10, 6))
        plt.plot(daily['lastTradeDate'], daily['cum_pnl'], label="Cumulative P&L")
        plt.title("Calendar Spread Strategy Performance")
        plt.xlabel("Date")
        plt.ylabel("P&L (price units)")
        plt.legend()
        os.makedirs("plots", exist_ok=True)
        plt.savefig("plots/calendar_spread.png", dpi=300, bbox_inches='tight')
        plt.show()

    return {
        'pairs_df': pairs,
        'daily': daily,
        'sharpe_ratio': sharpe_ratio,
        'cumulative_pnl': float(cumulative_pnl),
        'max_drawdown': float(max_drawdown),
        'total_trades': int(len(pairs)),
        'win_rate': float(win_rate)
    }
