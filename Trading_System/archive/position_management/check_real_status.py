"""
Check Real Account Status
========================
בדיקת סטטוס אמיתי של החשבון ופוזיציות
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from execution.broker_interface import IBBroker
from colorama import Fore, Style, init

init(autoreset=True)

def check_real_status():
    """בדוק את הסטטוס האמיתי של החשבון"""
    print("🔍 Checking REAL account status...")
    broker = IBBroker(port=7497, client_id=1001)  # נשתמש ב-client ID אחר
    
    if not broker.connect():
        print("❌ Failed to connect to TWS")
        return False
    
    print("✅ Connected to TWS!")
    time.sleep(3)  # המתן להתחברות מלאה
    
    # קבל מידע אמיתי על החשבון
    print("\n📊 Getting REAL account information...")
    account_info = broker.get_account_summary()
    if account_info:
        print("💰 Account Summary:")
        for key, value in account_info.items():
            if isinstance(value, dict):
                val = value.get('value', value)
                curr = value.get('currency', '')
                print(f"  {key}: {val} {curr}")
            else:
                print(f"  {key}: {value}")
    
    # קבל רשימת פוזיציות אמיתית
    print("\n📋 Getting REAL positions...")
    positions = broker.get_positions()
    
    if not positions:
        print("✅ ✅ ✅ NO POSITIONS! Account is CLEAN!")
        broker.disconnect()
        return True
    
    print(f"⚠️  Found {len(positions)} REAL positions:")
    
    for i, position in enumerate(positions, 1):
        symbol = position.get('symbol', 'Unknown')
        quantity = position.get('position', 0)
        market_price = position.get('market_price', 0)
        market_value = position.get('market_value', 0)
        unrealized_pnl = position.get('unrealized_pnl', 0)
        
        color = Fore.GREEN if unrealized_pnl >= 0 else Fore.RED
        print(f"  {i}. {color}{symbol:6} | Qty: {quantity:8.0f} | Price: ${market_price:8.2f} | Value: ${market_value:10.2f} | PnL: ${unrealized_pnl:8.2f}")
    
    # בדוק הוראות פתוחות
    print("\n📝 Checking open orders...")
    try:
        orders = broker.get_open_orders()
        if orders:
            print(f"📋 Found {len(orders)} open orders:")
            for order in orders:
                print(f"  Order: {order}")
        else:
            print("✅ No open orders")
    except Exception as e:
        print(f"❌ Error getting orders: {e}")
    
    broker.disconnect()
    print("\n🔚 Disconnected from TWS")
    return len(positions) == 0

if __name__ == "__main__":
    print("🔍 Real Account Status Checker")
    print("=" * 50)
    is_clean = check_real_status()
    
    if is_clean:
        print("\n🎉 ACCOUNT IS CLEAN! No positions found.")
    else:
        print("\n⚠️  ACCOUNT HAS POSITIONS! May need manual closing.")