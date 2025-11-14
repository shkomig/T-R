#!/usr/bin/env python3
"""
Emergency Position Closure Script with Smart Order Routing (SMART)
Closes all open positions to prevent further losses
"""

import asyncio
import logging
from ib_insync import IB, Stock, MarketOrder
from typing import List, Dict
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmergencyPositionCloser:
    def __init__(self):
        self.ib = IB()
        self.closed_positions: List[Dict] = []
        
    async def connect(self):
        """Connect to Interactive Brokers TWS"""
        try:
            print("🔌 Connecting to Interactive Brokers...")
            await self.ib.connectAsync('127.0.0.1', 7497, clientId=999)
            print("✅ Connected to TWS successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to TWS: {e}")
            return False
    
    async def get_positions(self):
        """Get all open positions"""
        try:
            print("\n📊 Getting current positions...")
            await self.ib.reqPositionsAsync()
            positions = self.ib.positions()
            
            if not positions:
                print("✅ No open positions found!")
                return []
            
            print(f"🚨 Found {len(positions)} open positions:")
            print("-" * 60)
            
            total_value = 0
            for pos in positions:
                contract = pos.contract
                position = pos.position
                avg_cost = pos.avgCost
                
                # Get current market price
                ticker = self.ib.reqMktData(contract)
                await asyncio.sleep(1)  # Wait for market data
                
                current_price = ticker.last if ticker.last else ticker.close if ticker.close else avg_cost
                value = position * avg_cost
                pnl = position * (current_price - avg_cost) if current_price != avg_cost else 0
                
                total_value += value
                
                print(f"  {contract.symbol:<8} | Qty: {position:>6} | Value: ${value:>10,.2f} | P&L: ${pnl:>8,.2f}")
            
            print("-" * 60)
            print(f"💰 Total Market Value: ${total_value:,.2f}")
            
            return positions
            
        except Exception as e:
            print(f"❌ Error getting positions: {e}")
            return []
    
    async def close_all_positions(self):
        """Close all open positions using SMART routing"""
        positions = await self.get_positions()
        
        if not positions:
            return True
        
        print("\n🛑 Placing EMERGENCY CLOSE orders with SMART routing")
        
        orders = []
        for pos in positions:
            contract = pos.contract
            position = pos.position
            
            if position == 0:
                continue
                
            # Determine order action
            action = 'SELL' if position > 0 else 'BUY'
            quantity = abs(position)
            
            # Create market order with SMART routing
            order = MarketOrder(action, quantity)
            order.outsideRth = True  # Allow trading outside regular hours
            order.transmit = True
            
            # Use SMART routing instead of direct exchange routing
            contract.exchange = 'SMART'
            
            print(f"🔄 Placing EMERGENCY CLOSE order for {contract.symbol}: {action} {quantity}")
            
            try:
                trade = self.ib.placeOrder(contract, order)
                orders.append(trade)
                await asyncio.sleep(0.1)  # Small delay between orders
                
            except Exception as e:
                print(f"❌ Failed to place order for {contract.symbol}: {e}")
        
        return await self.monitor_orders(orders)
    
    async def monitor_orders(self, orders):
        """Monitor order execution"""
        if not orders:
            return True
            
        print(f"\n⏳ Monitoring {len(orders)} orders...")
        
        # Wait for orders to fill
        max_wait_time = 60  # Maximum wait time in seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            await asyncio.sleep(2)
            
            # Check order status
            filled_count = 0
            cancelled_count = 0
            
            print("\n📋 Order Status:")
            print("-" * 40)
            
            for trade in orders:
                status = trade.orderStatus.status
                symbol = trade.contract.symbol
                filled = trade.orderStatus.filled
                remaining = trade.orderStatus.remaining
                
                print(f"  {symbol:<8} | Status: {status:<10} | Filled: {filled:>6} | Remaining: {remaining:>6}")
                
                if status in ['Filled', 'Cancelled']:
                    if status == 'Filled':
                        filled_count += 1
                    else:
                        cancelled_count += 1
            
            if filled_count + cancelled_count == len(orders):
                break
        
        return await self.verify_closure()
    
    async def verify_closure(self):
        """Verify all positions are closed"""
        print("\n🔍 Final position check...")
        remaining_positions = await self.get_positions()
        
        if remaining_positions:
            print(f"⚠️  WARNING: {len(remaining_positions)} positions still open:")
            for pos in remaining_positions:
                print(f"  {pos.contract.symbol}: {pos.position} shares")
            return False
        else:
            print("✅ All positions successfully closed!")
            return True
    
    async def run(self):
        """Main execution method"""
        print("🚨 EMERGENCY POSITION CLOSURE WITH SMART ROUTING")
        print("This will close ALL open positions immediately!")
        print("=" * 60)
        
        # Connect to TWS
        if not await self.connect():
            return False
        
        try:
            # Close all positions
            success = await self.close_all_positions()
            
            if success:
                print("\n✅ Emergency closure completed successfully!")
            else:
                print("\n⚠️  Emergency closure completed with warnings!")
            
            return success
            
        except Exception as e:
            print(f"\n❌ Error during emergency closure: {e}")
            return False
            
        finally:
            print("\n🔌 Disconnecting from TWS")
            self.ib.disconnect()

async def main():
    """Main function"""
    # Confirm action
    response = input("\nAre you sure you want to proceed with SMART routing? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Operation cancelled by user")
        return
    
    print("\n🚀 Starting emergency closure with SMART routing...")
    
    closer = EmergencyPositionCloser()
    success = await closer.run()
    
    if success:
        print("\n✅ Emergency position closure completed!")
    else:
        print("\n⚠️  Emergency position closure finished with issues!")

if __name__ == "__main__":
    asyncio.run(main())