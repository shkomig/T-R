# AI Trading System

## Overview
Advanced automated trading system designed for stock traders, focusing on 30-minute candles with low-risk strategies and connection to Interactive Brokers (Port 7497).

## Features
- 🤖 AI-powered trading strategies
- 📊 Real-time market data processing
- 🛡️ Comprehensive risk management
- 📈 Multiple technical indicators
- 🔄 Backtesting engine
- 📱 Real-time monitoring and alerts
- 🔗 Interactive Brokers integration
- 🎛️ **3 Professional Dashboard Interfaces** (NEW!)
  - 🌐 Web Dashboard with WebSocket real-time updates
  - 📓 Jupyter Notebook for advanced analysis
  - 💻 CLI Dashboard for quick monitoring

## Project Structure
```
Trading_System/
├── config/              # Configuration files
├── data/                # Data storage
├── strategies/          # Trading strategies
├── indicators/          # Custom indicators
├── risk_management/     # Risk management modules
├── execution/           # Order execution
├── backtesting/         # Backtesting engine
├── monitoring/          # Monitoring and alerts
├── dashboard/           # 🎛️ 3 Dashboard Interfaces (NEW!)
│   ├── web_dashboard.py          # Web interface
│   ├── notebook_dashboard.ipynb  # Jupyter notebook
│   ├── cli_dashboard.py          # CLI interface
│   ├── README_DASHBOARD.md       # Dashboard guide
│   └── COMPARISON.md             # Interface comparison
└── utils/               # Utility functions
```

## Installation

### Prerequisites
- Python 3.10 or higher
- Interactive Brokers TWS or IB Gateway
- TA-Lib library

### Steps

1. **Clone the repository**
```bash
cd c:\Vs-Pro\TR\Trading_System
```

2. **Create virtual environment**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies**
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Install TA-Lib** (Windows)
- Download TA-Lib wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
- Install: `pip install TA_Lib-0.4.XX-cpXX-cpXX-win_amd64.whl`

5. **Configure credentials**
- Copy `config/api_credentials.yaml`
- Fill in your IB account details
- Never commit this file to Git

## Quick Start

### 1. Configure the System
Edit `config/trading_config.yaml` and `config/risk_management.yaml` with your preferences.

### 2. Test IB Connection
```python
from execution.broker_interface import IBBroker

broker = IBBroker()
broker.connect()
print("Connected!" if broker.is_connected() else "Connection failed")
```

### 3. Run Backtesting
```python
from backtesting.backtest_engine import BacktestEngine

engine = BacktestEngine()
results = engine.run_backtest(start_date="2023-01-01", end_date="2024-12-31")
print(results.summary())
```

### 4. Start Paper Trading
```powershell
python main.py --mode paper
```

## Trading Strategies

### 1. EMA Cross Strategy
- Fast EMA (12) crosses Slow EMA (26)
- Signal confirmation with volume
- Risk: 2% per trade, R:R = 2:1

### 2. VWAP Strategy
- Entry on 0.5% deviation from VWAP
- Volume confirmation required
- Mean reversion approach

### 3. Volume Breakout Strategy
- 1.5x average volume threshold
- 3-candle confirmation
- Momentum-based entries

## Risk Management

### Core Principles
- Maximum 2% risk per trade
- Maximum 5 concurrent positions
- 5% maximum drawdown limit
- Stop after 3 consecutive losses

### Position Sizing
- Risk-based calculation
- Volatility adjustment
- Account for stop loss distance

## Configuration

### Trading Config (`trading_config.yaml`)
- Market hours and timeframes
- Strategy parameters
- Execution settings

### Risk Management (`risk_management.yaml`)
- Position sizing rules
- Stop loss/Take profit settings
- Drawdown limits
- Emergency controls

### API Credentials (`api_credentials.yaml`)
⚠️ **Keep this file secure and never commit to Git**

## Development

### Running Tests
```powershell
pytest tests/ -v
```

### Code Style
```powershell
black .
flake8 .
```

### Type Checking
```powershell
mypy .
```

## Monitoring

### Dashboard
Access the web dashboard at `http://localhost:8000`

### Alerts
- Email notifications
- Telegram messages
- System logs

## Performance Metrics

### Tracked Metrics
- Total Return
- Sharpe Ratio
- Sortino Ratio
- Maximum Drawdown
- Win Rate
- Profit Factor

## Deployment

### Paper Trading
1. Start with paper trading account
2. Monitor for 2-4 weeks
3. Verify all strategies work correctly

### Live Trading
1. Start with small capital (5-10%)
2. Use one strategy initially
3. Gradually increase size
4. Monitor closely

## Safety Features

### Kill Switch
Automatically closes all positions if:
- Drawdown exceeds 7%
- Daily loss exceeds 5%
- Manual trigger activated

### Circuit Breakers
- Stop trading after max consecutive losses
- Cool-down periods after loss limits
- Volatility-based trade restrictions

## Troubleshooting

### IB Connection Issues
- Verify TWS/Gateway is running
- Check port 7497 is accessible
- Enable API in TWS settings
- Check firewall settings

### Installation Issues
- Ensure Python 3.10+
- Install TA-Lib separately
- Use compatible package versions

## Resources

### Documentation
- [Interactive Brokers API](https://interactivebrokers.github.io/)
- [TA-Lib Documentation](https://mrjbq7.github.io/ta-lib/)
- [Trading Psychology Resources](https://youtube.com/playlist?list=PLXWi52aRZnNEl1aL4ag3t0CFfDY_U7k69)

### Support
- Check logs in `logs/` directory
- Review error messages
- Consult documentation

## Roadmap

### Phase 1 - Infrastructure ✅ COMPLETED
- ✅ Basic infrastructure
- ✅ Configuration system
- ✅ IB connection module
- ✅ Data processing module
- ✅ Logging system

### Phase 2 - Technical Analysis ✅ COMPLETED
- ✅ Indicator development (15+ indicators)
- ✅ Volume analysis module
- ✅ Signal generators
- ✅ Data validation

### Phase 3 - Strategy Development (In Progress)
- ⏳ EMA Cross Strategy
- ⏳ VWAP Strategy
- ⏳ Volume Breakout Strategy
- ⏳ Risk management integration

### Phase 4 - Backtesting
- ⏳ Backtesting engine
- ⏳ Performance analytics
- ⏳ Optimization tools
- ⏳ Report generation

### Phase 5 - Execution
- ⏳ Paper trading
- ⏳ Dashboard & monitoring
- ⏳ Alert system
- ⏳ Position tracking

### Phase 6 - Live Trading
- ⏳ Live trading (small capital)
- ⏳ ML enhancements
- ⏳ Advanced features
- ⏳ Portfolio management

## License
Private use only. Not for distribution.

## Disclaimer
⚠️ **Trading involves substantial risk of loss.**
- Use at your own risk
- Start with paper trading
- Never risk more than you can afford to lose
- Past performance doesn't guarantee future results

## Contributing
This is a private project. For suggestions, create an issue.

---

**Status**: � Phase 2 Complete - Ready for Strategy Development!

**Current Progress**: 
- ✅ Infrastructure: 100%
- ✅ Technical Indicators: 100%
- ⏳ Strategies: 0%
- ⏳ Backtesting: 0%
- ⏳ Live Trading: 0%

**Last Updated**: October 29, 2025

**Quick Start**: See [QUICK_START.md](QUICK_START.md) for testing instructions!
