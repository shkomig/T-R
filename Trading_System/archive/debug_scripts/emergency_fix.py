"""
EMERGENCY FIX: Market Data & Position Calculation
=================================================
תיקון חירום לנתוני שוק וחישובי פוזיציות
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from execution.broker_interface import IBBroker
from ibapi.contract import Contract
from colorama import Fore, Style, init
import pandas as pd

init(autoreset=True)

class FixedMarketData:
    def __init__(self):
        self.broker = None
        self.connected = False
    
    def connect(self):
        """התחבר ל-TWS עם הגדרות מתוקנות"""
        self.broker = IBBroker(port=7497, client_id=1007)
        self.connected = self.broker.connect()
        if self.connected:
            time.sleep(3)  # המתן לחיבור מלא
        return self.connected
    
    def get_real_price(self, symbol):
        """קבל מחיר אמיתי עדכני"""
        try:
            # נסה דרכים שונות לקבל מחיר
            
            # דרך 1: Real-time ticker
            if hasattr(self.broker, 'ib') and self.broker.ib:
                contract = Contract()
                contract.symbol = symbol
                contract.secType = "STK"
                contract.exchange = "SMART"
                contract.currency = "USD"
                
                # בקש נתונים בזמן אמת
                ticker = self.broker.ib.reqMktData(contract)
                time.sleep(2)  # המתן לנתונים
                
                if hasattr(ticker, 'last') and ticker.last and ticker.last > 0:
                    return float(ticker.last)
                elif hasattr(ticker, 'close') and ticker.close and ticker.close > 0:
                    return float(ticker.close)
            
            # דרך 2: נתונים היסטוריים
            hist_data = self.broker.get_historical_data(symbol, "1 D", "5 mins")
            if hist_data is not None and len(hist_data) > 0:
                if isinstance(hist_data, pd.DataFrame) and 'close' in hist_data.columns:
                    last_price = hist_data['close'].iloc[-1]
                    return float(last_price)
                elif isinstance(hist_data, list) and len(hist_data) > 0:
                    # אם זה רשימה, נסה לקבל את המחיר האחרון
                    last_bar = hist_data[-1]
                    if hasattr(last_bar, 'close'):
                        return float(last_bar.close)
            
            print(f"⚠️  Could not get real price for {symbol}")
            return None
            
        except Exception as e:
            print(f"❌ Error getting price for {symbol}: {e}")
            return None
    
    def fix_positions(self):
        """תקן את חישובי הפוזיציות"""
        if not self.connected:
            print("❌ Not connected to TWS")
            return
        
        print("🔧 FIXING POSITION CALCULATIONS")
        print("=" * 60)
        
        # קבל פוזיציות
        positions = self.broker.get_positions()
        
        if not positions:
            print("✅ No positions to fix")
            return
        
        print(f"🎯 Fixing {len(positions)} positions:\n")
        
        fixed_positions = []
        total_real_pnl = 0
        
        for i, position in enumerate(positions, 1):
            symbol = position.get('symbol', 'Unknown')
            quantity = position.get('position', 0)
            avg_cost = position.get('avg_cost', 0)
            
            if symbol == 'JPN':  # סמל בעייתי
                print(f"[{i}] {symbol}: Skipping invalid symbol")
                continue
            
            print(f"[{i}] {symbol}: Getting real price...")
            
            # קבל מחיר אמיתי
            real_price = self.get_real_price(symbol)
            
            if real_price is None or real_price <= 0:
                print(f"    ❌ Could not get real price")
                continue
            
            # חשב פרמטרים אמיתיים
            direction = "LONG" if quantity > 0 else "SHORT"
            market_value = real_price * quantity
            
            # חשב רווח/הפסד אמיתי
            if quantity > 0:  # Long position
                unrealized_pnl = (real_price - avg_cost) * quantity
            else:  # Short position
                unrealized_pnl = (avg_cost - real_price) * abs(quantity)
            
            pct_change = ((real_price - avg_cost) / avg_cost) * 100 if avg_cost > 0 else 0
            
            # צבע לפי רווחיות אמיתית
            if unrealized_pnl >= 0:
                color = Fore.GREEN
                status = "✅ PROFIT"
            else:
                color = Fore.RED
                status = "❌ LOSS"
            
            total_real_pnl += unrealized_pnl
            
            print(f"    {color}{direction} Position:")
            print(f"    Quantity: {quantity:8.0f}")
            print(f"    Entry: ${avg_cost:8.2f}")
            print(f"    Current: ${real_price:8.2f}")
            print(f"    Market Value: ${market_value:10.2f}")
            print(f"    Real P&L: ${unrealized_pnl:10.2f} ({pct_change:+6.2f}%)")
            print(f"    Status: {status}")
            print()
            
            fixed_positions.append({
                'symbol': symbol,
                'direction': direction,
                'quantity': quantity,
                'entry_price': avg_cost,
                'current_price': real_price,
                'market_value': market_value,
                'unrealized_pnl': unrealized_pnl,
                'pct_change': pct_change
            })
        
        # סיכום מתוקן
        print("=" * 60)
        print(f"🔧 FIXED SUMMARY:")
        print(f"Total Positions: {len(fixed_positions)}")
        
        winners = len([p for p in fixed_positions if p['unrealized_pnl'] >= 0])
        losers = len([p for p in fixed_positions if p['unrealized_pnl'] < 0])
        
        print(f"Winners: {Fore.GREEN}{winners}")
        print(f"Losers: {Fore.RED}{losers}")
        
        if total_real_pnl >= 0:
            print(f"REAL Total P&L: {Fore.GREEN}${total_real_pnl:,.2f}")
        else:
            print(f"REAL Total P&L: {Fore.RED}${total_real_pnl:,.2f}")
        
        # זיהוי בעיות אמיתיות
        print(f"\n🚨 REAL PROBLEMS:")
        big_losers = [p for p in fixed_positions if p['unrealized_pnl'] < -1000]
        if big_losers:
            print(f"❌ Positions with >$1,000 REAL loss:")
            for pos in big_losers:
                print(f"    {pos['symbol']} ({pos['direction']}): ${pos['unrealized_pnl']:,.2f}")
        else:
            print("✅ No major losing positions")
        
        return fixed_positions
    
    def disconnect(self):
        """התנתק"""
        if self.broker:
            self.broker.disconnect()

def main():
    """תקן את בעיות נתוני השוק"""
    print("🚨 EMERGENCY MARKET DATA FIX")
    print("=" * 70)
    
    fixer = FixedMarketData()
    
    if not fixer.connect():
        print("❌ Failed to connect to TWS")
        return
    
    print("✅ Connected successfully!")
    
    try:
        fixed_positions = fixer.fix_positions()
        
        if fixed_positions:
            print(f"\n💾 Would you like to save corrected position data? (The system had serious calculation errors)")
            
    except Exception as e:
        print(f"💥 Error during fix: {e}")
    finally:
        fixer.disconnect()
        print("\n🔚 Fix completed")

if __name__ == "__main__":
    main()