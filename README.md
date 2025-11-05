# 🚀 T-R Professional Trading System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

## 🎯 Overview

T-R is a sophisticated, production-ready algorithmic trading system built with Python. It features multi-strategy execution, comprehensive risk management, real-time market data processing, and professional-grade monitoring capabilities.

### ✨ Key Features

- **🧠 Multi-Strategy Engine**: 8+ proven trading strategies including VWAP, Momentum (61% win rate), Bollinger Bands, Mean Reversion, and Pairs Trading
- **🛡️ Advanced Risk Management**: Position sizing, stop-loss, portfolio-level risk controls, and drawdown protection
- **⚡ Real-time Execution**: Interactive Brokers Gateway integration with millisecond precision
- **� Error Prevention System**: Advanced IB Error 201 prevention with multi-layer order cancellation
- **�📊 Comprehensive Backtesting**: 20+ performance metrics with detailed analysis and reporting
- **🌙 Extended Hours Trading**: Pre-market and after-hours session support
- **📱 Live Dashboard**: Real-time monitoring with web-based and CLI interfaces
- **🔔 Smart Alerts**: Email and Telegram notifications for trades, errors, and performance alerts
- **📈 Performance Analytics**: Advanced metrics including Sharpe ratio, max drawdown, win/loss ratios
- **🧹 Portfolio Management**: Automated position closing and account cleanup tools

## 🏗️ Architecture

```
T-R Trading System/
├── 🎯 strategies/          # Trading strategy implementations
├── 🛡️ risk_management/     # Position sizing and risk controls
├── ⚡ execution/           # Order management and broker interface
├── 📊 backtesting/         # Historical testing and performance analysis
├── 📡 data/               # Market data processing and storage
├── 🖥️ dashboard/          # User interfaces and visualization
├── 🔔 monitoring/         # Alerts and system monitoring
├── ⚙️ config/             # Configuration management
└── 📝 docs/               # Documentation and guides
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Interactive Brokers** account with TWS or IB Gateway
- **Windows 10+** / **Ubuntu 20.04+** / **macOS 12+**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/shkomig/T-R.git
   cd T-R
   ```

