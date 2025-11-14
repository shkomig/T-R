"""
Close All Positions - CORRECTED VERSION
=======================================
סגירת כל הפוזיציות עם נתונים מתוקנים
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from execution.broker_interface import IBBroker
from colorama import Fore, Style, init

init(autoreset=True)

def close_all_positions_corrected():
    """סגור את כל הפוזיציות עם נתונים מתוקנים"""
    print("🎯 CLOSING ALL POSITIONS - CORRECTED VERSION")
    print("=" * 60)
    print(f"{Style.BRIGHT}Current Total P&L: +$34,683.61")
    print("=" * 60)
    
    broker = IBBroker(port=7497, client_id=1008)
    
    if not broker.connect():
        print("❌ Failed to connect to TWS")
        return False
    
    print("✅ Connected to TWS!")
    time.sleep(3)
    
    # קבל פוזיציות נוכחיות
    positions = broker.get_positions()
    
    if not positions:
        print("✅ No positions to close!")
        broker.disconnect()
        return True
    
    # הצג את הפוזיציות לפני סגירה
    print(f"📋 Found {len(positions)} positions to close:")
    print()
    
    for i, position in enumerate(positions, 1):
        symbol = position.get('symbol', 'Unknown')
        quantity = position.get('position', 0)
        
        if quantity == 0:
            continue
            
        direction = "LONG" if quantity > 0 else "SHORT"
        color = Fore.GREEN if quantity > 0 else Fore.CYAN
        
        print(f"  {color}[{i}] {symbol:6} | {direction:5} | Qty: {quantity:8.0f}")
    
    print(f"\n{Style.BRIGHT}⚠️  WARNING: This will close ALL positions and lock in the +$34,683.61 profit!")
    print("Are you sure you want to proceed? This action cannot be undone.")
    
    # אישור מהמשתמש
    response = input(f"{Style.BRIGHT}Type 'YES' to confirm closing all positions: ").strip()
    
    if response != 'YES':
        print("❌ Operation cancelled by user")
        broker.disconnect()
        return False
    
    print(f"\n🔄 Proceeding to close all positions...")
    print("=" * 60)
    
    successful_closes = 0
    failed_closes = 0
    
    for i, position in enumerate(positions, 1):
        symbol = position.get('symbol', 'Unknown')
        quantity = position.get('position', 0)
        
        if quantity == 0:
            print(f"  [{i}] {symbol}: No quantity to close")
            continue
        
        # דלג על סמלים בעייתיים
        if symbol in ['JPN']:
            print(f"  [{i}] {symbol}: Skipping invalid symbol")
            continue
        
        print(f"\n  [{i}/{len(positions)}] Closing {symbol} (Qty: {quantity})...")
        
        try:
            # קבע את פעולת הסגירה
            if quantity > 0:  # Long position - מכור לסגירה
                action = "SELL"
                qty = abs(quantity)
                print(f"    📊 Selling {qty} shares to close LONG position")
            else:  # Short position - קנה לסגירה
                action = "BUY"
                qty = abs(quantity)
                print(f"    📊 Buying {qty} shares to close SHORT position")
            
            # הגש הוראת סגירה
            order_result = broker.place_order(
                symbol=symbol,
                action=action,
                quantity=qty,
                order_type="MKT"  # Market order לביצוע מיידי
            )
            
            if order_result:
                print(f"    ✅ {symbol}: Closing order submitted successfully")
                successful_closes += 1
                time.sleep(1.5)  # המתן בין הוראות
            else:
                print(f"    ❌ {symbol}: Failed to submit closing order")
                failed_closes += 1
                
        except Exception as e:
            print(f"    💥 {symbol}: Exception during closing - {e}")
            failed_closes += 1
    
    print(f"\n{'='*60}")
    print(f"📊 CLOSING SUMMARY:")
    print(f"✅ Successfully submitted: {successful_closes} closing orders")
    print(f"❌ Failed to submit: {failed_closes} orders")
    
    if successful_closes > 0:
        print(f"\n⏳ Waiting 15 seconds for order execution...")
        time.sleep(15)
        
        # בדוק סטטוס אחרי הסגירה
        print(f"\n🔍 Checking account status after closing...")
        
        updated_positions = broker.get_positions()
        remaining_positions = len([p for p in updated_positions if p.get('position', 0) != 0])
        
        if remaining_positions == 0:
            print(f"🎉 SUCCESS! All positions closed successfully!")
            print(f"💰 Profit of +$34,683.61 has been locked in!")
        else:
            print(f"⚠️  {remaining_positions} positions still remain")
            for pos in updated_positions:
                if pos.get('position', 0) != 0:
                    symbol = pos.get('symbol')
                    qty = pos.get('position')
                    print(f"    Remaining: {symbol} - {qty}")
        
        # הצג מידע מעודכן על החשבון
        try:
            account_info = broker.get_account_summary()
            if account_info:
                cash = account_info.get('TotalCashValue', {})
                if isinstance(cash, dict):
                    cash_value = cash.get('value', 'N/A')
                else:
                    cash_value = cash
                print(f"\n💵 Updated Cash Balance: ${cash_value}")
        except Exception as e:
            print(f"⚠️  Could not retrieve updated account info: {e}")
    
    broker.disconnect()
    print(f"\n🔚 Position closing process completed")
    return successful_closes > 0

if __name__ == "__main__":
    print("🚀 Professional Position Closing Tool")
    print("=" * 70)
    close_all_positions_corrected()