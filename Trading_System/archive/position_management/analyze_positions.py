"""
Detailed Position Analysis
=========================
ניתוח מפורט של הפוזיציות והרווחיות
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from execution.broker_interface import IBBroker
from colorama import Fore, Style, init

init(autoreset=True)

def analyze_positions():
    """ניתוח מפורט של הפוזיציות"""
    print("🔍 DETAILED POSITION ANALYSIS")
    print("=" * 60)
    
    broker = IBBroker(port=7497, client_id=1005)
    
    if not broker.connect():
        print("❌ Failed to connect to TWS")
        return False
    
    print("✅ Connected to TWS!")
    time.sleep(3)
    
    # קבל פוזיציות מפורטות
    positions = broker.get_positions()
    
    if not positions:
        print("✅ No positions found!")
        broker.disconnect()
        return True
    
    print(f"📊 Found {len(positions)} positions:\n")
    
    total_pnl = 0
    winners = 0
    losers = 0
    
    for i, position in enumerate(positions, 1):
        symbol = position.get('symbol', 'Unknown')
        quantity = position.get('position', 0)
        avg_cost = position.get('avg_cost', 0)
        market_price = position.get('market_price', 0)
        market_value = position.get('market_value', 0)
        unrealized_pnl = position.get('unrealized_pnl', 0)
        
        # חשב אחוזי רווח/הפסד
        if avg_cost != 0:
            pct_change = ((market_price - avg_cost) / avg_cost) * 100
        else:
            pct_change = 0
        
        # זיהוי כיוון הפוזיציה
        direction = "LONG" if quantity > 0 else "SHORT"
        
        # צבע בהתאם לרווחיות
        if unrealized_pnl >= 0:
            color = Fore.GREEN
            status = "✅ PROFIT"
            winners += 1
        else:
            color = Fore.RED
            status = "❌ LOSS"
            losers += 1
        
        total_pnl += unrealized_pnl
        
        print(f"{color}[{i}] {symbol:6} ({direction})")
        print(f"    Quantity: {quantity:8.0f}")
        print(f"    Entry Price: ${avg_cost:8.2f}")
        print(f"    Current Price: ${market_price:8.2f}")
        print(f"    Market Value: ${market_value:10.2f}")
        print(f"    P&L: ${unrealized_pnl:10.2f} ({pct_change:+6.2f}%)")
        print(f"    Status: {status}")
        print()
    
    print("=" * 60)
    print(f"📊 SUMMARY:")
    print(f"Total Positions: {len(positions)}")
    print(f"Winners: {Fore.GREEN}{winners}")
    print(f"Losers: {Fore.RED}{losers}")
    
    if total_pnl >= 0:
        print(f"Total P&L: {Fore.GREEN}${total_pnl:,.2f}")
    else:
        print(f"Total P&L: {Fore.RED}${total_pnl:,.2f}")
    
    # זיהוי הבעיות העיקריות
    print(f"\n🔍 PROBLEM ANALYSIS:")
    
    big_losers = [pos for pos in positions if pos.get('unrealized_pnl', 0) < -1000]
    if big_losers:
        print(f"❌ Big Losers (>$1,000 loss):")
        for pos in big_losers:
            symbol = pos.get('symbol')
            loss = pos.get('unrealized_pnl')
            qty = pos.get('position')
            direction = "LONG" if qty > 0 else "SHORT"
            print(f"    {symbol} ({direction}): ${loss:,.2f}")
    
    big_winners = [pos for pos in positions if pos.get('unrealized_pnl', 0) > 10000]
    if big_winners:
        print(f"✅ Big Winners (>$10,000 profit):")
        for pos in big_winners:
            symbol = pos.get('symbol')
            profit = pos.get('unrealized_pnl')
            qty = pos.get('position')
            direction = "LONG" if qty > 0 else "SHORT"
            print(f"    {symbol} ({direction}): ${profit:,.2f}")
    
    broker.disconnect()
    return True

if __name__ == "__main__":
    analyze_positions()