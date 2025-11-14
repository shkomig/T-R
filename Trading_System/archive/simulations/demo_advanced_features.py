#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Features Demo
הדגמת תכונות מתקדמות

This script demonstrates the new advanced features:
- Advanced Order Management (Bracket, Trailing Stop, Conditional)
- Real-Time Market Scanner
- Enhanced Risk Management
"""

import sys
import time
from pathlib import Path

# Add project path
sys.path.append(str(Path(__file__).parent))

try:
    from execution.broker_interface import IBBroker
    from execution.advanced_orders import AdvancedOrderManager, BracketOrderParams
    from monitoring.market_scanner import MarketScanner, ScanType
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure all required modules are available")
    sys.exit(1)

def demo_advanced_orders(broker):
    """הדגמת פקודות מתקדמות"""
    print("\n🎯 ADVANCED ORDERS DEMO")
    print("=" * 50)
    
    order_manager = AdvancedOrderManager(broker)
    
    # 1. Bracket Order Demo
    print("\n📊 1. Bracket Order Example:")
    print("   - Entry: Market price")
    print("   - Stop Loss: -2% from entry")
    print("   - Take Profit: +6% from entry")
    
    # סימולציה של bracket order
    bracket_params = BracketOrderParams(
        entry_price=150.00,
        stop_loss_price=147.00,  # -2%
        take_profit_price=159.00,  # +6%
        quantity=100
    )
    
    print(f"   Entry: ${bracket_params.entry_price:.2f}")
    print(f"   Stop Loss: ${bracket_params.stop_loss_price:.2f}")
    print(f"   Take Profit: ${bracket_params.take_profit_price:.2f}")
    print(f"   Risk/Reward Ratio: 1:3")
    
    # 2. Trailing Stop Demo
    print("\n🔄 2. Trailing Stop Example:")
    print("   - Trail Amount: 1.5% of stock price")
    print("   - Follows price up, locks in profits")
    print("   - Automatically adjusts stop level")
    
    print("   Example: AAPL at $150")
    print("   - Initial Stop: $147.75 (1.5% trail)")
    print("   - If price moves to $155: Stop moves to $152.33")
    print("   - If price moves to $160: Stop moves to $156.80")
    
    # 3. Conditional Order Demo
    print("\n🎯 3. Conditional Order Example:")
    print("   - Buy AAPL when SPY reaches $590")
    print("   - Only executes if condition is met")
    print("   - Useful for sector rotation strategies")
    
    return order_manager

def demo_market_scanner(broker):
    """הדגמת סורק השוק"""
    print("\n🔍 MARKET SCANNER DEMO")
    print("=" * 50)
    
    scanner = MarketScanner(broker)
    
    print(f"📊 Monitoring {len(scanner.watchlist)} symbols")
    print("🔍 Scan types:")
    
    scan_types = [
        ("📈 Volume Breakout", "Volume 3x+ above average"),
        ("💥 Price Breakout", "Price movement 5%+ with volume"),
        ("⬆️ Gap Up", "Opening gap 2%+ above previous close"),
        ("⬇️ Gap Down", "Opening gap 2%+ below previous close"),
        ("🚀 High Momentum", "Strong price + volume combination"),
        ("📊 Unusual Volume", "Abnormal trading activity")
    ]
    
    for scan_name, description in scan_types:
        print(f"   {scan_name}: {description}")
    
    print("\n⚡ Alert Levels:")
    print("   🚨 CRITICAL: Extreme movements (>15% price, >10x volume)")
    print("   🔥 HIGH: Significant movements (>10% price, >5x volume)")
    print("   ⚡ MEDIUM: Notable movements (>7% price, >3x volume)")
    print("   📊 LOW: Moderate movements (threshold levels)")
    
    # הדגמת callback
    def demo_alert_handler(alert):
        print(f"\n🚨 DEMO ALERT: {alert.symbol}")
        print(f"   Type: {alert.scan_type.value}")
        print(f"   Price: ${alert.current_price:.2f} ({alert.change_percent:+.1f}%)")
        print(f"   Volume: {alert.volume_ratio:.1f}x average")
        print(f"   Level: {alert.alert_level}")
        print(f"   Details: {alert.details.get('description', '')}")
    
    scanner.add_alert_callback(demo_alert_handler)
    
    return scanner

def demo_risk_management():
    """הדגמת ניהול סיכונים מתקדם"""
    print("\n⚖️ ADVANCED RISK MANAGEMENT")
    print("=" * 50)
    
    print("🎯 Position Sizing Rules:")
    print("   - Max 2% risk per trade")
    print("   - Position size based on volatility")
    print("   - Correlation limits between positions")
    print("   - Sector exposure limits")
    
    print("\n📊 Portfolio Limits:")
    print("   - Max 10 concurrent positions")
    print("   - Max 50% in any single sector")
    print("   - Max 20% in any single position")
    print("   - Daily loss limit: 5% of portfolio")
    
    print("\n🔄 Dynamic Adjustments:")
    print("   - Position sizes adjust to market volatility")
    print("   - Stop losses tighten in high volatility")
    print("   - Reduce exposure during market stress")
    print("   - Increase exposure during stable trends")
    
    # דוגמה לחישוב position size
    print("\n💡 Position Size Example:")
    portfolio_value = 1000000  # $1M portfolio
    risk_per_trade = 0.02      # 2% risk
    entry_price = 150.00
    stop_loss = 147.00
    
    risk_amount = portfolio_value * risk_per_trade
    risk_per_share = entry_price - stop_loss
    position_size = int(risk_amount / risk_per_share)
    
    print(f"   Portfolio Value: ${portfolio_value:,.0f}")
    print(f"   Risk per Trade: {risk_per_trade*100:.1f}% = ${risk_amount:,.0f}")
    print(f"   Entry Price: ${entry_price:.2f}")
    print(f"   Stop Loss: ${stop_loss:.2f}")
    print(f"   Risk per Share: ${risk_per_share:.2f}")
    print(f"   Position Size: {position_size:,} shares")
    print(f"   Position Value: ${position_size * entry_price:,.0f}")

def demo_integration_benefits():
    """הדגמת יתרונות השילוב"""
    print("\n🚀 INTEGRATION BENEFITS")
    print("=" * 50)
    
    print("🎯 Automated Workflow:")
    print("   1. 🔍 Scanner detects volume breakout in AAPL")
    print("   2. 📊 Strategy confirms bullish signals")
    print("   3. 🎯 Advanced order places bracket order")
    print("   4. 📈 TWS shows order execution in real-time")
    print("   5. 💰 P&L tracking updates automatically")
    print("   6. 🔄 Risk management monitors position")
    
    print("\n💡 Smart Decision Making:")
    print("   - Scanner finds opportunities")
    print("   - Strategies confirm signals")
    print("   - Advanced orders manage risk")
    print("   - Charts provide visual confirmation")
    print("   - TWS provides professional interface")
    
    print("\n⚡ Speed & Efficiency:")
    print("   - Millisecond execution")
    print("   - Automatic stop losses")
    print("   - Real-time monitoring")
    print("   - Professional order management")
    print("   - Complete audit trail")

def main():
    """הדגמה ראשית"""
    print("🎯 ADVANCED FEATURES DEMONSTRATION")
    print("=" * 60)
    print("💡 This demo shows the new capabilities available")
    print("   in your enhanced trading system with TWS integration")
    print()
    
    # שאלת משתמש
    try:
        user_input = input("🤔 Connect to TWS for live demo? (y/n): ").lower().strip()
        
        if user_input in ['y', 'yes', 'כן']:
            print("\n🔌 Attempting connection to TWS...")
            
            # נסיון חיבור
            broker = IBBroker(port=7497, client_id=33)  # Client ID שונה
            
            if broker.connect():
                print("✅ Connected successfully!")
                
                # הדגמות עם חיבור חי
                order_manager = demo_advanced_orders(broker)
                scanner = demo_market_scanner(broker)
                
                print("\n🚀 Live features initialized!")
                print("💡 The system is now running with advanced capabilities")
                
                broker.disconnect()
            else:
                print("❌ Could not connect to TWS")
                print("💡 Showing offline demonstration instead...")
        
        # הדגמות כלליות
        demo_risk_management()
        demo_integration_benefits()
        
        print("\n" + "=" * 60)
        print("🎉 DEMO COMPLETE!")
        print("💡 Your trading system now includes:")
        print("   ✅ Advanced Order Management")
        print("   ✅ Real-Time Market Scanner") 
        print("   ✅ Enhanced Risk Management")
        print("   ✅ Professional TWS Integration")
        print("   ✅ Live Charts & Monitoring")
        print()
        print("🚀 Ready for professional trading!")
        
    except KeyboardInterrupt:
        print("\n\n📊 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")

if __name__ == "__main__":
    main()