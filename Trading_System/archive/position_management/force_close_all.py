"""
Force Close All Positions - Version 2
=====================================
סגירה מאולצת של כל הפוזיציות עם בדיקות מתקדמות
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from execution.broker_interface import IBBroker
from colorama import Fore, Style, init

init(autoreset=True)

def force_close_all():
    """סגור בכוח את כל הפוזיציות"""
    print("🚨 FORCE CLOSING ALL POSITIONS")
    print("=" * 50)
    
    broker = IBBroker(port=7497, client_id=1002)  # client ID אחר שוב
    
    if not broker.connect():
        print("❌ Failed to connect to TWS")
        return False
    
    print("✅ Connected to TWS!")
    time.sleep(3)
    
    # קבל פוזיציות
    positions = broker.get_positions()
    
    if not positions:
        print("✅ No positions to close!")
        broker.disconnect()
        return True
    
    print(f"🎯 Found {len(positions)} positions to close:")
    
    successful_closes = 0
    
    for i, position in enumerate(positions, 1):
        symbol = position.get('symbol', 'Unknown')
        quantity = position.get('position', 0)
        
        if quantity == 0:
            print(f"  [{i}] {symbol}: No quantity to close")
            continue
        
        print(f"\n  [{i}/{len(positions)}] Closing {symbol} (Qty: {quantity})...")
        
        # בדוק אם הסמל תקין
        if symbol in ['JPN']:  # רשימת סמלים בעייתיים
            print(f"    ⚠️  Skipping {symbol} - Invalid symbol")
            continue
        
        try:
            # צור הוראה בהתאם לכיוון הפוזיציה
            if quantity > 0:  # Long position
                action = "SELL"
                qty = abs(quantity)
            else:  # Short position  
                action = "BUY"
                qty = abs(quantity)
            
            print(f"    📋 Creating {action} order for {qty} shares...")
            
            # הגש הוראה
            order_result = broker.place_order(
                symbol=symbol,
                action=action,
                quantity=qty,
                order_type="MKT"  # Market order למהירות
            )
            
            if order_result:
                print(f"    ✅ {symbol}: Order submitted successfully")
                successful_closes += 1
                
                # המתן קצת לביצוע
                time.sleep(2)
                
            else:
                print(f"    ❌ {symbol}: Order failed")
                
        except Exception as e:
            print(f"    💥 {symbol}: Exception - {e}")
    
    print(f"\n📊 CLOSING SUMMARY:")
    print(f"✅ Successfully submitted {successful_closes} closing orders")
    print(f"❌ Failed to close {len(positions) - successful_closes} positions")
    
    if successful_closes > 0:
        print(f"\n⏳ Waiting 10 seconds for execution...")
        time.sleep(10)
        
        # בדוק מצב לאחר הסגירה
        print("\n🔍 Checking positions after closing...")
        updated_positions = broker.get_positions()
        
        if not updated_positions:
            print("🎉 SUCCESS! All positions closed!")
        else:
            print(f"⚠️  Still have {len(updated_positions)} positions:")
            for pos in updated_positions:
                symbol = pos.get('symbol', 'Unknown')
                qty = pos.get('position', 0)
                print(f"  - {symbol}: {qty}")
    
    broker.disconnect()
    return True

if __name__ == "__main__":
    force_close_all()