#!/usr/bin/env python3
"""
ניקוי חכם - מחיקת הזמנות ישנות וסגירה חסכונית
Smart cleanup - cancel old orders and close economically
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from execution.broker_interface import IBBroker

def main():
    print("🧹 Smart Cleanup & Close")
    print("=" * 40)
    
    # התחבר לברוקר
    print("📡 מתחבר ל-TWS...")
    broker = IBBroker()
    
    try:
        # התחבר
        if not broker.connect():
            print("❌ שגיאה בהתחברות לברוקר")
            return
            
        print("✅ התחברות הצליחה")
        time.sleep(2)
        
        # STEP 1: מחק את כל ההזמנות הפתוחות
        print("\n🗑️  STEP 1: מחיקת כל ההזמנות הפתוחות")
        print("-" * 45)
        
        try:
            # בקש מ-IB לבטל את כל ההזמנות
            broker.ib.reqGlobalCancel()
            print("✅ בקשת ביטול כללי נשלחה")
            time.sleep(5)  # המתן שהביטולים יתבצעו
            
        except Exception as e:
            print(f"⚠️  שגיאה בביטול כללי: {e}")
        
        # STEP 2: בדוק איך נראה המצב עכשיו
        print("\n📊 STEP 2: בדיקת המצב הנוכחי")
        print("-" * 35)
        
        positions = broker.get_positions()
        account_summary = broker.get_account_summary()
        
        available_funds = 0
        for key, data in account_summary.items():
            if key == "AvailableFunds" and data.get('currency') == 'USD':
                available_funds = float(data.get('value', 0))
                break
        
        print(f"💰 זמין למסחר: ${available_funds:,.2f}")
        print(f"📊 פוזיציות פתוחות: {len(positions)}")
        
        if not positions:
            print("🎉 החשבון נקי!")
            return
        
        # STEP 3: סגירה חסכונית - רק מה שמחוסר במרגין
        print(f"\n🎯 STEP 3: סגירה חסכונית")
        print("-" * 30)
        
        # התמקד במניות הגדולות שגוזלות הכי הרבה מרגין
        big_positions = []
        small_positions = []
        
        for pos in positions:
            symbol = pos['symbol']
            quantity = pos['position']
            value = abs(pos.get('market_value', 0))
            
            # דלג על סמלים בעייתיים
            if symbol in ['JPN']:
                print(f"⚠️  דולג על {symbol} - סמל בעייתי")
                continue
                
            if value > 100000:  # פוזיציות גדולות מ-100k
                big_positions.append((symbol, quantity, value))
            else:
                small_positions.append((symbol, quantity, value))
        
        print(f"\n🔴 פוזיציות גדולות ({len(big_positions)}):")
        for symbol, qty, value in big_positions:
            print(f"  {symbol}: {qty} יחידות = ${value:,.0f}")
            
        print(f"\n🟡 פוזיציות קטנות ({len(small_positions)}):")
        for symbol, qty, value in small_positions:
            print(f"  {symbol}: {qty} יחידות = ${value:,.0f}")
        
        # התמקד בסגירת הפוזיציות הגדולות תחילה
        print(f"\n📤 מתחיל סגירה מהפוזיציות הגדולות:")
        
        for symbol, quantity, value in big_positions:
            print(f"\n🔧 מטפל ב-{symbol} ({quantity} יחידות, ${value:,.0f}):")
            
            if quantity == 0:
                print("  ✅ כבר סגור")
                continue
            
            # סגור בחלקים קטנים (50 יחידות בכל פעם)
            close_action = "SELL" if quantity > 0 else "BUY"
            remaining = abs(quantity)
            chunk_size = min(50, remaining)  # חלקים קטנים
            
            try:
                print(f"  📤 סוגר {chunk_size} מ-{remaining} ({close_action})...")
                order_id = broker.place_order(
                    symbol=symbol,
                    action=close_action,
                    quantity=chunk_size,
                    order_type="MKT"
                )
                
                if order_id:
                    print(f"  ✅ הזמנה נשלחה: {order_id}")
                else:
                    print(f"  ❌ שגיאה בשליחת הזמנה")
                    
            except Exception as e:
                print(f"  ❌ שגיאה: {e}")
            
            time.sleep(2)  # המתן בין הזמנות
        
        print(f"\n⏳ ממתין שההזמנות יתמלאו...")
        time.sleep(10)
        
        # בדוק מה השתנה
        new_positions = broker.get_positions()
        print(f"\n📊 תוצאות: נותרו {len(new_positions)} פוזיציות")
        
        for pos in new_positions:
            symbol = pos['symbol']
            qty = pos['position'] 
            if symbol != 'JPN':  # דלג על הבעייתי
                print(f"  {symbol}: {qty} יחידות")
        
        print(f"\n💡 המלצה: אם עדיין יש פוזיציות, סגור אותן ידנית ב-TWS")
        print("   Trade → Portfolio → Right-click → Close Position")
        
    except Exception as e:
        print(f"❌ שגיאה כללית: {e}")
        
    finally:
        print("\n🔌 מתנתק...")
        broker.disconnect()

if __name__ == "__main__":
    main()