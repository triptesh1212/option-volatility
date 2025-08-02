# SPY Option Volatility

**A tool for estimating and analyzing implied volatility from SPY (S&P 500 ETF) option chains**

---

## Overview

This project estimates **implied volatility (IV)** from live SPY option chain data, constructs **volatility surfaces**, and backtests **IV-driven trading strategies**. It includes an interactive web app for visualizing volatility smiles, surfaces, and backtest performance.

---

## Features

- **Live Option Chain Fetching** via yfinance APIs
- **Implied Volatility Estimation** with Brent's Method
  - Pricing American options using Binomial Tree Model
  - Estimates implied volatility from mid-market option prices

