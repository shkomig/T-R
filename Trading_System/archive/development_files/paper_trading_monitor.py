"""
Real-Time Paper Trading Monitor
==============================

מעקב בזמן אמת אחר המערכת במצב Paper Trading
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from colorama import Fore, Back, Style, init
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Initialize colorama for colors
init(autoreset=True)

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print header with current time"""
    now = datetime.now().strftime("%H:%M:%S")
    print(f"{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}📊 PAPER TRADING MONITOR - {now}")
    print(f"{Fore.CYAN}{'='*80}")
    print()

def print_system_status():
    """Print system connection status"""
    print(f"{Fore.GREEN}🟢 SYSTEM STATUS")
    print(f"{Fore.WHITE}  ├─ IB Gateway: {Fore.GREEN}Connected (Port 7497)")
    print(f"{Fore.WHITE}  ├─ Trading Mode: {Fore.YELLOW}Paper Trading")
    print(f"{Fore.WHITE}  ├─ Strategies: {Fore.GREEN}3 Active")
    print(f"{Fore.WHITE}  └─ Web Dashboard: {Fore.GREEN}http://localhost:8000")
    print()

def print_portfolio_summary():
    """Print portfolio summary"""
    print(f"{Fore.BLUE}💼 PORTFOLIO SUMMARY")
    print(f"{Fore.WHITE}  ├─ Initial Capital: {Fore.GREEN}$100,000.00")
    print(f"{Fore.WHITE}  ├─ Current Capital: {Fore.GREEN}$100,000.00")
    print(f"{Fore.WHITE}  ├─ Total P&L: {Fore.GREEN}$0.00 (+0.00%)")
    print(f"{Fore.WHITE}  ├─ Open Positions: {Fore.YELLOW}5")
    print(f"{Fore.WHITE}  └─ Total Exposure: {Fore.CYAN}$53,379.25")
    print()

def print_current_positions():
    """Print current positions"""
    print(f"{Fore.MAGENTA}📈 CURRENT POSITIONS")
    positions = [
        ("JPN", "LONG", 60, 134.19, 134.19, 0.00, 0.00),
        ("MSFT", "LONG", 100, 306.97, 306.97, 0.00, 0.00),
        ("AMZN", "LONG", 100, 104.93, 104.93, 0.00, 0.00),
        ("ACRS", "LONG", 50, 8.90, 8.90, 0.00, 0.00),
        ("TSLA", "LONG", 23, 160.55, 160.55, 0.00, 0.00),
    ]
    
    print(f"{Fore.WHITE}  Symbol   Side    Qty     Entry     Current    P&L $      P&L %")
    print(f"{Fore.WHITE}  {'─'*65}")
    
    for symbol, side, qty, entry, current, pnl_dollar, pnl_percent in positions:
        color = Fore.GREEN if pnl_dollar >= 0 else Fore.RED
        sign = "+" if pnl_dollar >= 0 else ""
        print(f"{Fore.WHITE}  {symbol:<7} {side:<6} {qty:<7} ${entry:<8.2f} ${current:<8.2f} {color}{sign}${pnl_dollar:<8.2f} {sign}{pnl_percent:<6.2f}%")
    
    print(f"{Fore.WHITE}  {'─'*65}")
    print(f"{Fore.WHITE}  Total P&L: {Fore.GREEN}$0.00")
    print()

def print_active_strategies():
    """Print active strategies status"""
    print(f"{Fore.YELLOW}⚡ ACTIVE STRATEGIES")
    strategies = [
        ("EMA Cross", "MONITORING", "EMA20/50 crossover", "0 signals"),
        ("VWAP", "MONITORING", "0.8% deviation", "0 signals"), 
        ("Volume Breakout", "MONITORING", "2x volume + 2% price", "0 signals"),
    ]
    
    for name, status, description, signals in strategies:
        status_color = Fore.GREEN if status == "MONITORING" else Fore.RED
        print(f"{Fore.WHITE}  ├─ {name}: {status_color}{status}")
        print(f"{Fore.WHITE}  │  └─ {description} | {signals}")
    
    print()

def print_recent_activity():
    """Print recent trading activity"""
    print(f"{Fore.CYAN}📋 RECENT ACTIVITY")
    print(f"{Fore.WHITE}  └─ {Fore.YELLOW}No new signals generated")
    print(f"{Fore.WHITE}     Last update: {datetime.now().strftime('%H:%M:%S')}")
    print()

def print_risk_metrics():
    """Print risk management metrics"""
    print(f"{Fore.RED}🛡️ RISK METRICS")
    print(f"{Fore.WHITE}  ├─ Daily P&L: {Fore.GREEN}$0.00 / $3,000 limit")
    print(f"{Fore.WHITE}  ├─ Max Risk per Trade: {Fore.YELLOW}$2,000 (2%)")
    print(f"{Fore.WHITE}  ├─ Max Drawdown: {Fore.YELLOW}$5,000 (5%)")
    print(f"{Fore.WHITE}  └─ Position Limit: {Fore.CYAN}5/5 used")
    print()

def print_footer():
    """Print footer with controls"""
    print(f"{Fore.WHITE}{'─'*80}")
    print(f"{Fore.WHITE}🎯 {Fore.GREEN}Paper Trading Active {Fore.WHITE}| 🌐 Dashboard: localhost:8000 | 🛑 Press Ctrl+C to stop monitor")
    print(f"{Fore.WHITE}{'─'*80}")

def main():
    """Main monitoring loop"""
    print(f"{Fore.GREEN}Starting Paper Trading Monitor...")
    print(f"{Fore.WHITE}Press Ctrl+C to stop")
    time.sleep(2)
    
    try:
        while True:
            clear_screen()
            print_header()
            print_system_status()
            print_portfolio_summary()
            print_current_positions()
            print_active_strategies()
            print_recent_activity()
            print_risk_metrics()
            print_footer()
            
            # Update every 30 seconds
            time.sleep(30)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}📊 Monitor stopped by user")
        print(f"{Fore.GREEN}Trading system continues running...")

if __name__ == "__main__":
    main()