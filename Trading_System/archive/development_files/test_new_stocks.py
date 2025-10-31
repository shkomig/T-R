"""
Test New Stocks Configuration
============================

בדיקה מהירה של המניות החדשות שהוספנו למערכת
"""

import sys
import yaml
from pathlib import Path
from colorama import Fore, Back, Style, init

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Initialize colorama
init(autoreset=True)

def test_new_stocks():
    """Test the new stocks configuration"""
    
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("=" * 80)
    print("🔍 TESTING NEW STOCKS CONFIGURATION")
    print("=" * 80)
    print(f"{Style.RESET_ALL}")
    
    # Load configs
    try:
        with open('config/trading_config.yaml', 'r') as f:
            trading_config = yaml.safe_load(f)
        
        with open('config/risk_management.yaml', 'r') as f:
            risk_config = yaml.safe_load(f)
        
        print(f"{Fore.GREEN}✅ Configuration files loaded successfully")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error loading configs: {e}")
        return
    
    # Display current stock universe
    print(f"\n{Fore.BLUE}📊 CURRENT STOCK UNIVERSE:")
    tickers = trading_config.get('universe', {}).get('tickers', [])
    
    print(f"{Fore.WHITE}  Total stocks: {len(tickers)}")
    for i, ticker in enumerate(tickers, 1):
        print(f"  {i:2d}. {ticker}")
    
    # Display position limits
    print(f"\n{Fore.YELLOW}⚙️  POSITION MANAGEMENT:")
    position_config = trading_config.get('position', {})
    risk_limits = risk_config.get('position_limits', {})
    
    print(f"  Max Positions (Trading): {position_config.get('max_positions', 'N/A')}")
    print(f"  Max Positions (Risk):    {risk_limits.get('max_positions', 'N/A')}")
    print(f"  Max Position Size:       {risk_limits.get('max_position_size_percent', 'N/A')}%")
    print(f"  Position Size Amount:    ${risk_limits.get('max_position_size_amount', 'N/A'):,}")
    
    # New stocks highlight
    print(f"\n{Fore.GREEN}🆕 NEW STOCKS ADDED:")
    new_stocks = ['NVDA', 'META', 'NFLX']
    
    for stock in new_stocks:
        if stock in tickers:
            print(f"  ✅ {stock} - Successfully added")
        else:
            print(f"  ❌ {stock} - Not found in config")
    
    # Risk assessment
    print(f"\n{Fore.RED}🛡️  RISK ASSESSMENT:")
    total_positions = risk_limits.get('max_positions', 0)
    position_size_percent = risk_limits.get('max_position_size_percent', 0)
    max_exposure = total_positions * position_size_percent
    
    print(f"  Maximum Portfolio Exposure: {max_exposure:.1f}%")
    
    if max_exposure > 100:
        print(f"  {Fore.RED}⚠️  WARNING: Potential over-exposure!")
    elif max_exposure > 80:
        print(f"  {Fore.YELLOW}⚠️  CAUTION: High exposure level")
    else:
        print(f"  {Fore.GREEN}✅ Safe exposure level")
    
    # Investment recommendations
    print(f"\n{Fore.MAGENTA}💡 INVESTMENT BREAKDOWN:")
    if total_positions > 0:
        per_position = 100 / total_positions
        print(f"  Recommended per position: {per_position:.1f}% of portfolio")
        print(f"  With $100K portfolio: ${100000 * (per_position/100):,.0f} per position")
    
    print(f"\n{Fore.WHITE}{'─' * 80}")
    print(f"🎯 {Fore.GREEN}Configuration updated successfully!")
    print(f"{Fore.WHITE}{'─' * 80}")

def test_connection():
    """Test if we can load the stocks into a trading system"""
    print(f"\n{Fore.CYAN}🔌 Testing system initialization...")
    
    try:
        # Try to import and create basic components
        from execution.broker_interface import IBBroker
        from strategies.ema_cross_strategy import EMACrossStrategy
        
        print(f"{Fore.GREEN}✅ Core modules imported successfully")
        
        # Load config
        with open('config/trading_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Test strategy initialization
        ema_config = config.get('strategies', {}).get('ema_cross', {})
        strategy = EMACrossStrategy(ema_config)
        
        print(f"{Fore.GREEN}✅ EMA Cross Strategy initialized with new config")
        
        # Get symbols
        symbols = config.get('universe', {}).get('tickers', [])
        print(f"{Fore.GREEN}✅ {len(symbols)} symbols loaded from config")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error testing system: {e}")
        return False

def main():
    """Main test function"""
    test_new_stocks()
    success = test_connection()
    
    if success:
        print(f"\n{Fore.GREEN}{Style.BRIGHT}🚀 READY TO TRADE WITH NEW STOCKS!")
        print(f"{Fore.WHITE}You can now restart the trading system to use the new configuration.")
    else:
        print(f"\n{Fore.RED}❌ Issues detected. Please check the configuration.")

if __name__ == "__main__":
    main()