# 🚀 VIPER Live Trading Bot - Finalized Launch System

**✅ SYSTEM READY FOR LAUNCH**

A high-performance automated trading system with mandatory Docker and MCP (Model Context Protocol) enforcement for live cryptocurrency trading.

## 🎯 Quick Launch

**🚀 One-Command Launch (Recommended):**
```bash
python launch_viper.py
```

**📊 System Status Check:**
```bash
python system_launch_status.py
```

**🔧 Direct Launch Options:**
```bash
# Quick start trading
python start_trading.py

# Complete AI/ML system  
python scripts/launch_complete_system.py

# Integrated system with multiple modes
python scripts/launch_integrated_system.py demo
python scripts/launch_integrated_system.py status
python scripts/launch_integrated_system.py monitor
```

## ✅ System Ready Status

The VIPER trading system has been finalized and is ready for launch with:
- ✅ All critical launch scripts validated and working
- ✅ Syntax errors fixed in core system files
- ✅ Master launcher providing interactive menu
- ✅ Comprehensive system status validation
- ✅ Docker and dependency validation
- ✅ Multiple launch modes supported

## 🔒 System Requirements (MANDATORY)

**CRITICAL:** This system operates in LIVE TRADING mode only. All components require:

- **Docker & Docker Compose** - Mandatory for all operations
- **MCP Server** - Required for system coordination  
- **Valid Bitget API credentials** - Real trading credentials only
- **Redis** - For data caching and coordination
- **GitHub PAT** - For MCP integration

## 🚨 Live Trading Warning

**THIS SYSTEM EXECUTES REAL TRADES WITH REAL MONEY**

- No simulation or paper trading mode
- All trades are executed on live markets
- Losses can occur - use proper risk management
- Ensure you understand the risks before running

# 🚀 VIPER Live Trading Bot - Docker & MCP Enforced System

**⚠️ LIVE TRADING SYSTEM ONLY - NO MOCK DATA OR DEMO MODE**

A high-performance automated trading system with mandatory Docker and MCP (Model Context Protocol) enforcement for live cryptocurrency trading.

## 🎯 THE EASIEST SETUP EVER! (1 Command)

```bash
python viper.py
```

**This opens an interactive menu where you can setup and start trading in under 2 minutes!**

**🚀 CRYPTO-OPTIMIZED FOR LAUNCH:**
- **Lower Timeframes**: 1m, 5m, 15m optimized for crypto speed
- **ALL PAIRS SCANNED**: Automatically trades all available USDT pairs  
- **Just Add API Keys**: Everything else is handled automatically
- **Ready to Trade**: Start making money immediately after setup

---

## 🚀 Quick Start - THE EASIEST SETUP EVER!

### Super Simple Method (Recommended)
```bash
python viper.py
```
Interactive menu that guides you through everything!

### Direct Commands Method
1. **Setup:** `python setup.py`
2. **Add API keys** to `.env` file 
3. **Start trading:** `python start_trading.py`

### Want to Test First?
```bash
python demo.py
```
Safe demo mode with simulated data - no real money!

---

## ⚡ What You Get

- **🤖 AI Trading**: VIPER algorithm makes smart trades 24/7
- **🛡️ Risk Management**: Automatic stop-losses and limits
- **📊 Real-time Monitoring**: Live dashboard and performance tracking
- **💰 Multiple Markets**: Bitcoin, Ethereum, 500+ cryptocurrencies
- **🔒 Secure**: Encrypted API keys and secure connections

## 🎮 Demo Mode Available!

Test everything safely before live trading:
```bash
python demo.py
```
- See exactly how the system works
- No real money or API keys needed
- Perfect for learning and testing

---

## 🔧 System Architecture

The system uses a microservices architecture with Docker enforcement:

- **MCP Server** (Port 8015) - System coordination
- **Live Trading Engine** (Port 8007) - Trade execution
- **Risk Manager** (Port 8002) - Position and risk control
- **Exchange Connector** (Port 8005) - Bitget API integration
- **Market Data Manager** (Port 8003) - Real-time data feeds
- **Redis** (Port 6379) - Data caching and messaging

## ⚙️ Configuration

Key environment variables (all in `.env`):

```bash
# Trading Mode (ENFORCED)
USE_MOCK_DATA=false
FORCE_LIVE_TRADING=true
MANDATORY_DOCKER=true
MANDATORY_MCP=true

# Bitget API (REQUIRED)
BITGET_API_KEY=your_real_api_key
BITGET_API_SECRET=your_real_api_secret  
BITGET_API_PASSWORD=your_real_api_password

# Risk Management
RISK_PER_TRADE=0.02
MAX_LEVERAGE=50
MAX_POSITIONS=15
DAILY_LOSS_LIMIT=0.03
```

## 🛡️ Safety Features

- **Emergency Stop System** - Immediate position closure
- **Risk Limits** - Automatic position sizing and limits
- **Docker Health Checks** - Service monitoring and restart
- **MCP Validation** - Ensures system coordination
- **Real-time Monitoring** - Live performance tracking

## 📊 Monitoring

Access the monitoring dashboard:

- **Grafana:** http://localhost:3000 
- **Prometheus:** http://localhost:9090
- **MCP Server:** http://localhost:8015

## 🚫 What Was Removed

This version has all demo/mock functionality removed:

- All demo_*.py files
- All test_*.py files  
- Mock data generation functions
- Simulation modes
- Development validation scripts

## 🔧 Troubleshooting

### Docker Issues
```bash
# Check Docker status
docker compose ps

# Restart services  
docker compose down && docker compose up -d

# View logs
docker compose logs -f
```

### MCP Server Issues
```bash
# Check MCP server health
curl http://localhost:8015/health

# Restart MCP server
docker compose restart mcp-server
```

## ⚠️ Important Notes

- **No Demo Mode:** This system only operates with real money
- **Docker Required:** All operations require Docker services
- **MCP Required:** System coordination requires MCP server
- **API Credentials:** Must use valid Bitget production credentials
- **Risk Management:** Built-in limits protect against large losses

To contribute to this project:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Run tests to ensure everything works
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Requirements

- Python 3.7+
- pip

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Status

🚧 This project is currently under development. More features and documentation coming soon!
