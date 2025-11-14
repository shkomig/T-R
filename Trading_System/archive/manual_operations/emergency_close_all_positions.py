#!/usr/bin/env python3
"""
🚨 EMERGENCY POSITION CLOSURE - Force Close All Positions
==========================================================

This script will immediately close all open positions to prevent further losses.
The system has exposure of $32,093 instead of the $2,000 limit due to incorrect 
position sizing configuration.

Author: T-R Trading System
Date: November 6, 2025
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ib_insync import IB, MarketOrder
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def emergency_close_all_positions():
    """Emergency closure of all positions"""
    
    print("🚨 EMERGENCY POSITION CLOSURE STARTING...")
    print("=" * 60)
    
    # Connect to IB TWS/Gateway
    ib = IB()
    
    try:
        # Try connecting to TWS
        print("🔌 Connecting to Interactive Brokers...")
        await ib.connectAsync('127.0.0.1', 7497, clientId=999)
        print("✅ Connected to TWS successfully!")
        
        # Get all current positions
        print("\n📊 Getting current positions...")
        positions = ib.positions()
        
        if not positions:
            print("✅ No open positions found - account is clean!")
            return
        
        print(f"🚨 Found {len(positions)} open positions:")
        print("-" * 60)
        
        total_market_value = 0
        orders_placed = []
        
        for position in positions:
            symbol = position.contract.symbol
            quantity = position.position
            market_value = getattr(position, 'marketValue', quantity * getattr(position, 'avgCost', 0))
            avg_cost = getattr(position, 'avgCost', 0)
            pnl = getattr(position, 'unrealizedPNL', 0)
            
            total_market_value += abs(market_value)
            
            print(f"  {symbol:8} | Qty: {quantity:6.0f} | Value: ${market_value:10,.2f} | P&L: ${pnl:8,.2f}")
            
            if quantity != 0:  # Only close if we have a position
                # Create market order to close the position
                if quantity > 0:
                    # Close long position
                    order = MarketOrder('SELL', abs(quantity))
                else:
                    # Close short position  
                    order = MarketOrder('BUY', abs(quantity))
                
                # Place the order
                print(f"🔄 Placing EMERGENCY CLOSE order for {symbol}: {order.action} {order.totalQuantity}")
                trade = ib.placeOrder(position.contract, order)
                orders_placed.append((symbol, trade))
        
        print("-" * 60)
        print(f"💰 Total Market Value: ${total_market_value:,.2f}")
        print(f"🛑 Placed {len(orders_placed)} emergency close orders")
        
        # Wait for orders to fill
        print("\n⏳ Waiting for orders to fill...")
        await asyncio.sleep(5)  # Give time for orders to process
        
        # Check order status
        print("\n📋 Order Status:")
        print("-" * 40)
        for symbol, trade in orders_placed:
            status = trade.orderStatus.status
            filled = trade.orderStatus.filled
            remaining = trade.orderStatus.remaining
            print(f"  {symbol:8} | Status: {status:10} | Filled: {filled:6.0f} | Remaining: {remaining:6.0f}")
        
        # Final position check
        print("\n🔍 Final position check...")
        await asyncio.sleep(2)
        final_positions = ib.positions()
        
        if not final_positions:
            print("🎉 SUCCESS: All positions closed!")
        else:
            print(f"⚠️  WARNING: {len(final_positions)} positions still open:")
            for pos in final_positions:
                if pos.position != 0:
                    print(f"  {pos.contract.symbol}: {pos.position} shares")
        
        print("\n✅ Emergency closure completed!")
        
    except Exception as e:
        print(f"❌ ERROR during emergency closure: {e}")
        logger.error(f"Emergency closure failed: {e}")
    
    finally:
        # Disconnect
        if ib.isConnected():
            ib.disconnect()
            print("🔌 Disconnected from TWS")

if __name__ == "__main__":
    print("🚨 EMERGENCY POSITION CLOSURE")
    print("This will close ALL open positions immediately!")
    
    response = input("\nAre you sure you want to proceed? (yes/no): ").lower().strip()
    
    if response == 'yes':
        print("\n🚀 Starting emergency closure...")
        asyncio.run(emergency_close_all_positions())
    else:
        print("❌ Emergency closure cancelled by user")
        sys.exit(1)