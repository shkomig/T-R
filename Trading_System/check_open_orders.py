#!/usr/bin/env python3
"""
בדיקת פקודות פתוחות ב-TWS
============================

סקריפט לבדיקה ולביטול פקודות פתוחות לטיפול בשגיאת 201.
"""

import sys
import logging
from execution.broker_interface import IBBroker

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """בדיקת פקודות פתוחות"""
    
    # התחברות לברוקר
    broker = IBBroker(host="127.0.0.1", port=7497, client_id=1002)
    
    try:
        print("🔌 מתחבר ל-TWS...")
        if not broker.connect():
            print("❌ שגיאה בהתחברות")
            return
        
        print("✅ התחברות הצליחה")
        
        # קבלת פקודות פתוחות
        print("\n📋 בודק פקודות פתוחות...")
        open_orders = broker.get_open_orders()
        
        if not open_orders:
            print("✅ אין פקודות פתוחות")
        else:
            print(f"⚠️  נמצאו {len(open_orders)} פקודות פתוחות:")
            
            symbol_counts = {}
            for i, trade in enumerate(open_orders, 1):
                symbol = trade.contract.symbol if hasattr(trade, 'contract') else 'Unknown'
                status = trade.orderStatus.status if hasattr(trade, 'orderStatus') else 'Unknown'
                order_id = trade.order.orderId if hasattr(trade, 'order') else 'Unknown'
                action = trade.order.action if hasattr(trade, 'order') else 'Unknown'
                quantity = trade.order.totalQuantity if hasattr(trade, 'order') else 'Unknown'
                
                print(f"  {i:2d}. {symbol:6s} | {action:4s} | Qty: {quantity:6} | Status: {status:12s} | ID: {order_id}")
                
                # ספירה לפי סמל
                if symbol in symbol_counts:
                    symbol_counts[symbol] += 1
                else:
                    symbol_counts[symbol] = 1
            
            print(f"\n📊 סיכום לפי סמל:")
            for symbol, count in symbol_counts.items():
                if count >= 10:  # סמלים עם הרבה פקודות
                    print(f"  🚨 {symbol}: {count} פקודות (קרוב למגבלה של 15)")
                else:
                    print(f"  📈 {symbol}: {count} פקודות")
            
            # שאלה אם לבטל פקודות
            print(f"\n❓ האם לבטל פקודות?")
            print(f"1. בטל פקודות לסמל מסוים")
            print(f"2. בטל את כל הפקודות (חירום)")
            print(f"3. יציאה בלי ביטול")
            
            choice = input("בחר אפשרות (1-3): ").strip()
            
            if choice == "1":
                symbol = input("הכנס סמל לביטול פקודותיו: ").strip().upper()
                if symbol:
                    print(f"🧹 מבטל פקודות עבור {symbol}...")
                    cancelled = broker.cancel_open_orders_for_symbol(symbol)
                    print(f"✅ בוטלו {cancelled} פקודות עבור {symbol}")
                    
            elif choice == "2":
                confirm = input("⚠️  האם אתה בטוח שברצונך לבטל את כל הפקודות? (yes/no): ").strip().lower()
                if confirm == "yes":
                    print(f"🚨 מבטל את כל הפקודות...")
                    cancelled = broker.cancel_all_open_orders()
                    print(f"✅ בוטלו {cancelled} פקודות")
                else:
                    print("ביטול בוטל.")
            
            else:
                print("יוצא בלי ביטול.")
    
    except Exception as e:
        print(f"❌ שגיאה: {e}")
    
    finally:
        broker.disconnect()
        print("🔌 התנתק מהברוקר")

if __name__ == "__main__":
    main()