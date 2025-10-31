"""
Trading System - Main Entry Point
==================================

AI-powered automated trading system for Interactive Brokers.

Usage:
    python main.py --mode [paper|live|backtest]
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import load_config
from utils import setup_logging


def main():
    """Main entry point for the trading system."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="AI Trading System")
    parser.add_argument(
        "--mode",
        choices=["paper", "live", "backtest"],
        default="paper",
        help="Trading mode: paper, live, or backtest"
    )
    parser.add_argument(
        "--config",
        default="trading_config",
        help="Configuration file name (without .yaml)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(log_level=args.log_level)
    
    # Load configuration
    try:
        config = load_config(args.config)
        risk_config = load_config("risk_management")
        print(f"✓ Configuration loaded successfully")
    except Exception as e:
        print(f"✗ Error loading configuration: {e}")
        sys.exit(1)
    
    # Display welcome message
    print("\n" + "="*60)
    print("  AI TRADING SYSTEM")
    print("="*60)
    print(f"  Mode: {args.mode.upper()}")
    print(f"  Version: {config['system']['version']}")
    print(f"  Timezone: {config['system']['timezone']}")
    print("="*60 + "\n")
    
    # Execute based on mode
    if args.mode == "backtest":
        run_backtest(config, risk_config)
    elif args.mode == "paper":
        run_paper_trading(config, risk_config)
    elif args.mode == "live":
        run_live_trading(config, risk_config)


def run_backtest(config, risk_config):
    """Run backtesting mode."""
    print("🧪 BACKTEST MODE")
    print("-" * 60)
    print("Starting backtesting engine...")
    print("⚠️  This feature is under development")
    print("\nNext steps:")
    print("1. Implement backtesting engine")
    print("2. Load historical data")
    print("3. Run strategy simulations")
    print("4. Generate performance reports")


def run_paper_trading(config, risk_config):
    """Run paper trading mode."""
    print("📄 PAPER TRADING MODE")
    print("-" * 60)
    print("Initializing paper trading environment...")
    print("⚠️  This feature is under development")
    print("\nNext steps:")
    print("1. Connect to Interactive Brokers (Port 7497)")
    print("2. Initialize strategies")
    print("3. Start market data feed")
    print("4. Begin trading simulation")
    print("\nSafety checks:")
    print(f"✓ Max risk per trade: {risk_config['account']['max_risk_per_trade_percent']}%")
    print(f"✓ Max positions: {risk_config['position_limits']['max_positions']}")
    print(f"✓ Max drawdown: {risk_config['account']['max_drawdown_percent']}%")


def run_live_trading(config, risk_config):
    """Run live trading mode."""
    print("🔴 LIVE TRADING MODE")
    print("-" * 60)
    print("⚠️  WARNING: This will trade with real money!")
    
    # Safety confirmation
    confirm = input("\nType 'CONFIRM' to proceed with live trading: ")
    
    if confirm != "CONFIRM":
        print("Live trading cancelled.")
        return
    
    print("\n⚠️  This feature is under development")
    print("\nBefore going live:")
    print("1. Complete extensive backtesting")
    print("2. Run paper trading for 2-4 weeks")
    print("3. Verify all risk management systems")
    print("4. Start with minimal capital")
    print("5. Monitor constantly")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  System interrupted by user")
        print("Shutting down safely...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
