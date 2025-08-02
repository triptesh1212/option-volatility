import yfinance as yf 

def get_spot_price(ticker_symbol):
    
    ticker = yf.Ticker(ticker_symbol)
    
    data = ticker.history(period="1d", interval="1m")  # intraday 1-minute data
    
    if not data.empty:
        return data["Close"].iloc[-1]
    else:
        raise Exception(f"could not fetch price for {ticker_symbol}")