"""
Test Live Trading Engine in Paper Trading Mode

This script tests the live trading engine with paper trading.
It will connect to IB Gateway (port 7497) and run for a limited time.

Usage:
    python test_live_trading.py

Requirements:
    - IB Gateway or TWS running on port 7497 (Paper Trading)
    - All strategies configured
    - Risk management settings configured

Author: Trading System
Date: October 29, 2025
"""

import sys
import time
from datetime import datetime
from execution.live_engine import LiveTradingEngine


def main():
    """
    Test the live trading engine.
    """
    print("="*60)
    print("LIVE TRADING ENGINE TEST")
    print("="*60)
    print(f"Start Time: {datetime.now()}")
    print(f"Mode: PAPER TRADING")
    print("\nIMPORTANT:")
    print("- Ensure IB Gateway is running on port 7497")
    print("- This is PAPER TRADING mode only")
    print("- Press Ctrl+C to stop at any time")
    print("="*60)
    
    # Confirm user wants to proceed
    response = input("\nProceed with test? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Test cancelled.")
        return
    
    print("\nInitializing trading engine...")
    
    try:
        # Create engine
        engine = LiveTradingEngine()
        
        # Start engine (runs until interrupted)
        print("\nStarting live trading engine...")
        print("Press Ctrl+C to stop\n")
        
        engine.start()
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60)
    print(f"End Time: {datetime.now()}")
    print("\nCheck logs/ directory for detailed logs")


def quick_test():
    """
    Quick test - just initialize and check connections.
    """
    print("="*60)
    print("QUICK CONNECTION TEST")
    print("="*60)
    
    try:
        # Create engine
        engine = LiveTradingEngine()
        
        # Initialize (connects to IB)
        print("\nInitializing...")
        if engine.initialize():
            print("✓ Initialization successful")
            print(f"✓ Connected to IB Gateway")
            print(f"✓ Trading symbols: {', '.join(engine.symbols)}")
            print(f"✓ Active strategies: {', '.join(engine.strategies.keys())}")
            
            # Print status
            engine._print_status()
            
            # Print positions (if any)
            if engine.position_tracker:
                print("\n")
                engine.position_tracker.print_summary()
            
            # Print order manager status
            if engine.order_manager:
                print("\n")
                engine.order_manager.print_status()
            
            print("\n✓ All components initialized successfully")
            
            # Clean up
            engine.stop()
            
            return True
        else:
            print("✗ Initialization failed")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_market_data():
    """
    Test market data retrieval.
    """
    print("="*60)
    print("MARKET DATA TEST")
    print("="*60)
    
    try:
        engine = LiveTradingEngine()
        
        if not engine.initialize():
            print("Failed to initialize")
            return
        
        print("\nMarket data retrieved:")
        for symbol, df in engine.market_data.items():
            print(f"\n{symbol}:")
            print(f"  Bars: {len(df)}")
            if len(df) > 0:
                latest = df.iloc[-1]
                print(f"  Latest Close: ${latest['close']:.2f}")
                print(f"  Latest Volume: {latest['volume']:,}")
        
        # Print latest bars
        print("\n" + "="*60)
        print("LATEST BARS")
        print("="*60)
        for symbol, bar in engine.latest_bars.items():
            print(f"\n{symbol}:")
            print(f"  Open:   ${bar['open']:.2f}")
            print(f"  High:   ${bar['high']:.2f}")
            print(f"  Low:    ${bar['low']:.2f}")
            print(f"  Close:  ${bar['close']:.2f}")
            print(f"  Volume: {bar['volume']:,}")
        
        engine.stop()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def test_signal_generation():
    """
    Test signal generation without executing trades.
    """
    print("="*60)
    print("SIGNAL GENERATION TEST")
    print("="*60)
    
    try:
        engine = LiveTradingEngine()
        
        if not engine.initialize():
            print("Failed to initialize")
            return
        
        print("\nGenerating signals...")
        
        # Generate signals for all symbols
        engine._generate_signals()
        
        print(f"\nSignals generated: {engine.signals_generated}")
        
        # Check alert history
        if engine.alert_system:
            signal_alerts = engine.alert_system.get_alert_history(
                alert_type=engine.alert_system.AlertType.SIGNAL
            )
            
            if signal_alerts:
                print(f"\nSignal alerts: {len(signal_alerts)}")
                for alert in signal_alerts[-5:]:  # Last 5
                    print(f"  - {alert['message'][:100]}")
            else:
                print("\nNo signals generated")
        
        engine.stop()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == 'quick':
            quick_test()
        elif mode == 'data':
            test_market_data()
        elif mode == 'signals':
            test_signal_generation()
        elif mode == 'full':
            main()
        else:
            print("Usage:")
            print("  python test_live_trading.py quick    - Quick connection test")
            print("  python test_live_trading.py data     - Test market data")
            print("  python test_live_trading.py signals  - Test signal generation")
            print("  python test_live_trading.py full     - Full live trading test")
    else:
        # Default: quick test
        print("Running quick test...")
        print("Use 'python test_live_trading.py full' for full test\n")
        quick_test()