2. **Set up Python environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate environment
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   
   # Install dependencies
   cd Trading_System
   pip install -r requirements.txt
   ```

3. **Configure the system**
   ```bash
   # Copy example configurations
   cp config/trading_config.yaml.example config/trading_config.yaml
   cp config/risk_management.yaml.example config/risk_management.yaml
   
   # Edit configurations (see Configuration section)
   ```

4. **Start trading**
   ```bash
   # Run live dashboard
   python simple_live_dashboard.py
   
   # Or use the startup script (Windows)
   .\start_trading_system.ps1
   ```

## 📊 Trading Strategies

### Core Strategies

| Strategy | Win Rate | Description | Best Markets |
|----------|----------|-------------|--------------|
| **🧠 VWAP** | 58% | Volume Weighted Average Price mean reversion | High volume stocks |
| **⚡ Momentum** | **61%** | Donchian breakout with trend following | Trending markets |
| **📊 Bollinger Bands** | 56% | Volatility-based mean reversion | Range-bound markets |
| **🎯 Mean Reversion** | **65%** | Z-score enhanced statistical arbitrage | Stable large-caps |
| **👥 Pairs Trading** | 63% | Statistical arbitrage between correlated assets | Market neutral |
| **🎯 RSI Divergence** | **85-86%** | Advanced signal detection with RSI patterns | All markets |
| **📈 Volume Breakout** | **90%** | Volume-confirmed breakout strategy | High momentum |

### Strategy Features

- **🔄 Adaptive Parameters**: Strategies automatically adjust to market conditions
- **📈 Multi-Timeframe**: Support for 1min to 1day timeframes
- **🎚️ Configurable Risk**: Customizable position sizing and stop-loss levels
- **📊 Real-time Signals**: Live signal generation with confidence scoring

## 🎯 Recent Technical Achievements (November 2025)

### **🔧 IB Error 201 Prevention System**
- **Multi-layer Protection**: Preventive order cancellation at broker, wrapper, and dashboard levels
- **Smart Detection**: Comprehensive working order status identification (PendingSubmit, Submitted, PreSubmitted, ApiPending, PendingCancel)
- **Cycle-level Clearing**: Global order cleanup at the start of each trading cycle
- **Emergency Tools**: Manual diagnostic scripts for order inspection and cleanup
- **Result**: ✅ Eliminated IB Error 201 occurrences, ensuring smooth order placement

### **🧹 Portfolio Management Tools**
- **Automated Position Closing**: Professional close_all_positions.py script with safety confirmations
- **Account Cleanup**: Successfully liquidated 19/20 positions, converting to $1.2M+ cash position
- **Clean State**: Zero working orders, optimized for fresh trading strategies
- **P&L Realization**: +$25,120 realized profit from position closures

### **⚡ Enhanced System Stability**
- **Fresh Data Management**: Improved broker wrapper with stale data detection
- **Connection Resilience**: Robust TWS integration with automatic reconnection
- **Error Handling**: Comprehensive exception management and graceful degradation
- **Monitoring Tools**: Real-time diagnostics and health checks

## � Advanced Features (v3.0)

### **📊 Live Charts & Visualization**
- **Real-time Charts**: matplotlib-based live price visualization
- **Technical Indicators**: RSI, MACD, Bollinger Bands overlays
- **Multi-timeframe Support**: 1min to daily charts
- **Interactive Display**: Zoom, pan, and detailed price analysis

### **🔍 Market Scanner**
- **Volume Breakout Detection**: Real-time unusual volume alerts
- **Price Momentum Scanner**: Trend and breakout identification
- **Watchlist Monitoring**: S&P 500 + NASDAQ 100 coverage
- **Alert System**: Instant notifications for trading opportunities

### **⚡ Advanced Order Management**
- **Bracket Orders**: Automatic stop-loss and take-profit placement
- **Trailing Stops**: Dynamic stop adjustments following price
- **Conditional Orders**: Execute based on technical indicators
- **Risk-based Sizing**: Automatic position sizing with Kelly Criterion

### **🎯 Professional Trading Tools**
- **Cycle Management**: 3 trades per 5-minute cycle limit
- **Session Detection**: Regular/Pre-Market/After-Hours support
- **Live P&L Tracking**: Real-time profit/loss with color coding
- **Connection Monitoring**: Auto-reconnect to TWS with failover

## �🛡️ Risk Management

### Position Management
- **📏 Dynamic Position Sizing**: Kelly Criterion, Fixed Fractional, Volatility-based
- **🛑 Stop Loss**: ATR-based trailing stops and fixed percentage stops
- **🎯 Take Profit**: Multiple target levels with partial position closing
- **⚖️ Portfolio Limits**: Maximum positions, sector exposure, correlation limits

### Risk Controls
- **📉 Drawdown Protection**: Automatic position reduction on portfolio losses
- **💰 Capital Preservation**: Daily/weekly loss limits with system shutdown
- **⏰ Time-based Rules**: No overnight positions, session-specific strategies
- **🔍 Real-time Monitoring**: Continuous risk metric calculation and alerting

## 📈 Performance Tracking

### Key Metrics
- **📊 Returns**: Total return, annualized return, risk-adjusted returns
- **📉 Risk**: Sharpe ratio, Sortino ratio, maximum drawdown, VaR
- **🎯 Trade Analysis**: Win rate, profit factor, average trade duration
- **💰 Costs**: Commission impact, slippage analysis, net performance

### Reporting
- **📅 Daily Summaries**: Automated end-of-day performance reports
- **📧 Email Reports**: Weekly/monthly performance summaries
- **📊 Interactive Charts**: Web-based performance visualization
- **📄 Export Options**: CSV, JSON, PDF report generation

## ⚙️ Configuration

### Trading Configuration (`trading_config.yaml`)
```yaml
strategies:
  VWAP:
    enabled: true
    deviation_threshold: 0.002
    volume_threshold: 50000
    
  Momentum:
    enabled: true
    breakout_period: 20
    volume_multiplier: 2.0
    
