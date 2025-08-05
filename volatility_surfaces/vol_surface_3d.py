import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from mpl_toolkits.mplot3d import Axes3D

def plot_vol_surface(df, option_type):
    df = df[df['option_type'] == option_type]

    df = df.dropna(subset=['strike', 'time_to_expiry', 'iv_brent'])

    strikes = df["strike"].values
    times = df["time_to_expiry"].values
    ivs = df["iv_brent"].values

    strike_grid = np.linspace(strikes.min(), strikes.max(), 100)
    time_grid = np.linspace(times.min(), times.max(), 100)
    strike_mesh, time_mesh = np.meshgrid(strike_grid, time_grid)

    # Interpolate using cubic method
    iv_grid = griddata(
        points=(strikes, times),
        values=ivs,
        xi=(strike_mesh, time_mesh),
        method='cubic'
    )

    fig = plt.figure(figsize=(12, 7))
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(strike_mesh, time_mesh, iv_grid, cmap='viridis', edgecolor='none')

    ax.set_title(f"Volatility Surface - {option_type.capitalize()} Options")
    ax.set_xlabel("Strike")
    ax.set_ylabel("Time to Expiry (Years)")
    ax.set_zlabel("Implied Volatility")

    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
    plt.tight_layout()
    plt.savefig(f"plots_vol_surface_{option_type}.png")
    plt.show()


