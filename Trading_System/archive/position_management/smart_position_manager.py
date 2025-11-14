#!/usr/bin/env python3
"""
פתרון בעיות המרגין - סגירה מחדש עם פרמטרים מותאמים
Fix margin issues - smart close with adjusted parameters
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from execution.broker_interface import IBBroker

def main():
    print("🔧 Smart Position Manager - Fix Margin Issues")
    print("=" * 60)
    
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
        
        # בדוק פוזיציות נוכחיות
        print("\n📊 בודק פוזיציות נוכחיות...")
        positions = broker.get_positions()
        
        if not positions:
            print("✅ אין פוזיציות פתוחות - החשבון נקי!")
            return
            
        print(f"📊 נמצאו {len(positions)} פוזיציות:")
        
        # קודם נסגור את כל הפוזיציות הקיימות בזהירות
        print("\n🎯 STEP 1: סגירת פוזיציות קיימות")
        print("-" * 40)
        
        valid_positions = []
        for i, position in enumerate(positions, 1):
            symbol = position['symbol']
            quantity = position['position']
            
            print(f"{i}. {symbol}: {quantity} יחידות")
            
            # דלג על סמלים בעייתיים
            if symbol in ['JPN']:  # סמלים שלא מוכרים
                print(f"   ⚠️  דולג על {symbol} - סמל לא מוכר")
                continue
                
            if quantity == 0:
                print(f"   ✅ {symbol} - כבר סגור")
                continue
                
            valid_positions.append((symbol, quantity))
        
        # סגור פוזיציות תקינות
        for symbol, quantity in valid_positions:
            print(f"\n🔄 מטפל ב-{symbol} ({quantity} יחידות):")
            
            # אם זה פוזיציה גדולה - חלק לחלקים קטנים
            if abs(quantity) > 1000:
                print(f"   ⚠️  פוזיציה גדולה - מחלק לחלקים של 100 יחידות")
                
                # חלק לחלקים של 100
                remaining = abs(quantity)
                close_action = "SELL" if quantity > 0 else "BUY"
                
                while remaining > 0:
                    chunk_size = min(100, remaining)
                    
                    try:
                        print(f"   📤 סוגר {chunk_size} יחידות מ-{symbol}...")
                        order_id = broker.place_order(
                            symbol=symbol,
                            action=close_action,
                            quantity=chunk_size,
                            order_type="MKT"
                        )
                        
                        if order_id:
                            print(f"   ✅ הזמנה נשלחה: {order_id}")
                            remaining -= chunk_size
                            time.sleep(2)  # המתן בין הזמנות
                        else:
                            print(f"   ❌ שגיאה בשליחת הזמנה")
                            break
                            
                    except Exception as e:
                        print(f"   ❌ שגיאה: {e}")
                        break
                        
            else:
                # פוזיציה רגילה - סגור בבת אחת
                close_action = "SELL" if quantity > 0 else "BUY"
                close_qty = abs(quantity)
                
                try:
                    print(f"   📤 סוגר {close_action} {close_qty}...")
                    order_id = broker.place_order(
                        symbol=symbol,
                        action=close_action,
                        quantity=close_qty,
                        order_type="MKT"
                    )
                    
                    if order_id:
                        print(f"   ✅ הזמנת סגירה נשלחה: {order_id}")
                    else:
                        print(f"   ❌ שגיאה בשליחת הזמנת סגירה")
                        
                except Exception as e:
                    print(f"   ❌ שגיאה: {e}")
        
        # חכה שההזמנות יתבצעו
        print(f"\n⏳ ממתין 15 שניות שההזמנות יתמלאו...")
        time.sleep(15)
        
        # בדוק מה נותר
        print("\n📊 בודק מצב לאחר סגירות...")
        new_positions = broker.get_positions()
        
        if not new_positions:
            print("🎉 מעולה! כל הפוזיציות נסגרו!")
        else:
            print(f"⚠️  עדיין נותרו {len(new_positions)} פוזיציות:")
            for pos in new_positions:
                print(f"   - {pos['symbol']}: {pos['position']} יחידות")
                
        # עכשיו שים שורטים קטנים (רק אם החשבון נקי יחסית)
        if len(new_positions) <= 2:  # רק אם נותרו מעט פוזיציות
            print(f"\n🔻 STEP 2: שורטים קטנים (10 יחידות כל אחד)")
            print("-" * 40)
            
            # רשימת מניות בטוחות לשורט
            safe_symbols = ['SPY', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NFLX']
            
            for symbol in safe_symbols:
                print(f"\n🔻 שורט קטן על {symbol} (10 יחידות)...")
                
                try:
                    order_id = broker.place_order(
                        symbol=symbol,
                        action="SELL",  # שורט
                        quantity=10,    # כמות קטנה
                        order_type="MKT"
                    )
                    
                    if order_id:
                        print(f"   ✅ שורט נשלח: {symbol} x10 = {order_id}")
                    else:
                        print(f"   ❌ שגיאה בשליחת שורט")
                        
                except Exception as e:
                    print(f"   ❌ שגיאה בשורט: {e}")
                    
                time.sleep(1)  # המתן בין שורטים
        else:
            print(f"\n⚠️  יותר מדי פוזיציות פתוחות - מדלג על שורטים")
            print("   קודם צריך לסגור את כל הפוזיציות הקיימות")
        
        print(f"\n🎯 סיום! בדוק את התוצאות ב-TWS")
        
    except Exception as e:
        print(f"❌ שגיאה כללית: {e}")
        
    finally:
        print("\n🔌 מתנתק...")
        broker.disconnect()

if __name__ == "__main__":
    main()