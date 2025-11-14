#!/usr/bin/env python3
"""
🛡️ Add Stop Loss to All Existing Positions
==========================================

This script adds stop loss orders to all existing positions
that don't already have stop loss protection.

Features:
- 3% stop loss for all positions
- SMART routing for optimal execution
- Skip positions that already have stop loss orders
- Log all actions taken

Author: T-R Trading System
Date: November 6, 2025
"""

import sys
import os
import time
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from execution.broker_interface import IBBroker
from ib_insync import LimitOrder, StopOrder, Stock

def add_stop_loss_to_positions():
    """Add stop loss orders to all existing positions"""
    
    print("🛡️ Adding Stop Loss Orders to All Positions")
    print("=" * 50)
    
    # Connect to TWS
    broker = IBBroker()
    print("🔌 Connecting to TWS...")
    
    if not broker.connect():
        print("❌ Failed to connect to TWS")
        return False
    
    print("✅ Connected to TWS")
    
    try:
        # Get all current positions
        print("📊 Getting current positions...")
        positions = broker.get_positions()
        
        if not positions:
            print("✅ No positions found - nothing to do")
            return True
        
        print(f"📋 Found {len(positions)} positions")
        
        # Get existing orders to avoid duplicates
        print("🔍 Checking existing orders...")
        existing_orders = broker.get_open_orders()
        
        # Find symbols that already have stop orders
        symbols_with_stops = set()
        for order in existing_orders:
            if hasattr(order, 'orderType') and 'STP' in order.orderType:
                symbols_with_stops.add(order.contract.symbol)
        
        print(f"📋 Found {len(symbols_with_stops)} symbols with existing stop orders")
        
        stop_loss_percent = 0.03  # 3% stop loss
        orders_created = 0
        
        for pos in positions:
            symbol = pos['symbol']
            quantity = abs(pos['position'])  # Get absolute quantity
            avg_cost = pos['avg_cost']
            
            if quantity == 0:
                print(f"⏭️  Skipping {symbol} - zero position")
                continue
            
            if symbol in symbols_with_stops:
                print(f"⏭️  Skipping {symbol} - already has stop loss")
                continue
            
            # Calculate stop loss price (3% below average cost)
            stop_price = avg_cost * (1 - stop_loss_percent)
            
            print(f"🎯 Creating stop loss for {symbol}:")
            print(f"   Position: {quantity} shares @ ${avg_cost:.2f}")
            print(f"   Stop Price: ${stop_price:.2f} (-{stop_loss_percent:.1%})")
            
            try:
                # Create stop order
                contract = Stock(symbol, "SMART", "USD")
                
                # Create stop loss order
                stop_order = StopOrder(
                    action='SELL',  # Always sell to close position
                    totalQuantity=quantity,
                    stopPrice=stop_price
                )
                
                # Place the order with SMART routing
                stop_order.outsideRth = True  # Allow outside regular trading hours
                stop_order.tif = 'GTC'  # Good Till Cancelled
                
                # Submit the order
                trade = broker.ib.placeOrder(contract, stop_order)
                
                print(f"✅ Stop loss order placed for {symbol}")
                orders_created += 1
                
                # Small delay to avoid overwhelming the system
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Failed to create stop loss for {symbol}: {e}")
        
        print("\n" + "=" * 50)
        print(f"📊 SUMMARY:")
        print(f"   Total Positions: {len(positions)}")
        print(f"   Stop Loss Orders Created: {orders_created}")
        print(f"   Already Protected: {len(symbols_with_stops)}")
        print("✅ Stop loss addition completed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding stop losses: {e}")
        return False
    
    finally:
        print("🔌 Disconnecting from TWS...")
        broker.disconnect()
        print("✅ Disconnected")

if __name__ == "__main__":
    print(f"🛡️ Stop Loss Addition Script")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = add_stop_loss_to_positions()
    
    print()
    print(f"📅 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("🎉 All stop losses added successfully!")
        sys.exit(0)
    else:
        print("⚠️ Some issues occurred during stop loss addition")
        sys.exit(1)