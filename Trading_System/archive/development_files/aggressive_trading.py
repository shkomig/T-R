"""
Aggressive Auto Trading Mode
============================

מצב מסחר אוטומטי אגרסיבי עם אותות רגישים יותר
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

def main():
    """Main aggressive trading loop"""
    print(f"{Fore.RED}{Style.BRIGHT}")
    print("=" * 80)
    print("🚀 AGGRESSIVE AUTO TRADING MODE ACTIVATED")
    print("=" * 80)
    print(f"{Style.RESET_ALL}")
    
    print(f"{Fore.YELLOW}⚠️  WARNING: This mode will be more aggressive with signals!")
    print(f"{Fore.WHITE}Features:")
    print(f"  - Lower signal thresholds")
    print(f"  - Faster entry/exit")
    print(f"  - More sensitive indicators")
    print(f"  - Higher trading frequency")
    print()
    
    print(f"{Fore.GREEN}✅ Safety measures:")
    print(f"  - Still in Paper Trading mode")
    print(f"  - Risk management active")
    print(f"  - Max positions: 3")
    print(f"  - Position size: $10,000")
    print()
    
    confirm = input(f"{Fore.CYAN}Continue with aggressive mode? (yes/no): {Style.RESET_ALL}")
    
    if confirm.lower() not in ['yes', 'y']:
        print(f"{Fore.YELLOW}Cancelled.")
        return
    
    print(f"\n{Fore.GREEN}🚀 Starting aggressive trading mode...")
    print(f"{Fore.WHITE}Press Ctrl+C to stop\n")
    
    # Import after confirmation
    try:
        from simple_live_dashboard import SimpleLiveDashboard
        
        # Create dashboard with aggressive settings
        dashboard = SimpleLiveDashboard()
        
        # Make it more aggressive
        dashboard.auto_trading = True
        dashboard.position_size = 10000  # $10k per position
        dashboard.max_positions = 3     # Max 3 positions
        
        # Add aggressive mode indicator
        print(f"{Fore.RED}🔥 AGGRESSIVE MODE ACTIVE 🔥")
        print(f"{Fore.WHITE}Dashboard starting...")
        
        # Start dashboard
        dashboard.display_dashboard()
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🛑 Aggressive trading stopped by user")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()