"""
Test Interactive Brokers Connection
====================================

Test script to verify connection to TWS/Gateway.

Usage:
    python test_ib_connection.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from execution.broker_interface import IBBroker
from utils.data_processor import DataProcessor
from config import load_config
import pandas as pd


def test_connection():
    """Test basic connection to IB."""
    print("\n" + "="*60)
    print("  TESTING INTERACTIVE BROKERS CONNECTION")
    print("="*60 + "\n")
    
    # Load config
    try:
        config = load_config("trading_config")
        print("✓ Configuration loaded")
    except Exception as e:
        print(f"✗ Error loading config: {e}")
        return False
    
    # Create broker instance
    broker = IBBroker(
        host=config['broker']['host'],
        port=config['broker']['port'],
        client_id=config['broker']['client_id']
    )
    
    print(f"\nConnecting to {broker.host}:{broker.port}...")
    
    # Test connection
    if not broker.connect():
        print("✗ Connection failed")
        return False
    
    print("✓ Connection successful\n")
    
    # Test account info
    print("-" * 60)
    print("ACCOUNT INFORMATION")
    print("-" * 60)
    
    account_summary = broker.get_account_summary()
    
    if account_summary:
        # Display key account metrics
        important_fields = [
            'NetLiquidation',
            'TotalCashValue',
            'BuyingPower',
            'GrossPositionValue',
            'UnrealizedPnL'
        ]
        
        for field in important_fields:
            if field in account_summary:
                value = account_summary[field]['value']
                currency = account_summary[field]['currency']
                print(f"  {field:20s}: {value:>15s} {currency}")
    else:
        print("  No account data available")
    
    # Test positions
    print("\n" + "-" * 60)
    print("CURRENT POSITIONS")
    print("-" * 60)
    
    positions = broker.get_positions()
    
    if positions:
        for pos in positions:
            print(f"  {pos['symbol']:6s} | Qty: {pos['position']:>6.0f} | "
                  f"Avg Cost: ${pos['avg_cost']:>8.2f} | "
                  f"P&L: ${pos['pnl']:>8.2f}")
    else:
        print("  No open positions")
    
    # Test historical data
    print("\n" + "-" * 60)
    print("TESTING HISTORICAL DATA RETRIEVAL")
    print("-" * 60)
    
    test_symbol = "AAPL"
    print(f"\nFetching 1 day of 30-minute bars for {test_symbol}...")
    
    bars = broker.get_historical_data(
        symbol=test_symbol,
        duration="1 D",
        bar_size="30 mins"
    )
    
    if bars:
        print(f"✓ Retrieved {len(bars)} bars")
        
        # Convert to DataFrame
        df = DataProcessor.bars_to_dataframe(bars)
        
        if not df.empty:
            print("\nFirst 5 bars:")
            print(df.head())
            
            print("\nLast 5 bars:")
            print(df.tail())
            
            print(f"\nData Summary:")
            print(f"  Period: {df.index[0]} to {df.index[-1]}")
            print(f"  Open:  ${df['open'].iloc[0]:.2f}")
            print(f"  Close: ${df['close'].iloc[-1]:.2f}")
            print(f"  High:  ${df['high'].max():.2f}")
            print(f"  Low:   ${df['low'].min():.2f}")
            print(f"  Avg Volume: {df['volume'].mean():,.0f}")
    else:
        print("✗ Failed to retrieve historical data")
    
    # Disconnect
    print("\n" + "-" * 60)
    broker.disconnect()
    print("✓ Disconnected from IB")
    
    print("\n" + "="*60)
    print("  CONNECTION TEST COMPLETED SUCCESSFULLY")
    print("="*60 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        success = test_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
