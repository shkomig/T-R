"""
Simple Live Trading Dashboard
==============================
ממשק פשוט למסחר חי - משתמש רק ב-Historical Data

עובד ללא Real-Time subscription!
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import time
import yaml
import pandas as pd
from colorama import Fore, Back, Style, init

sys.path.append(str(Path(__file__).parent))

from execution.broker_interface import IBBroker
from strategies import VWAPStrategy

# Initialize colorama
init(autoreset=True)


class SimpleLiveDashboard:
    """Simple Live Trading Dashboard"""
    
    def __init__(self):
        self.broker = None
        self.strategy = None
        self.symbols = ['AAPL', 'GOOGL', 'MSFT']
        self.auto_trading = True  # Enable auto-trading
        self.position_size = 10000  # $10k per position
        self.max_positions = 3  # Maximum 3 positions
        
        # Load config
        with open('config/trading_config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
    
    def _clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _print_header(self):
        """Print dashboard header"""
        print(Fore.CYAN + "="*80)
        print(Fore.CYAN + Style.BRIGHT + "     📊 LIVE TRADING DASHBOARD - HISTORICAL DATA MODE")
        print(Fore.CYAN + "="*80)
        print(f"{Fore.WHITE}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if self.auto_trading:
            print(f"{Fore.GREEN}🤖 Auto-Trading: ENABLED{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⏸️  Auto-Trading: DISABLED{Style.RESET_ALL}")
        print()
    
    def execute_trade(self, symbol: str, signal: str, price: float):
        """Execute trade based on signal"""
        if not self.auto_trading:
            return False
        
        try:
            # Get current positions
            positions = self.broker.get_positions()
            current_symbols = [pos['symbol'] for pos in positions]
            
            if signal == 'long' and symbol not in current_symbols:
                # Check if we have room for more positions
                if len(positions) >= self.max_positions:
                    print(f"    {Fore.YELLOW}⚠️  Max positions ({self.max_positions}) reached{Style.RESET_ALL}")
                    return False
                
                # Calculate quantity
                quantity = int(self.position_size / price)
                
                # Place buy order
                result = self.broker.place_order(
                    symbol=symbol,
                    action='BUY',
                    quantity=quantity,
                    order_type='MKT'
                )
                
                if result:
                    print(f"    {Fore.GREEN}✅ BUY ORDER: {quantity} shares of {symbol} @ ${price:.2f}{Style.RESET_ALL}")
                    return True
                else:
                    print(f"    {Fore.RED}❌ Failed to place BUY order for {symbol}{Style.RESET_ALL}")
                    return False
            
            elif signal == 'exit' and symbol in current_symbols:
                # Find position to exit
                position = next((pos for pos in positions if pos['symbol'] == symbol), None)
                if position:
                    quantity = abs(int(position['position']))
                    
                    # Place sell order
                    result = self.broker.place_order(
                        symbol=symbol,
                        action='SELL',
                        quantity=quantity,
                        order_type='MKT'
                    )
                    
                    if result:
                        print(f"    {Fore.RED}✅ SELL ORDER: {quantity} shares of {symbol} @ ${price:.2f}{Style.RESET_ALL}")
                        return True
                    else:
                        print(f"    {Fore.RED}❌ Failed to place SELL order for {symbol}{Style.RESET_ALL}")
                        return False
        
        except Exception as e:
            print(f"    {Fore.RED}❌ Trade execution error: {e}{Style.RESET_ALL}")
            return False
        
        return False
    
    def run(self):
        """Run the dashboard"""
        print("="*80)
        print("     🚀 STARTING LIVE TRADING DASHBOARD")
        print("="*80)
        print()
        print("✓ Strategy: VWAP (Best performer: +1.46%, Win Rate: 42.86%)")
        print("✓ Mode: Paper Trading")
        print("✓ Data: Historical bars (FREE - no subscription needed)")
        print("✓ Update: Every 30 seconds")
        if self.auto_trading:
            print(f"🤖 Auto-Trading: {Fore.GREEN}ENABLED{Style.RESET_ALL} (Position Size: ${self.position_size:,})")
        else:
            print(f"⏸️  Auto-Trading: {Fore.YELLOW}DISABLED{Style.RESET_ALL}")
        print()
        print("Press Ctrl+C to stop...")
        print()
        time.sleep(2)
        
        try:
            # Connect to IB Gateway
            print("🔌 Connecting to IB Gateway...")
            self.broker = IBBroker(port=7497, client_id=10)
            
            if not self.broker.connect():
                print("❌ Failed to connect to IB Gateway")
                print("   Make sure IB Gateway is running on Port 7497")
                return
            
            print("✅ Connected successfully!")
            print()
            
            # Initialize strategy
            self.strategy = VWAPStrategy(self.config['strategies']['vwap'])
            
            # Get account info
            account_info = self.broker.get_account_summary()
            
            cycle = 0
            
            while True:
                cycle += 1
                
                # Clear screen
                self._clear_screen()
                
                # Print header
                self._print_header()
                
                # Account Status
                print(Fore.WHITE + Style.BRIGHT + "ACCOUNT STATUS")
                print(Fore.WHITE + "─"*80)
                
                if account_info:
                    # Extract values from dictionary format
                    equity = account_info.get('NetLiquidation', {}).get('value', 'N/A')
                    cash = account_info.get('TotalCashValue', {}).get('value', 'N/A')
                    buying_power = account_info.get('BuyingPower', {}).get('value', 'N/A')
                    
                    # Format numbers nicely
                    if equity != 'N/A':
                        equity = f"${float(equity):,.2f}"
                    if cash != 'N/A':
                        cash = f"${float(cash):,.2f}"
                    if buying_power != 'N/A':
                        buying_power = f"${float(buying_power):,.2f}"
                    
                    print(f"💰 Net Liquidation: {Fore.GREEN}{equity}{Style.RESET_ALL}")
                    print(f"💵 Cash:            {Fore.WHITE}{cash}{Style.RESET_ALL}")
                    print(f"🔥 Buying Power:    {Fore.YELLOW}{buying_power}{Style.RESET_ALL}")
                else:
                    print(Fore.YELLOW + "⚠️  Account info not available")
                print()
                
        # Positions
        print(Fore.WHITE + Style.BRIGHT + "POSITIONS")
        print(Fore.WHITE + "─"*80)
        
        positions = self.broker.get_positions()
        
        # Filter out invalid symbols that cause errors
        valid_symbols = {'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'ACRS'}
        
        if positions:
            for pos in positions:
                # pos is now a dictionary
                symbol = pos['symbol']
                quantity = pos['position']
                entry_price = pos['avg_cost']
                
                # Skip invalid symbols
                if symbol not in valid_symbols:
                    print(f"  {Fore.YELLOW}{symbol:<8} | Qty: {quantity} | Entry: ${entry_price:>8.2f} | Invalid symbol - skipped{Style.RESET_ALL}")
                    continue
                
                # Get current price via historical data
                bars = self.broker.get_historical_data(
                    symbol=symbol,
                    duration="1 D",
                    bar_size="1 min"
                )
                
                if bars and len(bars) > 0:
                    # Convert BarDataList to get last price
                    current_price = bars[-1].close if hasattr(bars[-1], 'close') else entry_price
                    pnl = (current_price - entry_price) * quantity
                    pnl_pct = ((current_price - entry_price) / entry_price) * 100 if entry_price > 0 else 0
                    
                    pnl_color = Fore.GREEN if pnl >= 0 else Fore.RED
                    
                    print(f"  {Fore.CYAN}{symbol:<8}{Style.RESET_ALL} | "
                          f"Qty: {quantity:>4} | "
                          f"Entry: ${entry_price:>7.2f} | "
                          f"Current: ${current_price:>7.2f} | "
                          f"P&L: {pnl_color}{pnl:>+9.2f}{Style.RESET_ALL} "
                          f"({pnl_color}{pnl_pct:>+6.2f}%{Style.RESET_ALL})")
                else:
                    print(f"  {Fore.CYAN}{symbol:<8}{Style.RESET_ALL} | Qty: {quantity:>4} | Entry: ${entry_price:>7.2f} | {Fore.YELLOW}No current price{Style.RESET_ALL}")
        else:
            print(Fore.YELLOW + "  No open positions")
                print()
                
                # Market Data & Signals
                print(Fore.WHITE + Style.BRIGHT + "MARKET DATA & SIGNALS")
                print(Fore.WHITE + "─"*80)
                
                for symbol in self.symbols:
                    # Get historical data (2 days for enough bars)
                    bars = self.broker.get_historical_data(
                        symbol=symbol,
                        duration="2 D",
                        bar_size="30 mins"
                    )
                    
                    if bars is not None and len(bars) > 5:
                        # Convert BarDataList to DataFrame
                        df = pd.DataFrame([{
                            'open': bar.open,
                            'high': bar.high,
                            'low': bar.low,
                            'close': bar.close,
                            'volume': bar.volume
                        } for bar in bars])
                        df.index = pd.to_datetime([bar.date for bar in bars])
                        
                        current = df.iloc[-1]
                        prev = df.iloc[-2]
                        
                        change = current['close'] - prev['close']
                        change_pct = (change / prev['close']) * 100
                        
                        price_color = Fore.GREEN if change >= 0 else Fore.RED
                        
                        # Analyze with VWAP strategy
                        analysis = self.strategy.analyze(df)
                        
                        # Calculate VWAP manually
                        df['typical'] = (df['high'] + df['low'] + df['close']) / 3
                        df['vwap'] = (df['typical'] * df['volume']).cumsum() / df['volume'].cumsum()
                        vwap = df['vwap'].iloc[-1]
                        
                        deviation = ((current['close'] - vwap) / vwap) * 100
                        
                        # Signal
                        signal_str = ""
                        signal_type = analysis.get('signal')
                        
                        if signal_type == 'long':
                            signal_str = f"{Fore.GREEN}📈 LONG{Style.RESET_ALL}"
                            # Execute auto-trade
                            if self.auto_trading:
                                self.execute_trade(symbol, 'long', current['close'])
                        elif signal_type == 'exit':
                            signal_str = f"{Fore.RED}📉 EXIT{Style.RESET_ALL}"
                            # Execute auto-trade
                            if self.auto_trading:
                                self.execute_trade(symbol, 'exit', current['close'])
                        else:
                            signal_str = f"{Fore.YELLOW}⏸️  HOLD{Style.RESET_ALL}"
                        
                        print(f"  {Fore.CYAN}{symbol:<8}{Style.RESET_ALL} | "
                              f"${current['close']:>7.2f} "
                              f"{price_color}{change:>+6.2f}{Style.RESET_ALL} "
                              f"({price_color}{change_pct:>+5.2f}%{Style.RESET_ALL}) | "
                              f"VWAP: ${vwap:>7.2f} | "
                              f"Dev: {deviation:>+5.2f}% | "
                              f"{signal_str}")
                    else:
                        print(f"  {Fore.CYAN}{symbol:<8}{Style.RESET_ALL} | {Fore.YELLOW}⚠️  No data{Style.RESET_ALL}")
                
                print()
                
                # Footer
                print(Fore.WHITE + "─"*80)
                print(f"Cycle: #{cycle} | Next update in 10 seconds...")
                print(Fore.YELLOW + "⏸️  Press Ctrl+C to stop")
                print()
                
                # Wait 10 seconds
                time.sleep(10)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.broker:
                print("\n🛑 Disconnecting...")
                self.broker.disconnect()
            print("✅ Dashboard stopped\n")


if __name__ == "__main__":
    dashboard = SimpleLiveDashboard()
    dashboard.run()
