# Binance USDT-M Futures CLI Trading Bot

A production-ready, CLI-based trading bot for Binance USDT-M Futures with comprehensive order types, advanced trading strategies, robust validation, and structured logging.

## 🎯 Project Overview

This trading bot provides a modular and professional Python implementation for executing various order types on Binance USDT-M Futures. Built with code quality, correctness, and maintainability in mind, it includes extensive input validation, error handling, and detailed logging.

**Key Highlights:**
- Clean, modular architecture
- Production-ready code with no placeholders
- Comprehensive input validation
- Structured logging to file and console
- Advanced trading strategies (TWAP, Grid Trading)
- Futures-compatible order implementations

## ✨ Features

### Basic Order Types
- **Market Orders**: Immediate buy/sell execution at current market price
- **Limit Orders**: Buy/sell at specified price with GTC (Good-Till-Cancelled) time-in-force

### Advanced Order Types
- **Stop-Limit Orders**: Trigger limit order when stop price is reached
- **OCO-Style Orders**: Simulated One-Cancels-Other using Take-Profit and Stop-Loss market orders
- **TWAP Strategy**: Time-Weighted Average Price - split large orders into time-distributed slices
- **Grid Trading**: Place multiple limit orders at equal intervals within a price range

### Core Capabilities
- ✅ Modular, well-structured codebase
- ✅ Comprehensive CLI interface
- ✅ Input validation for all parameters
- ✅ Detailed logging to `bot.log`
- ✅ Error handling with graceful recovery
- ✅ Environment-based configuration
- ✅ Testnet support for safe testing

## 📋 Requirements

- Python 3.9 or higher
- Binance Futures account (use testnet for testing)
- API key and secret from Binance

## 🚀 Setup Instructions

### 1. Clone or Download the Project

```bash
cd binance_bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `python-binance` - Official Binance API wrapper
- `python-dotenv` - Environment variable management

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Binance API credentials:

```env
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
USE_TESTNET=True
```

**⚠️ IMPORTANT: Always use testnet for development and testing!**

Get testnet credentials at: https://testnet.binancefuture.com/

### 4. Verify Setup

Test your configuration:

```bash
python src/market_orders.py BTCUSDT BUY 0.001
```

If successful, you'll see order confirmation and details logged to `bot.log`.

## 📖 Usage Examples

### Market Orders

Execute immediate buy/sell at market price:

```bash
# Buy 0.01 BTCUSDT at market price
python src/market_orders.py BTCUSDT BUY 0.01

# Sell 0.005 ETHUSDT at market price
python src/market_orders.py ETHUSDT SELL 0.005
```

**Parameters:**
- `SYMBOL`: Trading pair (must end with USDT)
- `SIDE`: BUY or SELL
- `QUANTITY`: Order quantity (must be > 0)

### Limit Orders

Place orders at specific price levels:

```bash
# Sell 0.01 BTCUSDT at 52000
python src/limit_orders.py BTCUSDT SELL 0.01 52000

# Buy 0.02 ETHUSDT at 3000
python src/limit_orders.py ETHUSDT BUY 0.02 3000
```

**Parameters:**
- `SYMBOL`: Trading pair
- `SIDE`: BUY or SELL
- `QUANTITY`: Order quantity
- `PRICE`: Limit price (must be > 0)

### Stop-Limit Orders

Trigger a limit order when stop price is reached:

```bash
# Sell when price drops to 51000, place limit order at 50800
python src/advanced/stop_limit.py BTCUSDT SELL 0.01 51000 50800

# Buy when price rises to 3100, place limit order at 3120
python src/advanced/stop_limit.py ETHUSDT BUY 0.02 3100 3120
```

**Parameters:**
- `SYMBOL`: Trading pair
- `SIDE`: BUY or SELL
- `QUANTITY`: Order quantity
- `STOP_PRICE`: Price that triggers the order
- `LIMIT_PRICE`: Limit price for the triggered order

### OCO-Style Orders

Simulate OCO with Take-Profit and Stop-Loss:

```bash
# For a LONG position: Take profit at 52000, stop loss at 50000
python src/advanced/oco.py BTCUSDT SELL 0.01 52000 50000

# For a SHORT position: Take profit at 2900, stop loss at 3100
python src/advanced/oco.py ETHUSDT BUY 0.02 2900 3100
```

**Parameters:**
- `SYMBOL`: Trading pair
- `SIDE`: Opposite to your position (SELL for LONG, BUY for SHORT)
- `QUANTITY`: Position size
- `TAKE_PROFIT_PRICE`: Price to take profit
- `STOP_LOSS_PRICE`: Price to stop loss

**Note:** Both orders will remain active. Consider implementing cancellation logic or using position-based risk management.

### TWAP Strategy

Split large orders into time-distributed slices:

```bash
# Buy 0.1 BTCUSDT split into 5 slices with 10-second intervals
python src/advanced/twap.py BTCUSDT BUY 0.1 5 10

# Sell 1.0 ETHUSDT split into 10 slices with 30-second intervals
python src/advanced/twap.py ETHUSDT SELL 1.0 10 30
```

**Parameters:**
- `SYMBOL`: Trading pair
- `SIDE`: BUY or SELL
- `TOTAL_QUANTITY`: Total amount to trade
- `NUM_SLICES`: Number of equal slices
- `INTERVAL_SECONDS`: Time between slices

**Benefits:**
- Reduces market impact
- Achieves average execution price
- Useful for large orders

### Grid Trading Strategy

Place multiple limit orders across a price range:

```bash
# Place 5 buy orders between 50000 and 52000
python src/advanced/grid.py BTCUSDT 0.01 50000 52000 5

