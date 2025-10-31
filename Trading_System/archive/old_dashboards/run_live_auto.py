"""
Run Live Trading - Automatic Mode
==================================

Runs the trading system in fully automatic mode.
The system will:
1. Connect to IB Gateway
2. Monitor market in real-time
3. Generate signals from strategies
4. Execute trades automatically
5. Manage positions and risk

IMPORTANT:
- This is PAPER TRADING by default (safe)
- Real trading requires changing config
- Market must be open (9:30-16:00 EST)

Author: Trading System
Date: October 29, 2025
"""

import sys
import os
from datetime import datetime
import signal

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from execution.live_engine import LiveTradingEngine
from utils.logger import setup_logging


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n\n⚠️  Stopping trading system...")
    if 'engine' in globals() and engine:
        engine.stop()
    sys.exit(0)


def main():
    """Main function to run live trading."""
    print("="*70)
    print("     🚀 LIVE TRADING SYSTEM - AUTOMATIC MODE")
    print("="*70)
    print()
    print("📊 Mode: PAPER TRADING (Safe simulation)")
    print("📡 Connection: IB Gateway (Port 7497)")
    print("⏰ Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    print("⚠️  IMPORTANT:")
    print("   - Market must be open (9:30-16:00 EST)")
    print("   - System will run automatically")
    print("   - Press Ctrl+C to stop at any time")
    print()
    print("="*70)
    
    # Ask for confirmation
    confirm = input("\n🔴 Start automatic trading? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Cancelled.")
        return
    
    print("\n✅ Starting trading system...\n")
    
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Initialize engine
        global engine
        engine = LiveTradingEngine()
        
        # Initialize connection and components
        print("🔌 Connecting to IB Gateway...")
        if not engine.initialize():
            print("❌ Failed to initialize. Check that IB Gateway is running.")
            return
        
        print("✅ Connected successfully!\n")
        
        # Start the trading engine
        # This will run the main loop and start trading automatically
        print("🚀 Starting automatic trading...")
        print("📊 System will monitor market and execute trades")
        print("⏸️  Press Ctrl+C to stop\n")
        print("="*70)
        print()
        
        engine.start()  # This blocks and runs the main trading loop
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'engine' in globals() and engine:
            print("\n🛑 Stopping engine...")
            engine.stop()
        print("✅ System stopped.\n")


if __name__ == "__main__":
    main()
