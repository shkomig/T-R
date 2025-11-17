"""
Drawdown Analysis Script
=========================
Retrieves current positions and trade history from IB to analyze drawdown.

Author: Claude AI
Date: 2025-11-17
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import time

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from execution.broker_interface import IBBroker
    from ib_insync import util
except ImportError as e:
    print(f"[ERROR] Missing dependencies: {e}")
    print("This script requires ib_insync and the broker interface")
    sys.exit(1)

def main():
    print("="*70)
    print("DRAWDOWN ANALYSIS - IB DATA RETRIEVAL")
    print("="*70)

    # Initialize broker
    print("\n[1] Connecting to Interactive Brokers...")
    try:
        broker = IBBroker(host='127.0.0.1', port=7497, client_id=99)
        broker.connect()
        print(f"    [OK] Connected to IB on port 7497")
    except Exception as e:
        print(f"    [ERROR] Failed to connect: {e}")
        print("\n[INFO] Make sure IB TWS/Gateway is running on port 7497")
        return

    # Get account summary
    print("\n[2] Retrieving account information...")
    try:
        account_summary = broker.get_account_summary()

        if account_summary:
            print(f"\n    Account Summary:")
            print(f"    ----------------")
            for key, value in account_summary.items():
                if 'balance' in key.lower() or 'value' in key.lower() or 'cash' in key.lower():
                    print(f"    {key}: ${float(value):,.2f}")
                elif 'pnl' in key.lower():
                    print(f"    {key}: ${float(value):,.2f}")
        else:
            print("    [WARN] No account summary available")
    except Exception as e:
        print(f"    [ERROR] Failed to get account summary: {e}")

    # Get current positions
    print("\n[3] Retrieving current positions...")
    try:
        positions = broker.get_positions()

        if positions:
            print(f"\n    Current Positions ({len(positions)}):")
            print(f"    " + "="*66)

            total_pnl = 0
            for pos in positions:
                symbol = pos.contract.symbol
                quantity = pos.position
                avg_cost = pos.avgCost
                market_price = pos.marketPrice if hasattr(pos, 'marketPrice') else 0
                market_value = pos.marketValue if hasattr(pos, 'marketValue') else 0
                unrealized_pnl = pos.unrealizedPNL if hasattr(pos, 'unrealizedPNL') else 0
                realized_pnl = pos.realizedPNL if hasattr(pos, 'realizedPNL') else 0

                total_pnl += unrealized_pnl + realized_pnl

                print(f"\n    {symbol}:")
                print(f"      Quantity: {quantity}")
                print(f"      Avg Cost: ${avg_cost:.2f}")
                print(f"      Market Price: ${market_price:.2f}")
                print(f"      Market Value: ${market_value:,.2f}")
                print(f"      Unrealized P&L: ${unrealized_pnl:,.2f}")
                print(f"      Realized P&L: ${realized_pnl:,.2f}")

            print(f"\n    " + "="*66)
            print(f"    Total P&L: ${total_pnl:,.2f}")

        else:
            print("    No open positions found")

    except Exception as e:
        print(f"    [ERROR] Failed to get positions: {e}")

    # Get executions (trades)
    print("\n[4] Retrieving recent executions...")
    try:
        # Try to get executions from the last 7 days
        executions = broker.ib.reqExecutions()

        if executions:
            print(f"\n    Recent Executions ({len(executions)}):")
            print(f"    " + "="*66)

            # Group by symbol
            by_symbol = {}
            for exec_detail in executions:
                exec_obj = exec_detail.execution
                symbol = exec_obj.symbol

                if symbol not in by_symbol:
                    by_symbol[symbol] = []

                by_symbol[symbol].append({
                    'time': exec_obj.time,
                    'side': exec_obj.side,
                    'shares': exec_obj.shares,
                    'price': exec_obj.price,
                    'cumQty': exec_obj.cumQty,
                    'avgPrice': exec_obj.avgPrice
                })

            for symbol, execs in by_symbol.items():
                print(f"\n    {symbol} ({len(execs)} trades):")
                for i, ex in enumerate(execs[:5], 1):  # Show first 5
                    print(f"      {i}. {ex['time']} - {ex['side']} {ex['shares']} @ ${ex['price']:.2f}")
                if len(execs) > 5:
                    print(f"      ... and {len(execs)-5} more trades")
        else:
            print("    No recent executions found")

    except Exception as e:
        print(f"    [ERROR] Failed to get executions: {e}")

    # Get PnL
    print("\n[5] Analyzing P&L...")
    try:
        pnl = broker.ib.pnl()

        if pnl:
            for item in pnl:
                print(f"\n    Daily P&L: ${item.dailyPnL:,.2f}")
                print(f"    Unrealized P&L: ${item.unrealizedPnL:,.2f}")
                print(f"    Realized P&L: ${item.realizedPnL:,.2f}")
        else:
            print("    No P&L data available")

    except Exception as e:
        print(f"    [ERROR] Failed to get P&L: {e}")

    # Disconnect
    print("\n[6] Disconnecting...")
    broker.disconnect()
    print("    [OK] Disconnected")

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)

    print("\nNOTE: For detailed historical analysis, check:")
    print("  - IB Account Management portal (https://www.interactivebrokers.com)")
    print("  - Activity > Flex Queries for comprehensive trade history")
    print("  - Reports > Trade Confirmations")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Analysis interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
