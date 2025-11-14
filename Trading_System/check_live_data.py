"""
Check Live Market Data
======================
Examine what data the dashboard is actually receiving from IB
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from execution.broker_interface import IBBroker
import pandas as pd
import random

def check_live_data():
    """Check live data from IB"""
    print("="*60)
    print("CHECKING LIVE MARKET DATA")
    print("="*60)

    # Connect to IB
    client_id = random.randint(3000, 9999)
    print(f"\nConnecting to IB Gateway (client_id: {client_id})...")
    broker = IBBroker(port=7497, client_id=client_id)

    if not broker.connect():
        print("[ERROR] Failed to connect to IB")
        return

    print("[OK] Connected to IB")

    # Test symbols
    symbols = ['AAPL', 'GOOGL', 'MSFT']

    for symbol in symbols:
        print(f"\n{'='*60}")
        print(f"Symbol: {symbol}")
        print(f"{'='*60}")

        # Get historical data (30-min bars)
        print(f"\nFetching 30-min bars...")
        data = broker.get_historical_data(
            symbol=symbol,
            duration='2 D',  # 2 days
            bar_size='30 mins'
        )

        if data is not None and len(data) > 0:
            print(f"[OK] Received {len(data)} bars")
            print(f"Data type: {type(data)}")

            # Convert to DataFrame if needed
            if not isinstance(data, pd.DataFrame):
                print("Converting to DataFrame...")
                data = pd.DataFrame(data)

            print(f"\nColumns: {list(data.columns)}")
            print(f"\nPrice range: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
            print(f"Latest price: ${data['close'].iloc[-1]:.2f}")
            print(f"Average volume: {data['volume'].mean():,.0f}")

            print(f"\nLast 3 bars:")
            print(data[['open', 'high', 'low', 'close', 'volume']].tail(3).to_string())

            # Check if data has variety
            price_change = ((data['close'].iloc[-1] - data['close'].iloc[0]) / data['close'].iloc[0]) * 100
            print(f"\nTotal price change: {price_change:+.2f}%")

            # Check for crossover potential
            if len(data) >= 50:
                ema_20 = data['close'].ewm(span=20, adjust=False).mean()
                ema_50 = data['close'].ewm(span=50, adjust=False).mean()

                print(f"\nEMA Analysis:")
                print(f"  EMA20 (latest): ${ema_20.iloc[-1]:.2f}")
                print(f"  EMA50 (latest): ${ema_50.iloc[-1]:.2f}")
                print(f"  Position: {'ABOVE' if ema_20.iloc[-1] > ema_50.iloc[-1] else 'BELOW'}")

                # Check for recent crossover
                for i in range(-1, -min(6, len(data)), -1):
                    if i > -len(data):
                        curr_fast = ema_20.iloc[i]
                        curr_slow = ema_50.iloc[i]
                        prev_fast = ema_20.iloc[i-1]
                        prev_slow = ema_50.iloc[i-1]

                        if prev_fast <= prev_slow and curr_fast > curr_slow:
                            print(f"  [!] BULLISH CROSSOVER at bar {i} (price: ${data['close'].iloc[i]:.2f})")
                        elif prev_fast >= prev_slow and curr_fast < curr_slow:
                            print(f"  [!] BEARISH CROSSOVER at bar {i} (price: ${data['close'].iloc[i]:.2f})")

        else:
            print("[ERROR] No data received")

    # Disconnect
    broker.disconnect()
    print(f"\n\n[OK] Analysis complete")

if __name__ == "__main__":
    check_live_data()
