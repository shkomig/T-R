"""
Start Live Trading System
==========================

Main entry point for starting the live trading system with timezone fix.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from execution.live_engine import LiveTradingEngine

def main():
    """Start the live trading system."""
    print("\n" + "="*70)
    print("STARTING LIVE TRADING SYSTEM")
    print("="*70)
    print()

    try:
        # Create trading engine
        engine = LiveTradingEngine()

        # Start the engine
        print("Initializing trading engine...")
        engine.start()

    except KeyboardInterrupt:
        print("\n\nSystem interrupted by user (Ctrl+C)")
        print("Shutting down gracefully...")

    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
