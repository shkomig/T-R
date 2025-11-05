"""
Close All Positions Script
=========================
סגירת כל הפוזיציות הפתוחות ועדכון סטטוס החשבון
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from execution.broker_interface import IBBroker
from colorama import Fore, Style, init

init(autoreset=True)

def close_all_positions():
    """סגור את כל הפוזיציות הפתוחות"""
    print("🔄 Connecting to TWS...")
    broker = IBBroker(port=7497, client_id=1000)
    
    if not broker.connect():
        print("❌ Failed to connect to TWS")
        return False
    
    print("✅ Connected to TWS!")
    time.sleep(2)  # המתן להתחברות מלאה
    
    # קבל מידע על החשבון
    print("\n📊 Getting account information...")
    account_info = broker.get_account_summary()
    if account_info:
        net_liq = account_info.get('NetLiquidation', 'N/A')
        cash = account_info.get('TotalCashValue', 'N/A')
        day_pnl = account_info.get('DayPNL', 'N/A')
        
        print(f"💰 Current Balance: ${net_liq:,.2f}" if isinstance(net_liq, (int, float)) else f"💰 Current Balance: {net_liq}")
        print(f"� Cash: ${cash:,.2f}" if isinstance(cash, (int, float)) else f"💵 Cash: {cash}")
        print(f"�📈 Day PnL: ${day_pnl:,.2f}" if isinstance(day_pnl, (int, float)) else f"📈 Day PnL: {day_pnl}")
    
    # קבל רשימת פוזיציות
    print("\n📋 Getting current positions...")
    positions = broker.get_positions()
    
    if not positions:
        print("✅ No open positions found!")
        broker.disconnect()
        return True
    
    print(f"📊 Found {len(positions)} open positions:")
    total_value = 0
    
    for position in positions:
        symbol = position.get('symbol', 'Unknown')
        quantity = position.get('position', 0)
        market_price = position.get('market_price', 0)
        market_value = position.get('market_value', 0)
        unrealized_pnl = position.get('unrealized_pnl', 0)
        
        total_value += market_value
        
        color = Fore.GREEN if unrealized_pnl >= 0 else Fore.RED
        print(f"  {color}{symbol:6} | Qty: {quantity:8.0f} | Price: ${market_price:8.2f} | Value: ${market_value:10.2f} | PnL: ${unrealized_pnl:8.2f}")
    
    print(f"\n💰 Total Position Value: ${total_value:,.2f}")
    
    # שאל אישור לסגירה
    print(f"\n{Style.BRIGHT}🚨 WARNING: This will close ALL {len(positions)} positions!")
    response = input("Are you sure you want to close all positions? (yes/no): ").lower().strip()
    
    if response != 'yes':
        print("❌ Operation cancelled")
        broker.disconnect()
        return False
    
    # סגור את כל הפוזיציות
    print(f"\n🔄 Closing {len(positions)} positions...")
    closed_count = 0
    
    for i, position in enumerate(positions, 1):
        symbol = position.get('symbol', 'Unknown')
        quantity = position.get('position', 0)
        
        if quantity == 0:
            continue
            
        print(f"  [{i}/{len(positions)}] Closing {symbol} (Qty: {quantity})...")
        
        # צור הוראת סגירה
        if quantity > 0:  # Long position - sell to close
            order_result = broker.place_order(
                symbol=symbol,
                action="SELL",
                quantity=abs(quantity),
                order_type="MKT"
            )
        else:  # Short position - buy to close
            order_result = broker.place_order(
                symbol=symbol,
                action="BUY", 
                quantity=abs(quantity),
                order_type="MKT"
            )
        
        if order_result:
            print(f"    ✅ {symbol} closing order placed")
            closed_count += 1
        else:
            print(f"    ❌ Failed to close {symbol}: Order failed")
        
        time.sleep(1)  # המתן בין הוראות
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Successfully placed {closed_count} closing orders")
    print(f"❌ Failed to close {len(positions) - closed_count} positions")
    
    if closed_count > 0:
        print(f"\n⏳ Waiting for orders to execute...")
        time.sleep(5)
        
        # בדוק סטטוס מעודכן
        print("\n📊 Updated account status:")
        updated_account = broker.get_account_summary()
        if updated_account:
            net_liq = updated_account.get('NetLiquidation', 'N/A')
            cash = updated_account.get('TotalCashValue', 'N/A')
            day_pnl = updated_account.get('DayPNL', 'N/A')
            
            print(f"💰 Updated Balance: ${net_liq:,.2f}" if isinstance(net_liq, (int, float)) else f"💰 Updated Balance: {net_liq}")
            print(f"� Updated Cash: ${cash:,.2f}" if isinstance(cash, (int, float)) else f"💵 Updated Cash: {cash}")
            print(f"📈 Day PnL: ${day_pnl:,.2f}" if isinstance(day_pnl, (int, float)) else f"📈 Day PnL: {day_pnl}")
    
    broker.disconnect()
    print("\n🔚 Disconnected from TWS")
    return True

if __name__ == "__main__":
    print("🧹 Close All Positions Tool")
    print("=" * 50)
    close_all_positions()