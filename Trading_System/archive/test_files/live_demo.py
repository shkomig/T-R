"""
Live Trading Demo with CLI Dashboard
=====================================
מסחר חי עם ממשק ויזואלי - גרסת הדגמה

משתמש ב:
- Historical Data (לא צריך Real-Time subscription)
- VWAP Strategy (המוצלחת ביותר)
- CLI Dashboard לתצוגה ויזואלית
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import time
import threading

sys.path.append(str(Path(__file__).parent))

from execution.live_engine import LiveTradingEngine
from strategies import VWAPStrategy
import yaml


class LiveTradingDemo:
    """Live Trading Demo with simulated real-time updates"""
    
    def __init__(self):
        self.engine = None
        self.running = False
        
        # Load config
        with open('config/trading_config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
    
    def run(self):
        """Run the demo"""
        print("="*70)
        print("     📊 LIVE TRADING DEMO - PAPER TRADING MODE")
        print("="*70)
        print()
        print("✓ Mode: Paper Trading (Safe)")
        print("✓ Strategy: VWAP (Win Rate: 42.86%, Return: +1.46%)")
        print("✓ Connection: IB Gateway Port 7497")
        print("✓ Data: Historical bars (no Real-Time subscription needed)")
        print()
        print("="*70)
        print()
        
        try:
            # Initialize engine
            print("🔌 Connecting to IB Gateway...")
            self.engine = LiveTradingEngine()
            
            if not self.engine.initialize():
                print("❌ Failed to connect to IB Gateway")
                print("   Make sure IB Gateway is running on Port 7497")
                return
            
            print("✅ Connected successfully!")
            print()
            
            # Show account info
            print("="*70)
            print("ACCOUNT INFORMATION")
            print("="*70)
            account_info = self.engine.get_account_info()
            for key, value in account_info.items():
                print(f"  {key}: {value}")
            print()
            
            # Show current positions
            print("="*70)
            print("CURRENT POSITIONS")
            print("="*70)
            positions = self.engine.get_positions()
            if positions:
                for pos in positions:
                    print(f"  {pos.symbol}: {pos.quantity} shares @ ${pos.avg_cost:.2f}")
            else:
                print("  No open positions")
            print()
            
            print("="*70)
            print("MONITORING MARKET - Historical Data Mode")
            print("="*70)
            print("📊 Fetching market data every 30 seconds...")
            print("⏸️  Press Ctrl+C to stop")
            print()
            
            self.running = True
            cycle = 0
            
            while self.running:
                cycle += 1
                print(f"\n{'─'*70}")
                print(f"Update Cycle #{cycle} - {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'─'*70}")
                
                # Fetch latest data for each symbol
                symbols = self.config['universe']['tickers']
                
                for symbol in symbols[:3]:  # First 3 symbols
                    print(f"\n📈 {symbol}:")
                    
                    # Get historical data
                    bars = self.engine.data_manager.get_historical_data(
                        symbol=symbol,
                        duration="1 D",
                        bar_size="30 mins"
                    )
                    
                    if bars is not None and len(bars) > 0:
                        latest = bars.iloc[-1]
                        
                        print(f"   Time:   {bars.index[-1]}")
                        print(f"   Open:   ${latest['open']:.2f}")
                        print(f"   High:   ${latest['high']:.2f}")
                        print(f"   Low:    ${latest['low']:.2f}")
                        print(f"   Close:  ${latest['close']:.2f}")
                        print(f"   Volume: {int(latest['volume']):,}")
                        
                        # Calculate VWAP
                        bars['vwap'] = (bars['volume'] * (bars['high'] + bars['low'] + bars['close']) / 3).cumsum() / bars['volume'].cumsum()
                        vwap = bars['vwap'].iloc[-1]
                        
                        deviation = ((latest['close'] - vwap) / vwap) * 100
                        
                        print(f"   VWAP:   ${vwap:.2f}")
                        print(f"   Dev:    {deviation:+.2f}%")
                        
                        # Signal
                        if deviation < -0.8:
                            print(f"   📊 SIGNAL: LONG (Price below VWAP)")
                        elif deviation > 0.8:
                            print(f"   📊 SIGNAL: EXIT (Price above VWAP)")
                        else:
                            print(f"   ⏸️  No signal")
                    else:
                        print(f"   ⚠️  No data available")
                
                # Show current equity
                print(f"\n{'─'*70}")
                account_info = self.engine.get_account_info()
                equity = account_info.get('NetLiquidation', 'N/A')
                print(f"💰 Current Equity: {equity}")
                print(f"{'─'*70}")
                
                # Wait 30 seconds
                print("\n⏱️  Next update in 30 seconds...")
                time.sleep(30)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.running = False
            if self.engine:
                print("\n🛑 Disconnecting...")
                self.engine.stop()
            print("✅ Demo completed\n")


if __name__ == "__main__":
    demo = LiveTradingDemo()
    demo.run()
