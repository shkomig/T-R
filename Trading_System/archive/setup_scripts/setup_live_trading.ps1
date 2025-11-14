# Quick Setup for Live Trading (PowerShell)
# ==========================================

Write-Host "🎯 Setting up Professional Live Trading System..." -ForegroundColor Cyan

# 1. Switch to live trading mode
Write-Host "📝 Updating configuration for live trading..." -ForegroundColor Yellow

# Update trading_config.yaml
python -c @"
import yaml

# Load current config
with open('config/trading_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Switch to live trading
config['development']['paper_trading'] = False
config['broker']['use_delayed_data'] = False
config['broker']['port'] = 7496  # Live trading port

# Add live trading settings
if 'live_trading' not in config['broker']:
    config['broker']['live_trading'] = {}

config['broker']['live_trading'] = {
    'enabled': True,
    'require_market_hours': True,
    'check_positions_on_startup': True,
    'validate_orders': True
}

# Save updated config
with open('config/trading_config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False, indent=2)

print('✅ Trading config updated for live trading')
"@

# 2. Update risk management
Write-Host "🛡️ Updating risk management settings..." -ForegroundColor Yellow

python -c @"
import yaml

# Load risk config
with open('config/risk_management.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Conservative settings for live trading
config['account']['max_daily_loss_percent'] = 5.0
config['account']['max_daily_loss_amount'] = 5000

# Enhanced risk management
config['risk_management']['max_daily_loss'] = 0.05              # 5% daily loss limit
config['risk_management']['max_single_position_risk'] = 0.03    # 3% per position
config['risk_management']['auto_halt_trading'] = True          # Auto-stop on violations

# Save updated config
with open('config/risk_management.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False, indent=2)

print('✅ Risk management updated for live trading')
"@

Write-Host ""
Write-Host "✅ Live Trading Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🔥 READY TO TRADE:" -ForegroundColor Red
Write-Host "   📡 Mode: LIVE TRADING" -ForegroundColor White
Write-Host "   🔌 Port: 7496 (Live)" -ForegroundColor White  
Write-Host "   🛡️ Max Daily Loss: 5%" -ForegroundColor White
Write-Host "   🎯 Professional System: ENABLED" -ForegroundColor White
Write-Host "   📈 Signal Enhancement: ACTIVE" -ForegroundColor White
Write-Host ""
Write-Host "🚀 To start trading:" -ForegroundColor Cyan
Write-Host "   python start_professional_trading.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  REMINDER: This will trade with REAL money!" -ForegroundColor Red
Write-Host "    Make sure TWS is running on port 7496 and connected." -ForegroundColor Yellow

# Final confirmation
$confirmation = Read-Host "`n🤔 Are you sure you want to enable LIVE TRADING? (yes/no)"

if ($confirmation.ToLower() -eq "yes" -or $confirmation.ToLower() -eq "y") {
    Write-Host "`n🔥 LIVE TRADING ENABLED!" -ForegroundColor Red
    Write-Host "🚀 Run: python start_professional_trading.py" -ForegroundColor Cyan
} else {
    Write-Host "`n❌ Live trading setup cancelled." -ForegroundColor Yellow
    Write-Host "💡 You can practice with paper trading first." -ForegroundColor Cyan
    
    # Switch back to paper trading
    python -c @"
import yaml
with open('config/trading_config.yaml', 'r') as f:
    config = yaml.safe_load(f)
config['development']['paper_trading'] = True
config['broker']['port'] = 7497
with open('config/trading_config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False, indent=2)
print('📝 Switched back to paper trading mode')
"@
}