"""
Simple Auto Trading Simulator
=============================

מדמה ביצוע עסקאות אוטומטיות כדי לראות איך זה עובד
"""

import sys
import time
import random
from datetime import datetime
from pathlib import Path
from colorama import Fore, Back, Style, init

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Initialize colorama
init(autoreset=True)

class TradingSimulator:
    """Trading simulator for demo purposes"""
    
    def __init__(self):
        self.symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
        self.initial_capital = 100000
        self.current_capital = 100000
        self.positions = {}
        self.orders_count = 0
        self.cycle = 0
        
        # Simulated prices
        self.prices = {
            'AAPL': 271.38,
            'GOOGL': 281.46,
            'MSFT': 525.81,
            'AMZN': 222.83,
            'TSLA': 440.03
        }
    
    def clear_screen(self):
        """Clear screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def simulate_price_change(self):
        """Simulate small price changes"""
        for symbol in self.prices:
            # Random price change -2% to +2%
            change = random.uniform(-0.02, 0.02)
            self.prices[symbol] *= (1 + change)
    
    def generate_random_signal(self):
        """Generate random trading signals"""
        # 20% chance of signal each cycle
        if random.random() < 0.2:
            symbol = random.choice(self.symbols)
            signal_type = random.choice(['BUY', 'SELL'])
            
            if signal_type == 'BUY' and symbol not in self.positions:
                return {'symbol': symbol, 'action': 'BUY', 'price': self.prices[symbol]}
            elif signal_type == 'SELL' and symbol in self.positions:
                return {'symbol': symbol, 'action': 'SELL', 'price': self.prices[symbol]}
        
        return None
    
    def execute_trade(self, signal):
        """Execute simulated trade"""
        symbol = signal['symbol']
        action = signal['action']
        price = signal['price']
        
        if action == 'BUY':
            # Calculate quantity ($10,000 position)
            position_size = 10000
            quantity = int(position_size / price)
            cost = quantity * price
            
            if cost <= self.current_capital:
                self.positions[symbol] = {
                    'quantity': quantity,
                    'entry_price': price,
                    'timestamp': datetime.now()
                }
                self.current_capital -= cost
                self.orders_count += 1
                
                print(f"{Fore.GREEN}✅ BUY EXECUTED: {quantity} {symbol} @ ${price:.2f} (${cost:.2f})")
                return True
        
        elif action == 'SELL' and symbol in self.positions:
            position = self.positions[symbol]
            quantity = position['quantity']
            entry_price = position['entry_price']
            proceeds = quantity * price
            pnl = proceeds - (quantity * entry_price)
            
            self.current_capital += proceeds
            del self.positions[symbol]
            self.orders_count += 1
            
            pnl_color = Fore.GREEN if pnl >= 0 else Fore.RED
            print(f"{Fore.CYAN}✅ SELL EXECUTED: {quantity} {symbol} @ ${price:.2f} ({pnl_color}P&L: ${pnl:.2f})")
            return True
        
        return False
    
    def display_status(self):
        """Display current status"""
        self.clear_screen()
        
        # Header
        print(f"{Fore.YELLOW}{Style.BRIGHT}")
        print("=" * 80)
        print("🚀 AUTO TRADING SIMULATOR - LIVE DEMO")
        print("=" * 80)
        print(f"{Style.RESET_ALL}")
        
        print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"Cycle: #{self.cycle}")
        print(f"🤖 Auto-Trading: {Fore.GREEN}ACTIVE{Style.RESET_ALL}")
        print()
        
        # Account status
        total_pnl = self.current_capital + sum(
            pos['quantity'] * self.prices[symbol] 
            for symbol, pos in self.positions.items()
        ) - self.initial_capital
        
        pnl_color = Fore.GREEN if total_pnl >= 0 else Fore.RED
        pnl_sign = "+" if total_pnl >= 0 else ""
        
        print(f"{Fore.BLUE}💰 ACCOUNT STATUS")
        print("─" * 60)
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Cash Available:  ${self.current_capital:,.2f}")
        print(f"Total P&L:       {pnl_color}{pnl_sign}${total_pnl:,.2f}")
        print(f"Orders Executed: {self.orders_count}")
        print()
        
        # Current positions
        print(f"{Fore.MAGENTA}📊 POSITIONS")
        print("─" * 60)
        if self.positions:
            for symbol, pos in self.positions.items():
                current_price = self.prices[symbol]
                entry_price = pos['entry_price']
                quantity = pos['quantity']
                position_value = quantity * current_price
                position_pnl = position_value - (quantity * entry_price)
                position_pnl_pct = (position_pnl / (quantity * entry_price)) * 100
                
                pnl_color = Fore.GREEN if position_pnl >= 0 else Fore.RED
                pnl_sign = "+" if position_pnl >= 0 else ""
                
                print(f"{symbol:<6} | Qty: {quantity:<4} | Entry: ${entry_price:<7.2f} | "
                      f"Current: ${current_price:<7.2f} | "
                      f"{pnl_color}{pnl_sign}${position_pnl:<7.2f} ({pnl_sign}{position_pnl_pct:.1f}%)")
        else:
            print("No open positions")
        print()
        
        # Market prices
        print(f"{Fore.CYAN}📈 MARKET PRICES")
        print("─" * 60)
        for symbol in self.symbols:
            price = self.prices[symbol]
            # Simulate small random change for display
            change = random.uniform(-2, 2)
            change_color = Fore.GREEN if change >= 0 else Fore.RED
            change_sign = "+" if change >= 0 else ""
            print(f"{symbol:<6} | ${price:<7.2f} | {change_color}{change_sign}{change:.2f}")
        print()
        
        print("─" * 60)
        print(f"Next update in 5 seconds... Press Ctrl+C to stop")
        print("─" * 60)
    
    def run_simulation(self):
        """Run the trading simulation"""
        print(f"{Fore.GREEN}🚀 Starting Auto Trading Simulation...")
        print(f"{Fore.WHITE}This will simulate automatic trading with random signals")
        print(f"{Fore.YELLOW}Press Ctrl+C to stop at any time\n")
        
        try:
            while True:
                self.cycle += 1
                
                # Simulate price changes
                self.simulate_price_change()
                
                # Generate signal
                signal = self.generate_random_signal()
                
                # Execute trade if signal exists
                if signal:
                    self.execute_trade(signal)
                
                # Display status
                self.display_status()
                
                # Wait 5 seconds
                time.sleep(5)
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}🛑 Simulation stopped by user")
            
            # Final summary
            final_value = self.current_capital + sum(
                pos['quantity'] * self.prices[symbol] 
                for symbol, pos in self.positions.items()
            )
            final_pnl = final_value - self.initial_capital
            
            print(f"\n{Fore.BLUE}📊 FINAL SUMMARY:")
            print(f"Initial Capital: ${self.initial_capital:,.2f}")
            print(f"Final Value:     ${final_value:,.2f}")
            print(f"Total P&L:       ${final_pnl:,.2f}")
            print(f"Orders Executed: {self.orders_count}")

def main():
    """Main function"""
    simulator = TradingSimulator()
    simulator.run_simulation()

if __name__ == "__main__":
    main()