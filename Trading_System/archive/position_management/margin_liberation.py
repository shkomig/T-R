#!/usr/bin/env python3
"""
סגירת השורטים הגדולים - פינוי מרגין לעבודה רגילה
Close big shorts - free up margin for normal trading
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from execution.broker_interface import IBBroker

def main():
    print("💰 Margin Liberation - סגירת השורטים הגדולים")
    print("=" * 55)
    
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
        
        # בדוק מצב נוכחי
        print("\n📊 בדיקת המצב הנוכחי...")
        positions = broker.get_positions()
        account_summary = broker.get_account_summary()
        
        available_funds = 0
        for key, data in account_summary.items():
            if key == "AvailableFunds" and data.get('currency') == 'USD':
                available_funds = float(data.get('value', 0))
                break
        
        print(f"💰 זמין כרגע: ${available_funds:,.2f}")
        
        # מצא את השורטים הגדולים
        big_shorts = []
        for pos in positions:
            symbol = pos['symbol']
            quantity = pos['position']
            value = abs(pos.get('market_value', 0))
            
            # רק שורטים גדולים
            if quantity < 0 and value > 200000:  # שורטים מעל 200k
                big_shorts.append((symbol, quantity, value))
        
        print(f"\n🔴 שורטים גדולים שצריך לסגור:")
        for symbol, qty, value in big_shorts:
            print(f"  {symbol}: {qty} יחידות = ${value:,.0f}")
        
        if not big_shorts:
            print("✅ אין שורטים גדולים לסגור!")
            return
        
        print(f"\n🎯 מתחיל סגירה חכמה (חלקים של 100 יחידות):")
        
        for symbol, quantity, value in big_shorts:
            print(f"\n🔧 מטפל ב-{symbol}:")
            print(f"   📊 נוכחי: {quantity} יחידות (${value:,.0f})")
            
            # סגור בחלקים של 100 יחידות
            remaining = abs(quantity)
            chunk_size = min(100, remaining)
            
            try:
                print(f"   📤 קונה {chunk_size} יחידות לסגירה חלקית...")
                order_id = broker.place_order(
                    symbol=symbol,
                    action="BUY",  # קנייה לסגירת שורט
                    quantity=chunk_size,
                    order_type="MKT"
                )
                
                if order_id:
                    print(f"   ✅ הזמנת סגירה נשלחה: {order_id}")
                    print(f"   📈 זה יפחית את הפוזיציה מ-{quantity} ל-{quantity + chunk_size}")
                else:
                    print(f"   ❌ שגיאה בשליחת הזמנה")
                    
            except Exception as e:
                print(f"   ❌ שגיאה: {e}")
            
            time.sleep(3)  # המתן בין הזמנות
        
        print(f"\n⏳ ממתין 15 שניות שההזמנות יתמלאו...")
        time.sleep(15)
        
        # בדוק שיפור במרגין
        print(f"\n📊 בדיקת שיפור במרגין...")
        new_account = broker.get_account_summary()
        new_available = 0
        for key, data in new_account.items():
            if key == "AvailableFunds" and data.get('currency') == 'USD':
                new_available = float(data.get('value', 0))
                break
        
        improvement = new_available - available_funds
        print(f"💰 זמין עכשיו: ${new_available:,.2f}")
        print(f"📈 שיפור: ${improvement:,.2f}")
        
        if improvement > 5000:
            print("🎉 שיפור משמעותי במרגין! אפשר להמשיך לעבודה רגילה")
        else:
            print("⚠️  שיפור קטן - אולי צריך לסגור עוד")
        
        # הצג פוזיציות נותרות
        new_positions = broker.get_positions()
        print(f"\n📋 פוזיציות נותרות ({len(new_positions)}):")
        for pos in new_positions:
            symbol = pos['symbol']
            qty = pos['position']
            value = pos.get('market_value', 0)
            if abs(value) > 1000:  # רק פוזיציות משמעותיות
                direction = "📈 לונג" if qty > 0 else "📉 שורט"
                print(f"  {symbol}: {qty} יחידות {direction} (${value:,.0f})")
        
        print(f"\n🚀 המערכת מוכנה לעבודה רגילה!")
        
    except Exception as e:
        print(f"❌ שגיאה כללית: {e}")
        
    finally:
        print("\n🔌 מתנתק...")
        broker.disconnect()

if __name__ == "__main__":
    main()