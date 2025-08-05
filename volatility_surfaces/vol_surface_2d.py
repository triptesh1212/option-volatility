# file: vol_surface.py
import pandas as pd
import matplotlib.pyplot as plt

def plot_iv_smiles(df, option_type):
    df = df[df['option_type'] == option_type]
    expiries = sorted(df['expiration'].unique())

    plt.figure(figsize=(10, 6))
    for expiry in expiries:
        subset = df[df['expiration'] == expiry]
        plt.plot(subset['strike'], subset['iv_brent'], label=str(expiry.date()))

    plt.xlabel("Strike Price")
    plt.ylabel("Implied Volatility (IV)")
    plt.title(f"Volatility Smile for {option_type.capitalize()} Options")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"plots_vol_smile_{option_type}.png")
    plt.show()
