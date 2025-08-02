from utils.fetch_option_data import get_option_data
from utils.fetch_spot_price import get_spot_price

df = get_option_data("EZU")

print(df.head())

spot_price = get_spot_price("EZU")

print("Spot Price : ", spot_price)
