from utils.fetch_option_data import get_option_data
from utils.fetch_spot_price import get_spot_price
from utils.iv_estimator import estimate_iv

df = get_option_data("SPY", 10)

spot_price = get_spot_price("SPY")

df_iv = estimate_iv(df, spot_price, 0.01)

total_non_nan_iv = df_iv["iv_brent"].notna().sum()

total_nan_iv = len(df) - total_non_nan_iv

success_rate = 100 * total_non_nan_iv / len(df)

print(f"IV Estimation Converge Rate: {success_rate:.2f}%")

df_non_nan = df_iv[df_iv["iv_brent"].notna()]

comparison = df_non_nan[["strike", "option_type", "iv_brent", "impliedVolatility"]].copy()
comparison = comparison.rename(columns={
    "iv_brent": "estimated_iv",
    "impliedVolatility": "yahoo_iv"
})

print(comparison.head(20))