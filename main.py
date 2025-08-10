from utils.fetch_option_data import get_option_data
from utils.fetch_spot_price import get_spot_price
from utils.iv_estimator import estimate_iv_from_live_data, estimate_iv_from_historical_data
from volatility_surfaces.vol_surface_2d import plot_iv_smiles
from volatility_surfaces.vol_surface_3d import plot_vol_surface
from utils.kalman_filter import smooth_iv_over_time
from utils.load_historical_data import get_historical_data
from strategies.iv_hv import backtest_iv_hv_arbitrage

# Fetch live data

# df = get_option_data("SPY", 10)

# spot_price = get_spot_price("SPY")

# df_iv = estimate_iv_from_live_data(df, spot_price, 0.01)

# Load historical data

df = get_historical_data()

df_iv = estimate_iv_from_historical_data(df, 0.01)

total_non_nan_iv = df_iv["iv_brent"].notna().sum()

success_rate = 100 * total_non_nan_iv / len(df)

print(f"IV Estimation Converge Rate: {success_rate:.2f}%")

df_iv_non_nan = df_iv[df_iv["iv_brent"].notna()]

#plot_iv_smiles(df_iv_non_nan, 'call')

#plot_vol_surface(df_iv_non_nan, 'call')

df_kalman = smooth_iv_over_time(df_iv_non_nan)

total_non_nan_kf = df_kalman['iv_smoothed'].notna().sum()

success_rate = 100 * total_non_nan_kf / len(df_kalman)

print(f"Smoothed IV Coverage (Kalman): {success_rate:.2f}%")

backtest_iv_hv_arbitrage(df_kalman, 20, 0.05, True)