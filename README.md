# Binance Trading Bot

A Python bot for Binance Futures Testnet trading.

## Requirements
- Python 3.8+
- `python-binance` package

## Setup
1. Install dependencies:
```bash
pip install python-binance
```

2. Get API keys from [Binance Testnet](https://testnet.binancefuture.com)

## Usage
```bash
python trading_bot.py SYMBOL SIDE TYPE QUANTITY --api_key KEY --api_secret SECRET
```

### Examples:
```bash
# Market buy
python trading_bot.py BTCUSDT buy market 0.001 --api_key your_key --api_secret your_secret

# Limit sell
python trading_bot.py ETHUSDT sell limit 0.1 2500 --api_key your_key --api_secret your_secret
```
