import numpy as np
import pandas as pd
from pykalman import KalmanFilter
import matplotlib.pyplot as plt

def apply_kalman_filter(series):
    
    kf = KalmanFilter(initial_state_mean=series.iloc[0], n_dim_obs=1)

    smoothed_state_means, _ = kf.smooth(series.values)

    return smoothed_state_means.flatten()

def smooth_iv_over_time(df, plot_sample=False):
    
    df = df.sort_values(by=["strike", "expiration", "date"])

    smoothed = []

    for (strike, expiration), group in df.groupby(["strike", "expiration"]):
        group = group.sort_values("date")

        if len(group) < 3:
            smoothed.extend([np.nan] * len(group))
            continue

        try:
            smoothed_iv = apply_kalman_filter(group["iv_brent"])
            smoothed.extend(smoothed_iv)

            if plot_sample and np.random.rand() < 0.01:
                plt.plot(group["date"], group["iv_brent"], label="original", marker='o')
                plt.plot(group["date"], smoothed_iv, label="smoothed", marker='x')
                plt.title(f"Strike: {strike}, Expiry: {expiration.date()}")
                plt.legend()
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.show()

        except Exception as e:
            print(f"Skipping smoothing for strike {strike}, expiry {expiration}: {e}")
            smoothed.extend([np.nan] * len(group))

    df["iv_smoothed"] = smoothed
    return df
