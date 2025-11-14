"""
Check Orders Status
==================
בדיקת סטטוס ההוראות ב-TWS
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from execution.broker_interface import IBBroker

def check_orders():
    """בדוק סטטוס ההוראות"""
    print("🔍 Checking orders status...")
    
    broker = IBBroker(port=7497, client_id=1003)
    
    if not broker.connect():
        print("❌ Failed to connect")
        return
    
    print("✅ Connected!")
    time.sleep(3)
    
    try:
        # בדוק הוראות פתוחות
        print("\n📋 Checking open orders...")
        orders = broker.get_open_orders()
        
        if orders:
            print(f"Found {len(orders)} open orders:")
            for order in orders:
                print(f"  Order: {order}")
        else:
            print("No open orders found")
        
        # בדוק פוזיציות נוכחיות
        print("\n📊 Current positions:")
        positions = broker.get_positions()
        
        if positions:
            print(f"Found {len(positions)} positions:")
            for pos in positions:
                symbol = pos.get('symbol')
                qty = pos.get('position')
                print(f"  {symbol}: {qty}")
        else:
            print("No positions!")
            
    except Exception as e:
        print(f"Error: {e}")
    
    broker.disconnect()

if __name__ == "__main__":
    check_orders()