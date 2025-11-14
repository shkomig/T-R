#!/usr/bin/env python3
"""
סגירת כל הפוזיציות ושורט על הכל
Force close all positions and then short everything
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from execution.broker_interface import IBBroker

def main():
    print("🔴 Force Close All Positions & Go Short")
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
        else:
            print(f"📊 נמצאו {len(positions)} פוזיציות:")
            
            symbols_to_short = []
            
            # סגור כל פוזיציה קיימת
            for i, position in enumerate(positions, 1):
                symbol = position['symbol']
                quantity = position['position']
                
                print(f"\n{i}. {symbol}: {quantity} יחידות")
                
                if quantity != 0:
                    # סגור את הפוזיציה
                    close_action = "SELL" if quantity > 0 else "BUY"
                    close_qty = abs(quantity)
                    
                    print(f"   🔄 סוגר פוזיציה: {close_action} {close_qty}")
                    
                    try:
                        order_id = broker.place_order(
                            symbol=symbol,
                            action=close_action,
                            quantity=close_qty,
                            order_type="MKT"
                        )
                        
                        if order_id:
                            print(f"   ✅ הזמנת סגירה נשלחה: {order_id}")
                            symbols_to_short.append(symbol)
                        else:
                            print(f"   ❌ שגיאה בשליחת הזמנת סגירה")
                            
                    except Exception as e:
                        print(f"   ❌ שגיאה: {e}")
                        # עדיין נוסיף לרשימת השורט
                        symbols_to_short.append(symbol)
            
            # חכה קצת שההזמנות יתמלאו
            print(f"\n⏳ ממתין 10 שניות שההזמנות יתמלאו...")
            time.sleep(10)
            
            # עכשיו שים שורט על הכל
            print(f"\n🔻 משים שורט על {len(symbols_to_short)} מניות:")
            
            for symbol in symbols_to_short:
                print(f"\n🔻 שורט על {symbol}...")
                
                try:
                    # שורט 100 יחידות מכל מניה (או כמות אחרת שתרצה)
                    short_qty = 100
                    
                    order_id = broker.place_order(
                        symbol=symbol,
                        action="SELL",  # שורט = מכירה
                        quantity=short_qty,
                        order_type="MKT"
                    )
                    
                    if order_id:
                        print(f"   ✅ שורט נשלח: {symbol} x{short_qty} = {order_id}")
                    else:
                        print(f"   ❌ שגיאה בשליחת שורט")
                        
                except Exception as e:
                    print(f"   ❌ שגיאה בשורט: {e}")
                    
                # חכה קצת בין הזמנות
                time.sleep(1)
        
        print(f"\n🎯 סיום! בדוק את הפוזיציות ב-TWS")
        
    except Exception as e:
        print(f"❌ שגיאה כללית: {e}")
        
    finally:
        print("\n🔌 מתנתק...")
        broker.disconnect()

if __name__ == "__main__":
    # אזהרת בטיחות
    print("⚠️  אזהרה: סקריפט זה יסגור את כל הפוזיציות וישים שורט!")
    print("⚠️  וודא שזה חשבון נייר (Paper Trading)!")
    
    response = input("\nהאם להמשיך? (כן/לא): ").strip().lower()
    if response in ['כן', 'yes', 'y', 'כ']:
        main()
    else:
        print("מבוטל.")