# Place 10 buy orders between 2800 and 3200
python src/advanced/grid.py ETHUSDT 0.02 2800 3200 10
```

**Parameters:**
- `SYMBOL`: Trading pair
- `QUANTITY_PER_GRID`: Quantity for each grid level
- `LOWER_PRICE`: Lower bound of price range
- `UPPER_PRICE`: Upper bound of price range
- `GRID_COUNT`: Number of grid levels (2-50)

**Strategy:**
- Places limit BUY orders at equal intervals
- Profits from price oscillations
- Orders fill as price moves through grid levels

## 📁 Project Structure

```
binance_bot/
│
├── src/
│   ├── config.py          # Binance client initialization & env loading
│   ├── logger.py          # Centralized logging configuration
│   ├── utils.py           # Input validation helpers
│   ├── market_orders.py   # Market order execution
│   ├── limit_orders.py    # Limit order execution
│   └── advanced/
│       ├── stop_limit.py  # Stop-limit orders
│       ├── oco.py         # OCO-style orders
│       ├── twap.py        # TWAP strategy
│       └── grid.py        # Grid trading strategy
│
├── bot.log                # Structured logging output
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
├── .env                  # Your API credentials (git-ignored)
└── README.md             # This file
```

## 📊 Logging

All activities are logged to `bot.log` with the following information:
- Timestamp
- Log level (DEBUG, INFO, WARNING, ERROR)
- Function name and line number
- Detailed messages
- Full stack traces for errors

**Log Levels:**
- **DEBUG**: Detailed validation and processing steps
- **INFO**: Order placements, confirmations, strategy execution
- **WARNING**: Non-critical issues
- **ERROR**: API errors, validation failures, exceptions

**Example log entry:**
```
2025-01-29 14:30:15 | INFO     | TradingBot | place_market_order:45 | Placing market order: BUY 0.01 BTCUSDT
2025-01-29 14:30:16 | INFO     | TradingBot | place_market_order:58 | Order placed successfully:
  Order ID: 12345678
  Symbol: BTCUSDT
  Side: BUY
  Type: MARKET
  Quantity: 0.01
  Status: FILLED
```

## 🔒 Security Best Practices

1. **Never commit `.env` file**: It contains sensitive API credentials
2. **Use testnet for development**: Always test on testnet before using mainnet
3. **Restrict API key permissions**: Only enable Futures trading, disable withdrawals
4. **Use IP whitelisting**: Restrict API key to specific IP addresses
5. **Monitor bot.log regularly**: Check for suspicious activities

## ⚠️ Important Notes

### Testnet Usage
**ALWAYS use Binance Futures Testnet for development, testing, and learning!**

- Testnet URL: https://testnet.binancefuture.com/
- Free testnet funds available
- No real money at risk
- Same functionality as mainnet

### Order Validation
- All symbols must end with "USDT" for USDT-M Futures
- Quantities and prices must be positive numbers
- Side must be either "BUY" or "SELL"
- Grid count limited to 50 for safety
- TWAP slices limited to 100 for safety

### OCO Orders Note
Binance Futures doesn't natively support OCO orders. This bot simulates OCO functionality using Take-Profit Market and Stop-Loss Market orders with `closePosition='true'`. Both orders remain active, and you may need to implement additional logic to cancel the unfilled order when one is triggered.

## 🐛 Error Handling

The bot implements comprehensive error handling:

1. **Input Validation**: All CLI arguments validated before API calls
2. **API Errors**: Caught and logged with detailed messages
3. **Network Issues**: Graceful handling of connection problems
4. **Partial Execution**: For TWAP and Grid strategies, tracks completed orders
5. **User Interruption**: Keyboard interrupts handled gracefully

**Common Errors:**
- Invalid symbol format → Must end with USDT
- Insufficient balance → Check account balance on testnet
- Invalid price/quantity → Must be positive numbers
- API rate limits → Reduce frequency of requests
- Position size errors → Ensure proper leverage settings

## 🔄 Future Improvements

Potential enhancements for future versions:

1. **Position Management**
   - Track open positions
   - Automatic position closing
   - Position size calculator

2. **Risk Management**
   - Portfolio-based position sizing
   - Maximum drawdown limits
   - Daily loss limits

3. **Advanced Strategies**
   - DCA (Dollar Cost Averaging)
   - Trailing stop orders
   - Iceberg orders
   - Market-making strategies

4. **Monitoring & Analytics**
   - Real-time P&L tracking
   - Performance metrics
   - Trade history analysis
   - Web dashboard

5. **Configuration Enhancements**
   - YAML/JSON configuration files
   - Multiple exchange support
   - Strategy backtesting

6. **Notifications**
   - Email alerts
   - Telegram notifications
   - Discord webhooks

7. **Database Integration**
   - Store trade history
   - Order tracking
   - Performance analytics

## 📞 Support & Resources

- **Binance Futures API Documentation**: https://binance-docs.github.io/apidocs/futures/en/
- **python-binance Documentation**: https://python-binance.readthedocs.io/
- **Binance Testnet**: https://testnet.binancefuture.com/

## 📄 License

This project is for educational and internship evaluation purposes.

## 🙏 Acknowledgments

- Binance for providing comprehensive API and testnet
- python-binance library maintainers
- Python community for excellent libraries and tools

---

**⚠️ Disclaimer**: This bot is for educational purposes. Trading cryptocurrencies carries significant risk. Always use testnet for learning and testing. Never invest more than you can afford to lose. This bot is not financial advice.