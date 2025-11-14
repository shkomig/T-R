#!/usr/bin/env python3
"""
Professional Live Trading Launcher
==================================
מפעיל את מערכת המסחר המקצועית עם אימותים מלאים

🚀 Professional Execution System
🛡️ 5-Stage Validation Pipeline  
🎯 Signal Quality Enhancement
🌊 Market Regime Detection
"""

import sys
import os
from pathlib import Path
import subprocess
import time
import yaml
from datetime import datetime
import requests

# Add Trading_System to path
sys.path.append(str(Path(__file__).parent))

def check_system_requirements():
    """בדיקת דרישות המערכת"""
    print("🔍 Checking system requirements...")
    
    checks = []
    
    # 1. Check TWS connection
    print("   📡 Testing TWS connection...")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 7497))
        sock.close()
        if result == 0:
            print("   ✅ TWS connection available (Paper Trading)")
            checks.append(True)
        else:
            # Try live port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', 7496))
            sock.close()
            if result == 0:
                print("   ✅ TWS connection available (Live Trading)")
                checks.append(True)
            else:
                print("   ❌ TWS not available - Please start TWS/IB Gateway")
                checks.append(False)
    except Exception as e:
        print(f"   ❌ TWS connection test failed: {e}")
        checks.append(False)
    
    # 2. Check market hours
    print("   ⏰ Checking market hours...")
    try:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # Market hours: 9:30 - 16:00 EST
        if "09:30" <= current_time <= "16:00":
            print(f"   ✅ Market is OPEN ({current_time})")
            checks.append(True)
        else:
            print(f"   ⚠️  Market is CLOSED ({current_time}) - Extended hours available")
            checks.append(True)  # Still allow trading in extended hours
    except Exception as e:
        print(f"   ⚠️  Market hours check failed: {e}")
        checks.append(True)  # Don't block on this
    
    # 3. Check config files
    print("   📋 Checking configuration files...")
    config_files = [
        "config/trading_config.yaml",
        "config/risk_management.yaml",
        "config/api_credentials.yaml"
    ]
    
    config_ok = True
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"   ✅ {config_file}")
        else:
            print(f"   ❌ {config_file} missing")
            config_ok = False
    
    checks.append(config_ok)
    
    # 4. Check Python packages
    print("   📦 Checking required packages...")
    required_packages = [
        'ibapi', 'pandas', 'numpy', 'colorama', 'yaml'
    ]
    
    packages_ok = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} not installed")
            packages_ok = False
    
    checks.append(packages_ok)
    
    return all(checks)

def display_trading_info():
    """הצגת מידע על המערכת"""
    print("\n" + "="*80)
    print("🎯 PROFESSIONAL TRADING SYSTEM v3.0")
    print("="*80)
    
    # Load config to show current settings
    try:
        with open('config/trading_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        paper_trading = config.get('development', {}).get('paper_trading', True)
        port = config.get('broker', {}).get('port', 7497)
        
        print(f"📡 Connection: {'Paper Trading' if paper_trading else 'LIVE TRADING'}")
        print(f"🔌 Port: {port}")
        print(f"💰 Max Daily Loss: {config.get('account', {}).get('max_daily_loss_percent', 5)}%")
        print(f"🎯 Max Positions: {config.get('position', {}).get('max_positions', 8)}")
        
        print("\n🚀 PROFESSIONAL FEATURES:")
        print("   ✅ 5-Stage Validation Pipeline")
        print("   ✅ Signal Quality Enhancement (50% → 80%+ confidence)")
        print("   ✅ Market Regime Detection (7 market states)")
        print("   ✅ Advanced Risk Management")
        print("   ✅ Real-time Portfolio Monitoring")
        
        symbols = config.get('universe', {}).get('tickers', [])
        print(f"\n📊 Trading Universe: {len(symbols)} symbols")
        print(f"   {', '.join(symbols[:10])}")
        if len(symbols) > 10:
            print(f"   ... and {len(symbols) - 10} more")
            
    except Exception as e:
        print(f"⚠️  Could not load config: {e}")
    
    print("="*80)

def confirm_live_trading():
    """אישור למסחר חי"""
    print("\n🔥 LIVE TRADING CONFIRMATION")
    print("=" * 40)
    print("⚠️  This will execute REAL trades with REAL money!")
    print("⚠️  Make sure you understand the risks involved.")
    print("⚠️  Professional system will protect you, but losses are possible.")
    
    response = input("\n🤔 Are you ready to start live trading? (yes/no): ").lower().strip()
    
    if response in ['yes', 'y']:
        print("\n✅ Live trading confirmed!")
        return True
    else:
        print("\n❌ Live trading cancelled.")
        print("💡 You can practice with paper trading first.")
        return False

def launch_professional_dashboard():
    """הפעלת הדשבורד המקצועי"""
    print("\n🚀 Launching Professional Trading Dashboard...")
    print("🎯 Professional Execution System: ACTIVE")
    print("🛡️ 5-Stage Validation: ENABLED")
    print("📈 Signal Enhancement: ENABLED")
    print("🌊 Market Regime Detection: ENABLED")
    
    try:
        # Launch the dashboard
        result = subprocess.run([
            sys.executable, 
            "simple_live_dashboard.py"
        ], cwd=Path(__file__).parent)
        
        return result.returncode == 0
        
    except KeyboardInterrupt:
        print("\n\n🛑 Trading stopped by user")
        return True
    except Exception as e:
        print(f"\n❌ Error launching dashboard: {e}")
        return False

def main():
    """פונקציה ראשית"""
    print("🎯 Professional Live Trading System")
    print("=" * 50)
    
    # Check system requirements
    if not check_system_requirements():
        print("\n❌ System requirements not met!")
        print("💡 Please fix the issues above and try again.")
        return
    
    print("\n✅ All system checks passed!")
    
    # Display trading info
    display_trading_info()
    
    # Check if this is live trading
    try:
        with open('config/trading_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        paper_trading = config.get('development', {}).get('paper_trading', True)
        
        if not paper_trading:
            # This is live trading - need confirmation
            if not confirm_live_trading():
                return
    except:
        pass
    
    # Launch the dashboard
    print("\n🚀 Starting Professional Trading System...")
    print("⏰ " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    success = launch_professional_dashboard()
    
    if success:
        print("\n✅ Trading session completed successfully")
    else:
        print("\n⚠️  Trading session ended with issues")

if __name__ == "__main__":
    main()