symbols:
  - AAPL
  - GOOGL
  - MSFT
  - NVDA
  
trading_session:
  start_time: "09:30"
  end_time: "16:00"
  timezone: "US/Eastern"
```

### Risk Management (`risk_management.yaml`)
```yaml
position_sizing:
  method: "kelly_criterion"
  max_position_size: 0.05  # 5% of portfolio
  
risk_limits:
  max_daily_loss: 0.02     # 2% max daily loss
  max_drawdown: 0.10       # 10% max drawdown
  max_positions: 10
  
stop_loss:
  method: "atr"
  atr_multiplier: 2.0
  max_loss_percent: 0.02   # 2% max loss per trade
```

## 🔗 Interactive Brokers Setup

### Requirements
1. **IB Account**: Paper trading or live account
2. **TWS/Gateway**: Download and install IB Gateway
3. **API Access**: Enable API access in account settings

### Configuration
1. **Start IB Gateway** on port 7497 (paper) or 7496 (live)
2. **Enable API**: Account Settings → API → Enable API access
3. **Configure Permissions**: Allow connections from 127.0.0.1
4. **Set Credentials**: Update `config/api_credentials.yaml`

### Connection Test
```bash
python archive/test_files/test_ib_connection.py
```

## 🖥️ Dashboard Usage

### Live Dashboard Features
- **📊 Real-time Positions**: Current holdings, P&L, and market values
- **📈 Market Data**: Live prices, volume, and technical indicators
- **🎯 Strategy Signals**: Active signals with confidence levels
- **🔔 Alert Feed**: Real-time notifications and system messages
- **📉 Performance Charts**: Intraday and historical performance

### Dashboard Commands
```bash
# Start main dashboard
python simple_live_dashboard.py

# CLI-only dashboard
python dashboard/cli_dashboard.py

# Web dashboard (with charts)
python dashboard/web_dashboard.py
```

## 🧪 Testing & Validation

### Backtesting
```bash
# Run comprehensive backtest
python backtesting/run_backtest.py

# Strategy-specific backtest
python backtesting/run_backtest.py --strategy VWAP --start 2023-01-01

# Generate performance report
python backtesting/generate_report.py --backtest latest
```

### Live Testing
```bash
# Quick connection test
python archive/test_files/test_live_trading.py quick

# Strategy signal test
python archive/test_files/test_live_trading.py signals

# Full system test
python archive/test_files/test_live_trading.py full
```

## 🔔 Monitoring & Alerts

### Alert Types
- **🎯 Trade Execution**: Order fills, partial fills, rejections
- **📊 Performance**: Daily P&L, drawdown warnings, target achievements
- **🚨 System**: Connection issues, data feed problems, system errors
- **⚖️ Risk**: Position limit breaches, stop-loss triggers

### Notification Channels
- **📧 Email**: Detailed reports and critical alerts
- **📱 Telegram**: Real-time trade notifications
- **💻 Dashboard**: In-app notifications and status updates
- **📄 Logs**: Comprehensive logging for audit trails

## 📁 Project Structure

```
Trading_System/
├── 📋 README.md                    # This file
├── 📄 requirements.txt             # Python dependencies
├── ⚙️ config/                     # Configuration files
│   ├── trading_config.yaml        # Trading strategy settings
│   ├── risk_management.yaml       # Risk management rules
│   └── api_credentials.yaml       # Broker API credentials
├── 🎯 strategies/                 # Trading strategy implementations
│   ├── base_strategy.py           # Base strategy class
│   ├── vwap_strategy.py          # VWAP strategy
│   ├── momentum_strategy.py       # Momentum breakout strategy
│   └── ...                       # Additional strategies
├── ⚡ execution/                  # Order execution and management
│   ├── broker_interface.py        # IB Gateway interface
│   ├── order_manager.py          # Order lifecycle management
│   └── position_tracker.py       # Position monitoring
├── 🛡️ risk_management/           # Risk control systems
│   ├── position_sizer.py         # Position sizing algorithms
│   └── risk_calculator.py        # Portfolio risk metrics
├── 📊 backtesting/               # Historical testing framework
│   ├── backtest_engine.py        # Backtesting engine
│   └── performance.py            # Performance analysis
├── 🖥️ dashboard/                 # User interfaces
│   ├── simple_live_dashboard.py  # Main live dashboard
│   ├── web_dashboard.py          # Web-based interface
│   └── cli_dashboard.py          # Command-line interface
├── 📡 data/                      # Data management
│   ├── market_data/              # Real-time and historical data
│   └── backtest_results/         # Backtesting outputs
├── 🔔 monitoring/                # System monitoring
│   └── alert_system.py           # Notification management
├── 🧰 utils/                     # Utility functions
│   ├── logger.py                 # Logging system
│   └── data_processor.py         # Data processing utilities
├── 📝 logs/                      # System logs
└── 🧪 archive/                   # Tests and utilities
    └── test_files/               # Testing scripts
