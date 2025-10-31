"""
Force Trading Mode - Demo Execution
===================================

מצב שמכריח את המערכת לבצע עסקאות כדי לבדוק את הביצוע
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from colorama import Fore, Back, Style, init
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from execution.broker_interface import IBBroker

# Initialize colorama
init(autoreset=True)

class ForceTradingDemo:
    """Demo class for forced trading execution"""
    
    def __init__(self):
        self.broker = None
        self.demo_symbols = ['AAPL', 'GOOGL', 'MSFT']
        self.position_size = 5000  # Smaller positions for demo
        
    def connect_broker(self):
        """Connect to IB"""
        try:
            print(f"{Fore.CYAN}🔌 Connecting to IB Gateway...")
            self.broker = IBBroker()
            self.broker.connect()
            print(f"{Fore.GREEN}✅ Connected successfully!")
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Connection failed: {e}")
            return False
    
    def get_current_price(self, symbol):
        """Get current price for symbol"""
        try:
            # Get latest market data
            df = self.broker.get_historical_data(symbol, '1 D', '1 min')
            if len(df) > 0:
                return df['close'].iloc[-1]
            return None
        except:
            return None
    
    def demo_buy_order(self, symbol):
        """Execute a demo buy order"""
        try:
            price = self.get_current_price(symbol)
            if not price:
                print(f"{Fore.RED}❌ Could not get price for {symbol}")
                return False
            
            quantity = int(self.position_size / price)
            
            print(f"{Fore.YELLOW}📋 Preparing BUY order:")
            print(f"   Symbol: {symbol}")
            print(f"   Price: ${price:.2f}")
            print(f"   Quantity: {quantity}")
            print(f"   Total: ${quantity * price:.2f}")
            
            # Place order
            result = self.broker.place_order(
                symbol=symbol,
                action='BUY',
                order_type='MKT',
                quantity=quantity
            )
            
            if result:
                print(f"{Fore.GREEN}✅ BUY order placed successfully!")
                return True
            else:
                print(f"{Fore.RED}❌ BUY order failed!")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error placing BUY order: {e}")
            return False
    
    def demo_sell_order(self, symbol):
        """Execute a demo sell order"""
        try:
            # Get current positions
            positions = self.broker.get_positions()
            position = next((pos for pos in positions if pos['symbol'] == symbol), None)
            
            if not position:
                print(f"{Fore.YELLOW}⚠️  No position found for {symbol}")
                return False
            
            quantity = abs(int(position['position']))
            price = self.get_current_price(symbol)
            
            print(f"{Fore.YELLOW}📋 Preparing SELL order:")
            print(f"   Symbol: {symbol}")
            print(f"   Price: ${price:.2f}")
            print(f"   Quantity: {quantity}")
            print(f"   Total: ${quantity * price:.2f}")
            
            # Place order
            result = self.broker.place_order(
                symbol=symbol,
                action='SELL',
                order_type='MKT',
                quantity=quantity
            )
            
            if result:
                print(f"{Fore.GREEN}✅ SELL order placed successfully!")
                return True
            else:
                print(f"{Fore.RED}❌ SELL order failed!")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error placing SELL order: {e}")
            return False
    
    def interactive_demo(self):
        """Interactive trading demo"""
        print(f"{Fore.RED}{Style.BRIGHT}")
        print("=" * 80)
        print("🚀 FORCE TRADING DEMO - INTERACTIVE MODE")
        print("=" * 80)
        print(f"{Style.RESET_ALL}")
        
        if not self.connect_broker():
            return
        
        try:
            while True:
                print(f"\n{Fore.CYAN}Available commands:")
                print(f"  buy <symbol>  - Place buy order")
                print(f"  sell <symbol> - Place sell order") 
                print(f"  status        - Show account status")
                print(f"  positions     - Show positions")
                print(f"  auto          - Auto demo trading")
                print(f"  quit          - Exit demo")
                
                command = input(f"\n{Fore.WHITE}Enter command: {Style.RESET_ALL}").strip().lower()
                
                if command == 'quit':
                    break
                elif command == 'status':
                    self.show_status()
                elif command == 'positions':
                    self.show_positions()
                elif command == 'auto':
                    self.auto_demo()
                elif command.startswith('buy '):
                    symbol = command.split()[1].upper()
                    self.demo_buy_order(symbol)
                elif command.startswith('sell '):
                    symbol = command.split()[1].upper()
                    self.demo_sell_order(symbol)
                else:
                    print(f"{Fore.RED}Unknown command: {command}")
                    
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Demo stopped by user")
        finally:
            if self.broker:
                self.broker.disconnect()
    
    def show_status(self):
        """Show account status"""
        try:
            account = self.broker.get_account_info()
            print(f"\n{Fore.GREEN}💰 Account Status:")
            print(f"   Net Liquidation: ${account.get('NetLiquidation', 0):,.2f}")
            print(f"   Cash: ${account.get('TotalCashValue', 0):,.2f}")
            print(f"   Buying Power: ${account.get('BuyingPower', 0):,.2f}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error getting status: {e}")
    
    def show_positions(self):
        """Show current positions"""
        try:
            positions = self.broker.get_positions()
            print(f"\n{Fore.BLUE}📊 Current Positions:")
            for pos in positions:
                symbol = pos['symbol']
                qty = pos['position']
                price = pos.get('averageCost', 0)
                print(f"   {symbol}: {qty} shares @ ${price:.2f}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error getting positions: {e}")
    
    def auto_demo(self):
        """Automatic demo trading"""
        print(f"\n{Fore.YELLOW}🤖 Auto Demo Trading...")
        print(f"This will place a small buy order for AAPL")
        
        confirm = input(f"Continue? (yes/no): ")
        if confirm.lower() not in ['yes', 'y']:
            return
        
        # Demo buy AAPL
        self.demo_buy_order('AAPL')
        
        print(f"\n{Fore.CYAN}Waiting 30 seconds before next action...")
        time.sleep(30)
        
        # Demo sell AAPL
        self.demo_sell_order('AAPL')

def main():
    """Main demo function"""
    demo = ForceTradingDemo()
    demo.interactive_demo()

if __name__ == "__main__":
    main()