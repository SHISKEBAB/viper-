# VIPER Trading Bot - USDT Swap Integration Guide

## Overview

The VIPER Trading Bot has been fully integrated with Bitget's USDT-M futures (swap) API endpoints using proper HMAC-SHA256 authentication. This document explains the integration, configuration, and usage.

## Key Features

### 1. HMAC Authentication
- ✅ Secure HMAC-SHA256 signature generation
- ✅ Proper timestamp and message formatting
- ✅ All required headers: ACCESS-KEY, ACCESS-SIGN, ACCESS-TIMESTAMP, ACCESS-PASSPHRASE
- ✅ Shared authentication utility across all services

### 2. USDT Swap Endpoints
- ✅ Account balance and equity monitoring
- ✅ Position management for leveraged trades
- ✅ Real-time market data (ticker, orderbook, OHLCV)
- ✅ Order placement with leverage support
- ✅ Order management and status tracking

### 3. Enhanced Services

#### Exchange Connector (`services/exchange-connector/`)
- Direct API integration with HMAC authentication
- USDT swap symbol support (BTCUSDT_UMCBL format)
- Leverage support (1x to 125x)
- Proper order parameter formatting for futures

#### VIPER Scoring Service (`services/viper-scoring-service/`)
- Execution cost calculation optimized for futures markets
- USDT swap symbol recognition
- Enhanced volume-based cost adjustments
- Tighter spreads for futures trading

#### Market Data Manager (`services/market-data-manager/`)
- HMAC authenticated market data retrieval
- Priority symbol list for USDT swaps
- Enhanced caching for futures data

#### Live Trading Engine (`services/live-trading-engine/`)
- USDT swap focused trading
- Leverage and risk management
- Real-time position monitoring

## Symbol Format

### Standard Format
```
BTCUSDT_UMCBL  # Bitcoin USDT-M futures
ETHUSDT_UMCBL  # Ethereum USDT-M futures
BNBUSDT_UMCBL  # BNB USDT-M futures
```

### Product Type
- `UMCBL` = USDT-M futures (perpetual swaps)
- `marginCoin` = `USDT`

## API Authentication

### HMAC Signature Generation
```python
# Message format
message = timestamp + method + requestPath + body

# Signature generation
signature = base64.b64encode(
    hmac.new(
        api_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
).decode('utf-8')
```

### Required Headers
```json
{
    "ACCESS-KEY": "your_api_key",
    "ACCESS-SIGN": "generated_signature",
    "ACCESS-TIMESTAMP": "timestamp_in_milliseconds",
    "ACCESS-PASSPHRASE": "your_passphrase",
    "Content-Type": "application/json",
    "locale": "en-US"
}
```

## Order Parameters

### Market Order (Long)
```json
{
    "symbol": "BTCUSDT_UMCBL",
    "productType": "UMCBL",
    "marginCoin": "USDT",
    "side": "open_long",
    "orderType": "market",
    "size": "0.001",
    "timeInForce": "IOC"
}
```

### Limit Order (Short)
```json
{
    "symbol": "ETHUSDT_UMCBL",
    "productType": "UMCBL",
    "marginCoin": "USDT",
    "side": "open_short",
    "orderType": "limit",
    "size": "0.01",
    "price": "3000.0",
    "timeInForce": "GTC"
}
```

## Configuration

### Environment Variables
```bash
# API Credentials
BITGET_API_KEY=your_api_key
BITGET_API_SECRET=your_api_secret
BITGET_API_PASSWORD=your_passphrase

# Trading Configuration
DEFAULT_LEVERAGE=20
RISK_PER_TRADE=0.02
POSITION_SIZE_USDT=100
```

### Service Configuration
```bash
# Service Ports
EXCHANGE_CONNECTOR_PORT=8000
VIPER_SCORING_SERVICE_PORT=8009
MARKET_DATA_MANAGER_PORT=8001

# VIPER Scoring
VIPER_THRESHOLD_HIGH=75
EXECUTION_COST_THRESHOLD=3.0
```

## Validation

### Connection Test
```bash
# Run USDT swap connection validation
python validate_usdt_swap_connection.py
```

### Expected Output
```
✅ PASS Credentials Check: All credentials properly configured
✅ PASS Signature Generation: Signature length: 44
✅ PASS Account Access: USDT Equity: $1000.00
✅ PASS Market Data - BTCUSDT_UMCBL: Price: $45000.0
✅ PASS Order Preparation: All parameters formatted correctly
```

## API Endpoints

### Account & Positions
- **Account Balance**: `/api/mix/v1/account/account`
- **All Positions**: `/api/mix/v1/position/allPosition`
- **Set Leverage**: `/api/mix/v1/account/setLeverage`

