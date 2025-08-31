# VIPER Trading System - CCXT WebSocket Integration

## Overview

The VIPER trading system now includes **CCXT built-in WebSocket support** (free version) for real-time market data streaming. This provides ultra-low latency trading with live price feeds directly from Bitget's WebSocket API.

## Key Features

✅ **CCXT WebSocket Integration** - Uses CCXT's built-in WebSocket functionality (free version)  
✅ **Real-time Market Data** - Live ticker data, OHLCV streams, position updates  
✅ **Hybrid Architecture** - WebSocket data with REST API fallbacks  
✅ **Multi-pair Trading** - Simultaneous WebSocket feeds for multiple symbols  
✅ **$1 × 50x Leverage** - Proper notional value calculation ($1 margin × 50x = $50 notional)  
✅ **Position Monitoring** - Real-time position updates via WebSocket  

## Trading Modes

### 1. Enhanced REST Trader (Recommended)
- **File**: `run_live_trader.py`
- **Description**: Enhanced REST API trader with WebSocket real-time data
- **Features**:
  - Real-time price data via CCXT WebSocket feeds
  - REST API for trade execution and order management
  - Automatic fallback from WebSocket to REST if needed
  - 30 symbols monitored via WebSocket concurrently

### 2. Pure WebSocket Trader (Advanced)
- **File**: `run_live_trader_websocket.py`
- **Description**: 100% WebSocket-based trading system
- **Features**:
  - All market data via WebSocket streams
  - Multi-timeframe analysis with WebSocket OHLCV data
  - Real-time position and balance monitoring
  - Maximum speed with minimal latency

## Quick Start

### Launch Trading System
```bash
python launch_viper_websocket.py
```

This launcher provides:
1. **Enhanced REST Trader** - WebSocket data + REST execution
2. **Pure WebSocket Trader** - 100% WebSocket implementation
3. **WebSocket Test** - Verify CCXT WebSocket functionality
4. **Exit**

### Direct Launch Options

#### Enhanced REST Trader
```bash
python run_live_trader.py
```

#### Pure WebSocket Trader
```bash
python run_live_trader_websocket.py
```

#### Test WebSocket Functionality
```bash
python test_ccxt_websockets.py
```

## Configuration

### Environment Variables (.env)
```
# API Credentials
BITGET_API_KEY=your_api_key
BITGET_API_SECRET=your_api_secret
BITGET_API_PASSWORD=your_api_password

# Trading Configuration
MIN_MARGIN_PER_TRADE=1.0        # $1.0 margin as requested
MAX_LEVERAGE=50                 # 50x leverage
MAX_POSITIONS=15                # Maximum concurrent positions
RISK_PER_TRADE=0.001           # 0.1% risk per trade
TAKE_PROFIT_PCT=3.0            # 3% take profit
STOP_LOSS_PCT=2.0              # 2% stop loss
```

### Notional Value Calculation
- **Margin**: $1.00 (configurable via MIN_MARGIN_PER_TRADE)
- **Leverage**: 50x (configurable via MAX_LEVERAGE) 
- **Notional Value**: $1.00 × 50 = $50.00
- **Bitget Minimum**: $5.00 ✅ (requirement exceeded)

## WebSocket Features

### Available CCXT WebSocket Methods
- `watch_tickers()` - Real-time price data
- `watch_ohlcv()` - Live OHLCV data streams  
- `watch_positions()` - Real-time position updates
- `watch_balance()` - Live balance monitoring
- `watch_orders()` - Order status updates
- `watch_trades()` - Trade execution data

### Data Feeds
- **Ticker Data**: Real-time bid/ask/last prices for 30+ symbols
- **OHLCV Streams**: Multi-timeframe candlestick data (1m, 5m, 15m)
- **Position Updates**: Live position size, P&L, and status changes
- **Balance Monitoring**: Real-time account balance updates

## Architecture

### WebSocket Integration Flow
1. **Connection Setup**: CCXT establishes WebSocket connections to Bitget
2. **Data Streaming**: Real-time market data streams via WebSocket feeds
3. **Signal Generation**: Trading signals generated using WebSocket data
4. **Trade Execution**: Orders placed via REST API for reliability
5. **Position Monitoring**: Real-time position updates via WebSocket

### Thread Management
- **Main Thread**: Trading logic and decision making
- **WebSocket Thread**: Async WebSocket data collection
- **Data Synchronization**: Thread-safe data sharing with locks

## Benefits of WebSocket Integration

### Performance Improvements
- **Latency**: Sub-100ms data updates vs. 1000ms+ REST polling
- **Throughput**: Continuous data stream vs. periodic REST requests
- **Efficiency**: Single persistent connection vs. multiple HTTP requests
- **Real-time**: Live market data vs. snapshot data

### Trading Advantages
- **Faster Signals**: Real-time price action for quicker signal generation
- **Better Fills**: More accurate entry prices with live data
- **Position Monitoring**: Instant position updates and P&L tracking
- **Risk Management**: Real-time balance monitoring for position sizing

## Installation

### Requirements
```bash
pip install ccxt>=4.1.63  # CCXT with WebSocket support
pip install websockets>=12.0
pip install asyncio
```

### Complete Installation
```bash
pip install -r requirements.txt
```

## Usage Examples

### Basic WebSocket Test
```python
import ccxt
import asyncio

async def test_websockets():
    exchange = ccxt.bitget({
        'apiKey': 'your_key',
        'secret': 'your_secret', 
        'password': 'your_password'
    })
    
    # Watch live ticker data
    symbols = ['BTC/USDT', 'ETH/USDT']
    tickers = await exchange.watch_tickers(symbols)
    print(f"Live prices: {tickers}")

# Run test
asyncio.run(test_websockets())
```

### Enhanced Price Fetching
```python
# Get current price with WebSocket preference
current_price = trader.get_current_price_enhanced('BTC/USDT')
print(f"Real-time BTC price: ${current_price}")
```

## Monitoring and Logging

### Log Files
- `logs/viper_fixed_trader.log` - Enhanced REST trader logs
- `logs/viper_websocket_trader.log` - Pure WebSocket trader logs

### Real-time Status
- WebSocket connection status
- Data feed health monitoring
- Position sync verification
- Market data freshness checks

## Troubleshooting

### Common Issues

#### WebSocket Connection Errors
```
❌ WebSocket connection failed
```
**Solution**: Check API credentials and network connectivity

#### Missing Market Data
```
⚠️ No websocket ticker data for symbol
```
**Solution**: System automatically falls back to REST API

#### Thread Synchronization
```
⚠️ WebSocket data synchronization error
```
**Solution**: Data locks ensure thread safety, temporary issue resolves automatically

### Debug Mode
Enable detailed WebSocket logging:
```python
logging.getLogger().setLevel(logging.DEBUG)
```

## Support

### CCXT WebSocket Documentation
- [CCXT WebSocket Guide](https://github.com/ccxt/ccxt/wiki/Manual#websocket-api)
- [Bitget WebSocket API](https://bitgetlimited.github.io/apidoc/en/mix/#websocket-api)

### System Requirements
- Python 3.8+
- CCXT 4.1.63+
- Active internet connection
- Bitget API credentials

---

**Ready to trade with lightning-fast WebSocket data! 🚀📡**