#!/bin/bash
# Quick Setup for Live Trading
# ============================

echo "🎯 Setting up Professional Live Trading System..."

# 1. Switch to live trading mode
echo "📝 Updating configuration for live trading..."

# Update trading_config.yaml - switch to live trading
python -c "
import yaml
with open('config/trading_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Switch to live trading
config['development']['paper_trading'] = False
config['broker']['use_delayed_data'] = False

# Add live trading settings
config['broker']['live_trading'] = {
    'enabled': True,
    'require_market_hours': True,
    'check_positions_on_startup': True,
    'validate_orders': True
}

with open('config/trading_config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)

print('✅ Trading config updated for live trading')
"

# 2. Update risk management for live trading
echo "🛡️ Updating risk management settings..."

python -c "
import yaml
with open('config/risk_management.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Conservative settings for live trading
config['account']['max_daily_loss_percent'] = 5.0
config['account']['max_daily_loss_amount'] = 5000
config['risk_management']['max_daily_loss'] = 0.05
config['risk_management']['max_single_position_risk'] = 0.03
config['risk_management']['auto_halt_trading'] = True

with open('config/risk_management.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)

print('✅ Risk management updated for live trading')
"

echo ""
echo "✅ Live Trading Setup Complete!"
echo ""
echo "🔥 READY TO TRADE:"
echo "   📡 Mode: LIVE TRADING"
echo "   🛡️ Max Daily Loss: 5%"
echo "   🎯 Professional System: ENABLED"
echo "   📈 Signal Enhancement: ACTIVE"
echo ""
echo "🚀 To start trading:"
echo "   python start_professional_trading.py"
echo ""
echo "⚠️  REMINDER: This will trade with REAL money!"
echo "    Make sure TWS is running and connected."