### Market Data
- **Ticker**: `/api/mix/v1/market/ticker`
- **Order Book**: `/api/mix/v1/market/depth`
- **OHLCV Data**: `/api/mix/v1/market/candles`

### Trading
- **Place Order**: `/api/mix/v1/order/placeOrder`
- **Cancel Order**: `/api/mix/v1/order/cancel-order`
- **Order Status**: `/api/mix/v1/order/detail`
- **Open Orders**: `/api/mix/v1/order/current`

## Service Usage

### Exchange Connector
```python
# Create USDT swap order
POST /api/orders
{
    "symbol": "BTCUSDT_UMCBL",
    "side": "long",
    "type": "market",
    "amount": 0.001,
    "leverage": 20
}
```

### VIPER Scoring
```python
# Get enhanced score for USDT swap
POST /api/score
{
    "symbol": "BTCUSDT_UMCBL",
    "market_data": {...}
}
```

### Market Data Manager
```python
# Get USDT swap ticker
GET /api/ticker/BTCUSDT_UMCBL
```

## Execution Cost Optimization

### Cost Calculation for USDT Swaps
- **BTC**: ~$0.12 base spread (very tight futures)
- **ETH**: ~$0.16 base spread (tight futures)
- **Major Alts**: ~$0.25 base spread
- **Others**: ~$0.50 base spread

### Volume Adjustments
- **$50M+**: 30% discount (very liquid)
- **$20M+**: 10% discount (liquid)
- **$10M+**: Normal cost
- **$5M+**: 30% increase
- **$1M+**: 2x cost
- **<$1M**: 5x cost (avoid)

## Risk Management

### Position Limits
- Maximum leverage: 125x (configurable)
- Risk per trade: 2% (configurable)
- Maximum concurrent positions: 10
- Maximum daily loss: $1000 USDT

### Circuit Breakers
- 5 consecutive losses trigger cooldown
- 1-hour cooldown period
- Automatic position size reduction

## Error Handling

### Common Errors
1. **Invalid signature**: Check timestamp and message format
2. **Invalid symbol**: Ensure UMCBL format (e.g., BTCUSDT_UMCBL)
3. **Insufficient margin**: Check USDT balance
4. **Rate limiting**: Respect 2 requests/second limit

### Debugging
```python
# Enable debug logging
LOG_LEVEL=DEBUG

# Check authenticator status
GET /health
# Look for "hmac_authenticator": true
```

## Performance Optimization

### Rate Limiting
- Maximum 2 requests per second
- Intelligent batching for market data
- Request queuing for order management

### Caching
- 5-minute TTL for market data
- Position cache with real-time updates
- Balance cache with periodic refresh

## Security Considerations

### API Security
- Never expose credentials in logs
- Use environment variables for sensitive data
- Rotate API keys regularly
- Monitor API usage for anomalies

### Network Security
- Use HTTPS for all API calls
- Validate SSL certificates
- Implement request timeouts
- Use circuit breakers for fault tolerance

## Monitoring

### Health Checks
```bash
# Exchange Connector
curl http://localhost:8000/health

# VIPER Scoring Service  
curl http://localhost:8009/health

# Market Data Manager
curl http://localhost:8001/health
```

### Metrics
- Order success rate
- API response times
- Authentication failures
- Position P&L tracking

## Troubleshooting

### Common Issues

1. **DNS Resolution Failures**
   - Issue: Cannot resolve api.bitget.com
   - Solution: Check network configuration or firewall settings

2. **Authentication Failures**
   - Issue: Invalid signature errors
   - Solution: Verify timestamp format and message construction

3. **Symbol Not Supported**
   - Issue: Trading pair not found
   - Solution: Use UMCBL format (e.g., BTCUSDT_UMCBL)

4. **Insufficient Permissions**
   - Issue: API key lacks trading permissions
   - Solution: Enable futures trading in Bitget API settings

### Support Resources
- Bitget API Documentation: https://bitgetlimited.github.io/apidoc/en/mix/
- VIPER Bot Logs: Check service logs for detailed error messages
- Validation Script: Run `validate_usdt_swap_connection.py` for diagnostics

## Conclusion

The VIPER Trading Bot is now fully integrated with Bitget's USDT-M futures API, providing:
- Secure HMAC authentication
- Comprehensive USDT swap trading support
- Enhanced execution cost optimization
- Robust error handling and monitoring
- Complete documentation and validation tools

All services are configured to work seamlessly with USDT swap endpoints, ensuring optimal performance for leveraged cryptocurrency trading.