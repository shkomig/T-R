#!/usr/bin/env python3
"""
איזון פוזיציות - שורט באותה כמות כדי לאפס פוזיציות
Balance positions - short same amount to zero out positions
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from execution.broker_interface import IBBroker

def main():
    print("⚖️  Position Balancer - שורט לאיזון פוזיציות")
    print("=" * 50)
    
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
            print("✅ אין פוזיציות פתוחות")
            return
            
        print(f"📊 נמצאו {len(positions)} פוזיציות:")
        print("\n🎯 אסטרטגיה: שורט באותה כמות לאיזון = פוזיציה 0")
        print("-" * 50)
        
        for i, position in enumerate(positions, 1):
            symbol = position['symbol']
            quantity = position['position']
            
            print(f"\n{i}. {symbol}: {quantity} יחידות נוכחיות")
            
            # דלג על סמלים בעייתיים
            if symbol in ['JPN']:  # סמלים שלא מוכרים ב-IB
                print(f"   ⚠️  דולג על {symbol} - סמל לא מוכר ב-IB")
                continue
                
            if quantity == 0:
                print(f"   ✅ {symbol} - כבר מאוזן")
                continue
                
            # חשב איך לאזן
            if quantity > 0:
                # פוזיציה לונג - נשים שורט באותה כמות
                action = "SELL"
                balance_qty = quantity
                print(f"   📋 תוכנית: שורט {balance_qty} יחידות כדי לאזן ל-0")
            else:
                # פוזיציה שורט - נקנה כדי לאזן
                action = "BUY" 
                balance_qty = abs(quantity)
                print(f"   📋 תוכנית: קנה {balance_qty} יחידות כדי לאזן ל-0")
            
            # אם זה כמות גדולה - חלק לחלקים
            if balance_qty > 1000:
                print(f"   ⚠️  כמות גדולה - מחלק לחלקים של 500 יחידות")
                
                remaining = balance_qty
                while remaining > 0:
                    chunk_size = min(500, remaining)
                    
                    try:
                        print(f"   📤 מאזן {chunk_size} יחידות מ-{symbol} ({action})...")
                        order_id = broker.place_order(
                            symbol=symbol,
                            action=action,
                            quantity=chunk_size,
                            order_type="MKT"
                        )
                        
                        if order_id:
                            print(f"   ✅ הזמנת איזון נשלחה: {order_id}")
                            remaining -= chunk_size
                            time.sleep(3)  # המתן יותר בין הזמנות גדולות
                        else:
                            print(f"   ❌ שגיאה בשליחת הזמנה")
                            break
                            
                    except Exception as e:
                        print(f"   ❌ שגיאה: {e}")
                        break
                        
            else:
                # כמות רגילה - אזן בבת אחת
                try:
                    print(f"   📤 מאזן {action} {balance_qty}...")
                    order_id = broker.place_order(
                        symbol=symbol,
                        action=action,
                        quantity=balance_qty,
                        order_type="MKT"
                    )
                    
                    if order_id:
                        print(f"   ✅ הזמנת איזון נשלחה: {order_id}")
                    else:
                        print(f"   ❌ שגיאה בשליחת הזמנת איזון")
                        
                except Exception as e:
                    print(f"   ❌ שגיאה: {e}")
        
        # חכה שההזמנות יתבצעו
        print(f"\n⏳ ממתין 20 שניות שההזמנות יתמלאו...")
        time.sleep(20)
        
        # בדוק תוצאות
        print(f"\n📊 בודק תוצאות האיזון...")
        new_positions = broker.get_positions()
        
        if not new_positions:
            print("🎉 מושלם! כל הפוזיציות מאוזנות - החשבון נקי!")
        else:
            print(f"📊 נותרו {len(new_positions)} פוזיציות לאחר איזון:")
            for pos in new_positions:
                qty = pos['position']
                symbol = pos['symbol']
                if abs(qty) < 1:  # כמעט אפס
                    status = "✅ כמעט מאוזן"
                elif abs(qty) < abs(positions[0]['position']) * 0.1:  # 10% מהכמות המקורית
                    status = "🔶 חלקי"
                else:
                    status = "🔴 לא מאוזן"
                    
                print(f"   {status} {symbol}: {qty} יחידות")
        
        print(f"\n🎯 סיום איזון! בדוק את התוצאות ב-TWS")
        
    except Exception as e:
        print(f"❌ שגיאה כללית: {e}")
        
    finally:
        print("\n🔌 מתנתק...")
        broker.disconnect()

if __name__ == "__main__":
    print("⚠️  הסקריפט יאזן פוזיציות על ידי שורט/קנייה באותה כמות")
    print("⚠️  מטרה: להגיע לפוזיציות 0 בכל המניות")
    
    response = input("\nהאם להמשיך? (כן/לא): ").strip().lower()
    if response in ['כן', 'yes', 'y', 'כ']:
        main()
    else:
        print("מבוטל.")