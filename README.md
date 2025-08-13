# SPY Option Volatility

**A tool for estimating and analyzing implied volatility from SPY (S&P 500 ETF) option chains**

---

## Overview

This project estimates **implied volatility (IV)** from SPY option chain data and backtests **IV-driven trading strategies**.

**[WIP]** An interactive web app for visualizing volatility smiles, surfaces, and backtest performance.

---

## Features
  
- **Implied Volatility Estimation** with Brent's Method
  - Pricing American options using Binomial Tree Model
  - Estimates implied volatility from mid-market option prices
    
- **Volatility Surfaces Construction** using Cubic Interpolation

- **IV Time Series Smoothening** using Kalman Filters

- **IV–HV arbitrage, Calendar Spread** strategies Backtesting

---

## Historical Backtesting Results: SPY Option Chain (2020–2022)

**IV-HV Arbitrage Strategy**

The backtesting was conducted on SPY options from 2020 to 2022. Only option contracts with expiry dates between **2 to 6 weeks** from the trade date were included. The strategy focused on implied volatility–historical volatility arbitrage.

| HV Window Size        | Sharpe Ratio  | P&L     | Max Drawdown | 
|-----------------------|---------------|---------|--------------|
| 20 | 0.81 | 1.56 % | -34.07 % |
| 30 | 1.24 | 2.41 % | -20.73 % |
| 40 | 1.08 | 2.03 % | -12.73 % |


**Vega-Based Calendar Spread Strategy**

Backtesting was performed on SPY option chains from 2020 to 2022. Trades involved selling a short-term option and buying a longer-term option with the same strike price, filtered by short expiry **15–25 days** and long expiry **40–54 days**. Positions were selected based on **vega exposure** estimated using a binomial pricing model.

| Vega Threshold | Sharpe Ratio  | P&L     | Max Drawdown | Total Trades | 
|----------------|---------------|---------|--------------|--------------|
| > 0.05 | 0.60 | 2.09 % | -13.10 % | 27776 |
| > 0.5 | 1.12 | 11.47 % | -13.10 % | 26736 |
| > 0.8 | 1.35 | 15.75 % | -11.41 % | 26024 |