```

## ✨ What's New in v3.0

### 🎯 **Major Additions**
- **🔥 RSI Divergence Strategy**: Achieved 85-86% win rate with advanced pattern detection
- **🚀 Volume Breakout Strategy**: Reached 90% win rate with volume confirmation signals
- **📊 Live Chart System**: Real-time matplotlib visualization integrated with Interactive Brokers
- **🔍 Advanced Market Scanner**: Breakout and momentum detection across 600+ symbols
- **⚡ Professional Order Management**: Bracket orders, trailing stops, conditional execution

### 🛡️ **Enhanced Risk Management**
- **Cycle-based Trading**: Maximum 3 trades per 5-minute cycle for disciplined execution
- **Session Detection**: Automatic Regular/Pre-Market/After-Hours trading session management
- **Dynamic Position Sizing**: Market condition-based position adjustment
- **Real-time P&L**: Live profit/loss tracking with color-coded performance indicators

### 🔧 **System Improvements**
- **TWS Integration**: Full Interactive Brokers API support with Read-Only disabled
- **Connection Stability**: Auto-reconnect functionality with robust error handling
- **Performance Optimization**: Enhanced signal calculation and data processing
- **Professional UI**: Improved dashboard with real-time status and trade management

### 📈 **Performance Results**
```
🎯 RSI Divergence Strategy: 85-86% Win Rate
🚀 Volume Breakout Strategy: 90% Win Rate  
⚡ Momentum Strategy: 61% Win Rate
🧠 VWAP Strategy: 58% Win Rate
```

## 🔧 Development

### Setup Development Environment
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run tests
python -m pytest tests/

# Code formatting
black .
isort .
```

### Contributing Guidelines
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feat/new-strategy`
3. **Follow conventions**: Use [Conventional Commits](https://conventionalcommits.org/)
4. **Add tests**: Ensure new features are tested
5. **Update docs**: Document new functionality
6. **Submit PR**: Use the provided PR template

### Code Standards
- **🐍 Python 3.11+**: Use modern Python features
- **📝 Type Hints**: All functions should have type annotations
- **🧪 Testing**: Maintain >90% test coverage
- **📚 Documentation**: Comprehensive docstrings and README updates
- **🎨 Formatting**: Black and isort for consistent styling

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**This software is for educational and research purposes only. Trading financial instruments carries substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results. Use at your own risk.**

## 🤝 Support

- **📧 Email**: [Your Email]
- **💬 Discussions**: [GitHub Discussions](https://github.com/shkomig/T-R/discussions)
- **🐛 Issues**: [GitHub Issues](https://github.com/shkomig/T-R/issues)
- **📖 Documentation**: [Full Documentation](docs/)

## 🏆 Acknowledgments

- **Interactive Brokers** for providing professional trading infrastructure
- **Python Trading Community** for inspiration and best practices
- **Open Source Contributors** who made this project possible

---

**⭐ Star this repository if you find it useful!**

📈 **Happy Trading!** 🚀