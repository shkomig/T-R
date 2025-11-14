"""
Market Data Test
===============
בדיקה של נתוני שוק מ-TWS
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from execution.broker_interface import IBBroker

def test_market_data():
    """בדוק קבלת נתוני שוק"""
    print("🔍 Testing Market Data Connection...")
    
    broker = IBBroker(port=7497, client_id=1006)
    
    if not broker.connect():
        print("❌ Failed to connect")
        return
    
    print("✅ Connected!")
    time.sleep(3)
    
    # נסה לקבל מחיר עדכני של מניה פשוטה
    test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}...")
        try:
            # נסה לקבל נתונים היסטוריים
            hist_data = broker.get_historical_data(symbol, "1 D", "1 min")
            if hist_data and len(hist_data) > 0:
                last_price = hist_data['close'].iloc[-1]
                print(f"  ✅ {symbol}: Last price ${last_price:.2f}")
            else:
                print(f"  ❌ {symbol}: No historical data")
                
        except Exception as e:
            print(f"  💥 {symbol}: Error - {e}")
    
    broker.disconnect()
    print("\n🔚 Test completed")

if __name__ == "__main__":
    test_market_data()