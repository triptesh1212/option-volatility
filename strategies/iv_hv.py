import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def backtest_iv_hv_arbitrage(df_kalman, window, threshold, plot=True):
    
    df_kalman = df_kalman.copy()
    df_kalman['date'] = df_kalman['lastTradeDate']
    
    df_daily = df_kalman.groupby('date').agg({
        'underlying_price': 'first',
        'iv_smoothed': 'mean'
    }).reset_index()

    # Calculate Historical Volatility (HV)
    df_daily['log_ret'] = np.log(df_daily['underlying_price'] / df_daily['underlying_price'].shift(1))
    df_daily['HV'] = df_daily['log_ret'].rolling(window).std() * np.sqrt(252)

    # Generate signals
    df_daily['signal'] = 0
    df_daily.loc[df_daily['iv_smoothed'] - df_daily['HV'] > threshold, 'signal'] = -1
    df_daily.loc[df_daily['iv_smoothed'] - df_daily['HV'] < -threshold, 'signal'] = 1

    # Simulate P&L
    df_daily['iv_change'] = df_daily['iv_smoothed'].diff()
    df_daily['daily_pnl'] = df_daily['signal'].shift(1) * df_daily['iv_change']

    df_daily = df_daily.dropna(subset=['daily_pnl'])

    # Calculate metrics
    cumulative_pnl = df_daily['daily_pnl'].cumsum()

    daily_std = df_daily['daily_pnl'].std()
    sharpe_ratio = np.sqrt(252) * df_daily['daily_pnl'].mean() / daily_std if daily_std != 0 else 0

    cumulative_pnl = df_daily['daily_pnl'].cumsum().fillna(0)

    rolling_max = cumulative_pnl.cummax()
    max_drawdown = (cumulative_pnl - rolling_max).min()
    total_trades = (df_daily['signal'].diff().abs() > 0).sum()
    win_rate = (df_daily['daily_pnl'] > 0).sum() / (df_daily['daily_pnl'] != 0).sum()

    # Print results
    print(f"Sharpe Ratio:     {sharpe_ratio:.2f}")
    print(f"Cumulative P&L:   {cumulative_pnl.iloc[-1]:.4f}")
    print(f"Max Drawdown:     {max_drawdown:.4f}")
    print(f"Total Trades:     {total_trades}")
    print(f"Win Rate:         {win_rate*100:.2f}%")

    if plot:
        plt.figure(figsize=(10, 6))
        plt.plot(df_daily['date'], cumulative_pnl, label="Cumulative P&L")
        plt.title("IV-HV Arbitrage Strategy Performance")
        plt.xlabel("Date")
        plt.ylabel("P&L (proxy units)")
        plt.legend()

        output_dir = "plots"
        os.makedirs(output_dir, exist_ok=True)

        plt.savefig(os.path.join(output_dir, "iv_hv_arbitrage.png"), dpi=300, bbox_inches='tight')
        plt.show()

    return {
        'sharpe_ratio': sharpe_ratio,
        'cumulative_pnl': cumulative_pnl.iloc[-1],
        'max_drawdown': max_drawdown,
        'total_trades': total_trades,
        'win_rate': win_rate
    }
