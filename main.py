import os
import pandas as pd
from utils.fetch_option_data import get_option_data
from utils.fetch_spot_price import get_spot_price
from utils.iv_estimator import estimate_iv_from_live_data, estimate_iv_from_historical_data
from volatility_surfaces.vol_surface_2d import plot_iv_smiles
from volatility_surfaces.vol_surface_3d import plot_vol_surface
from utils.kalman_filter import smooth_iv_over_time
from utils.load_historical_data import get_historical_data_for_iv_hv, get_historical_data_for_calendar_spread
from strategies.iv_hv import backtest_iv_hv_arbitrage
from strategies.calendar_spread import backtest_iv_hv_arbitrage


# <---- live data ----->

# df = get_option_data("SPY", 10)

# spot_price = get_spot_price("SPY")

# df_iv = estimate_iv_from_live_data(df, spot_price, 0.01)

# df_iv = estimate_iv_from_historical_data(df, 0.01)

# total_non_nan_iv = df_iv["iv_brent"].notna().sum()

# success_rate = 100 * total_non_nan_iv / len(df)

# print(f"IV Estimation Converge Rate: {success_rate:.2f}%")

# df_iv_non_nan = df_iv[df_iv["iv_brent"].notna()]

# plot_iv_smiles(df_iv_non_nan, 'call')

# plot_vol_surface(df_iv_non_nan, 'call')



# <--- IV-HV strategy backtest with historical data ---->

# df = get_historical_data_for_iv_hv()

# df_iv = estimate_iv_from_historical_data(df, 0.01)

# total_non_nan_iv = df_iv["iv_brent"].notna().sum()

# success_rate = 100 * total_non_nan_iv / len(df)

# print(f"IV Estimation Converge Rate: {success_rate:.2f}%")

# df_iv_non_nan = df_iv[df_iv["iv_brent"].notna()]

# df_kalman = smooth_iv_over_time(df_iv_non_nan)

# total_non_nan_kf = df_kalman['iv_smoothed'].notna().sum()

# success_rate = 100 * total_non_nan_kf / len(df_kalman)

# print(f"Smoothed IV Coverage (Kalman): {success_rate:.2f}%")

# backtest_iv_hv_arbitrage(df_kalman, 40, 0.05, True)



# <--- calendar spread strategy backtest with historical data ---->

intervals = [
    (15, 22),
    (23, 30),
    (31, 38),
    (39, 46),
    (47, 54)
]

for s, e in intervals:

    print(f"fetching data for expiry range {s}-{e} days")

    df = get_historical_data_for_calendar_spread(s, e)
    
    df_iv = estimate_iv_from_historical_data(df, 0.01)

    total_non_nan_iv = df_iv["iv_brent"].notna().sum()

    success_rate = 100 * total_non_nan_iv / len(df)

    print(f"IV Estimation Converge Rate: {success_rate:.2f}%")

    df_iv_non_nan = df_iv[df_iv["iv_brent"].notna()]

    df_kalman = smooth_iv_over_time(df_iv_non_nan)

    total_non_nan_kf = df_kalman['iv_smoothed'].notna().sum()

    success_rate = 100 * total_non_nan_kf / len(df_kalman)

    print(f"Smoothed IV Coverage (Kalman): {success_rate:.2f}%")

    df_kalman.to_csv(f"dataset/calendar_spread_{s}_{e}.csv", index=False)

    print("size of current dataframe = ", len(df_kalman))


df_list = []

for s, e in intervals:

    path = f"dataset/calendar_spread_{s}_{e}.csv"

    if os.path.exists(path):
        df_temp = pd.read_csv(path)
        df_list.append(df_temp)
        
df_kalman = pd.concat(df_list, ignore_index=True)


metrics = backtest_iv_hv_arbitrage(
    df_kalman, 
    short_dte_range=(15,25), 
    long_dte_range=(40,54), 
    option_type_filter='call',
    plot=True
)
