import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def pair_short_long(df, short_dte_range, long_dte_range, option_type_filter):

    df2 = df.copy()
    df2['lastTradeDate'] = pd.to_datetime(df2['lastTradeDate'])

    if 'mid_price' not in df2.columns:
        raise KeyError("'mid_price' column not found in DataFrame")

    if option_type_filter:
        df2 = df2[df2['option_type'].str.lower() == option_type_filter.lower()]

    short_opts = df2[(df2['days_to_expiry'] >= short_dte_range[0]) & (df2['days_to_expiry'] <= short_dte_range[1])].copy()
    long_opts  = df2[(df2['days_to_expiry'] >= long_dte_range[0])  & (df2['days_to_expiry'] <= long_dte_range[1])].copy()

    print(f"Short candidates: {len(short_opts)}  |  Long candidates: {len(long_opts)}")

    pairs = pd.merge(
        short_opts,
        long_opts,
        on=['lastTradeDate', 'strike', 'option_type'],
        suffixes=('_short', '_long'),
        how='inner'
    )

    if 'mid_price_short' in pairs.columns and 'mid_price_long' in pairs.columns:
        pairs = pairs.dropna(subset=['mid_price_short', 'mid_price_long'])
    else:
        mp_cols = [c for c in pairs.columns if 'mid_price' in c]
        if len(mp_cols) >= 2:
            pairs = pairs.dropna(subset=mp_cols[:2])
        else:
            raise KeyError("expected merged mid_price columns (mid_price_short, mid_price_long) not found.")

    pairs = pairs.sort_values('lastTradeDate').reset_index(drop=True)

    return pairs


def backtest_iv_hv_arbitrage(df, short_dte_range, long_dte_range, option_type_filter, plot):
    
    pairs = pair_short_long(df, short_dte_range, long_dte_range, option_type_filter)

    if pairs.empty:
        print("no valid pairs found for given date ranges")
        return None

    
    if 'mid_price_long' in pairs.columns and 'mid_price_short' in pairs.columns:
        mid_long = 'mid_price_long'
        mid_short = 'mid_price_short'
    else:
        mid_cols = [c for c in pairs.columns if 'mid_price' in c]
        if len(mid_cols) >= 2:
            mid_short, mid_long = mid_cols[0], mid_cols[1]
        else:
            raise KeyError("could not find mid_price columns after merge")

    pairs['spread_price'] = pairs[mid_long].astype(float) - pairs[mid_short].astype(float)

    pairs = pairs.sort_values('lastTradeDate')

    pairs['spread_change'] = pairs.groupby('lastTradeDate')['spread_price'].transform(lambda x: x - x.shift(1))

    daily = pairs.groupby('lastTradeDate').agg({'spread_change': 'sum'}).reset_index()

    daily = daily.dropna(subset=['spread_change']).reset_index(drop=True)

    if daily.empty:
        print("after computing daily changes, no data remains")
        return None

    daily['cum_pnl'] = daily['spread_change'].cumsum()

    returns = daily['spread_change']
    mean_ret = returns.mean()
    std_ret = returns.std(ddof=0)

    sharpe_ratio = (mean_ret / (std_ret + 1e-12)) * np.sqrt(252) if std_ret > 0 else np.nan

    cumulative_pnl = daily['cum_pnl'].iloc[-1]

    rolling_max = daily['cum_pnl'].cummax()
    drawdown = rolling_max - daily['cum_pnl']
    max_drawdown = drawdown.max()

    total_trades = len(pairs) 
    win_rate = (daily['spread_change'] > 0).sum() / len(daily) if len(daily) > 0 else np.nan

    print(f"Sharpe Ratio:     {sharpe_ratio:.2f}")
    print(f"Cumulative P&L:   {cumulative_pnl:.6f}")
    print(f"Max Drawdown:     {max_drawdown:.6f}")
    print(f"Total Trades:     {total_trades}")
    print(f"Win Rate:         {win_rate*100:.2f}%")

    if plot:
        plt.figure(figsize=(10, 6))
        plt.plot(daily['lastTradeDate'], daily['cum_pnl'], label="Cumulative P&L")
        plt.title("Calendar Spread Strategy Performance")
        plt.xlabel("Date")
        plt.ylabel("P&L (price units)")
        plt.legend()
        output_dir = "plots"
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(os.path.join(output_dir, "calendar_spread.png"), dpi=300, bbox_inches='tight')
        plt.show()

    return {
        'pairs_df': pairs,
        'daily': daily,
        'sharpe_ratio': sharpe_ratio,
        'cumulative_pnl': float(cumulative_pnl),
        'max_drawdown': float(max_drawdown),
        'total_trades': int(total_trades),
        'win_rate': float(win_rate)
    }
