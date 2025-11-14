"""
Test TWS Market Scanner Integration
=====================================
Tests the scanner functionality without running the full dashboard
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from ib_insync import IB, ScannerSubscription
import time

def test_scanner_connection():
    """Test basic scanner connection and data fetch"""
    print("=" * 70)
    print("TWS MARKET SCANNER TEST")
    print("=" * 70)
    print()

    ib = None
    try:
        # Connect to TWS
        print("[1] Connecting to TWS...")
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=9998)
        print("    [OK] Connected successfully!")
        print()

        # Create scanner subscription
        print("[2] Creating scanner subscription...")
        sub = ScannerSubscription(
            instrument='STK',
            locationCode='STK.US',
            scanCode='TOP_PERC_GAIN'
        )
        print("    [OK] Subscription created: TOP_PERC_GAIN (US Stocks)")
        print()

        # Request scanner data
        print("[3] Requesting scanner data...")
        scanner_data = ib.reqScannerData(sub)
        print(f"    [OK] Received {len(scanner_data)} results")
        print()

        # Display top 10 results
        print("[4] Top 10 % Gainers:")
        print("-" * 70)
        print(f"  {'Rank':<6} {'Symbol':<10} {'Distance':>10}")
        print("-" * 70)

        for i, item in enumerate(scanner_data[:10], 1):
            try:
                contract = item.contractDetails.contract
                symbol = contract.symbol
                distance = item.distance
                rank = item.rank

                print(f"  {rank:<6} {symbol:<10} {distance:>10}")
            except Exception as e:
                print(f"  Error processing item {i}: {e}")

        print()
        print("=" * 70)
        print("[SUCCESS] Scanner integration test completed!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Run: python simple_live_dashboard.py")
        print("2. Scanner will automatically fetch hot stocks every 5 minutes")
        print("3. System will trade MSTR, LCID + top 20 gainers (max 25 total)")

        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure TWS/IB Gateway is running")
        print("2. Check that port 7497 is correct (Paper Trading)")
        print("3. Verify API connections are enabled in TWS")
        print("4. Check that client ID 9998 is not already in use")
        return False

    finally:
        if ib and ib.isConnected():
            print("\n[CLEANUP] Disconnecting...")
            ib.disconnect()
            print("[OK] Disconnected")

if __name__ == "__main__":
    test_scanner_connection()
