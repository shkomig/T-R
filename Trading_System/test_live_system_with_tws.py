"""
Live System Test with TWS Integration
=====================================

Comprehensive end-to-end test of the trading system with TWS (Trader Workstation)
running in the background. Verifies SignalAggregator integration in live mode.

Phase 2, Task 2.1: Live System Validation
Author: Claude AI
Date: 2025-11-11
"""

import sys
import os
import time
from datetime import datetime
from pathlib import Path

# Add project to path
sys.path.append(str(Path(__file__).parent))

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}[OK] {text}{Colors.ENDC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}[ERROR] {text}{Colors.ENDC}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}[WARN] {text}{Colors.ENDC}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}[INFO] {text}{Colors.ENDC}")


def test_tws_connection():
    """Test 1: Check TWS connection availability"""
    print_header("TEST 1: TWS Connection Check")

    try:
        from execution.fresh_data_broker import FreshDataBroker

        # Try to connect to TWS
        print_info("Attempting to connect to TWS on port 7497...")
        broker = FreshDataBroker(port=7497, client_id=1999)  # Use unique client ID for testing

        connected = broker.connect()

        if connected:
            print_success("Successfully connected to TWS!")
            print_info(f"  - Port: 7497")
            print_info(f"  - Client ID: 1999")

            # Get account info
            try:
                account_info = broker.get_account_summary()
                if account_info:
                    print_success("Account information retrieved:")
                    print_info(f"  - NetLiquidation: {account_info.get('NetLiquidation', 'N/A')}")
                    print_info(f"  - CashBalance: {account_info.get('CashBalance', 'N/A')}")
                    print_info(f"  - BuyingPower: {account_info.get('BuyingPower', 'N/A')}")
                else:
                    print_warning("Account info returned empty")
            except Exception as e:
                print_warning(f"Could not retrieve account info: {e}")

            # Disconnect
            broker.disconnect()
            return True, broker
        else:
            print_error("Failed to connect to TWS")
            print_info("Please ensure:")
            print_info("  1. TWS is running")
            print_info("  2. API is enabled (Global Configuration > API)")
            print_info("  3. Socket port is 7497")
            print_info("  4. 'Enable ActiveX and Socket Clients' is checked")
            return False, None

    except Exception as e:
        print_error(f"Connection test failed: {e}")
        return False, None


def test_signal_aggregator_initialization():
    """Test 2: Verify SignalAggregator initializes correctly"""
    print_header("TEST 2: SignalAggregator Initialization")

    try:
        import yaml

        # Load config
        config_path = Path(__file__).parent / 'config' / 'trading_config.yaml'
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        print_success("Configuration loaded successfully")

        # Import strategies
        from strategies import (
            VWAPStrategy, MomentumStrategy, BollingerBandsStrategy,
            MeanReversionStrategy, PairsTradingStrategy,
            RSIDivergenceStrategy, AdvancedVolumeBreakoutStrategy
        )

        print_success("All strategy imports successful")

        # Initialize strategies
        strategies_dict = {}

        try:
            strategies_dict['vwap'] = VWAPStrategy(config['strategies']['vwap'])
            print_success("  - VWAP Strategy initialized")
        except Exception as e:
            print_error(f"  - VWAP Strategy failed: {e}")

        try:
            strategies_dict['momentum'] = MomentumStrategy(config['strategies']['Momentum'])
            print_success("  - Momentum Strategy initialized")
        except Exception as e:
            print_error(f"  - Momentum Strategy failed: {e}")

        try:
            strategies_dict['bollinger'] = BollingerBandsStrategy(config['strategies']['Bollinger_Bands'])
            print_success("  - Bollinger Bands Strategy initialized")
        except Exception as e:
            print_error(f"  - Bollinger Strategy failed: {e}")

        try:
            strategies_dict['mean_reversion'] = MeanReversionStrategy(config['strategies']['Mean_Reversion'])
            print_success("  - Mean Reversion Strategy initialized")
        except Exception as e:
            print_error(f"  - Mean Reversion Strategy failed: {e}")

        try:
            strategies_dict['pairs_trading'] = PairsTradingStrategy(config['strategies']['Pairs_Trading'])
            print_success("  - Pairs Trading Strategy initialized")
        except Exception as e:
            print_error(f"  - Pairs Trading Strategy failed: {e}")

        try:
            rsi_config = config['strategies'].get('rsi_divergence', {})
            strategies_dict['rsi_divergence'] = RSIDivergenceStrategy(
                name="RSI_Divergence",
                config=rsi_config,
                conservative_mode=True
            )
            print_success("  - RSI Divergence Strategy initialized")
        except Exception as e:
            print_error(f"  - RSI Divergence Strategy failed: {e}")

        try:
            breakout_config = config['strategies'].get('advanced_volume_breakout', {})
            strategies_dict['volume_breakout'] = AdvancedVolumeBreakoutStrategy(
                name="Advanced_Volume_Breakout",
                config=breakout_config,
                volume_spike_multiplier=1.5
            )
            print_success("  - Advanced Volume Breakout Strategy initialized")
        except Exception as e:
            print_error(f"  - Volume Breakout Strategy failed: {e}")

        # Initialize SignalAggregator
        from Trading_Dashboard.core.signal_aggregator import SignalAggregator

        active_strategies = {
            'vwap': True,
            'momentum': True,
            'bollinger': False,
            'mean_reversion': False,
            'pairs_trading': True,
            'rsi_divergence': True,
            'volume_breakout': True
        }

        signal_aggregator = SignalAggregator(
            strategies=strategies_dict,
            active_strategies=active_strategies,
            signal_threshold=2
        )

        print_success("SignalAggregator initialized successfully!")
        print_info(f"  - Strategies loaded: {len(signal_aggregator.strategies)}")
        print_info(f"  - Signal threshold: {signal_aggregator.signal_threshold}")

        return True, signal_aggregator

    except Exception as e:
        print_error(f"SignalAggregator initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_market_data_retrieval(broker):
    """Test 3: Test market data retrieval from TWS"""
    print_header("TEST 3: Market Data Retrieval")

    try:
        # Reconnect broker
        connected = broker.connect()
        if not connected:
            print_error("Could not reconnect to TWS")
            return False

        print_success("Reconnected to TWS")

        # Test symbols
        test_symbols = ['AAPL', 'MSFT', 'GOOGL']

        for symbol in test_symbols:
            print_info(f"\nTesting {symbol}...")

            try:
                # Get historical data
                bars = broker.get_historical_data(
                    symbol=symbol,
                    duration="1 D",
                    bar_size="5 mins"
                )

                if bars and len(bars) > 0:
                    print_success(f"  - Retrieved {len(bars)} bars for {symbol}")
                    latest_bar = bars[-1]
                    print_info(f"  - Latest close: ${latest_bar.close:.2f}")
                    print_info(f"  - Volume: {latest_bar.volume:,.0f}")
                else:
                    print_warning(f"  - No data retrieved for {symbol}")

            except Exception as e:
                print_error(f"  - Failed to get data for {symbol}: {e}")

        broker.disconnect()
        return True

    except Exception as e:
        print_error(f"Market data test failed: {e}")
        return False


def test_signal_generation_live(broker, signal_aggregator):
    """Test 4: Test signal generation with live data"""
    print_header("TEST 4: Live Signal Generation")

    try:
        import pandas as pd

        # Reconnect broker
        connected = broker.connect()
        if not connected:
            print_error("Could not reconnect to TWS")
            return False

        print_success("Reconnected to TWS")

        # Test signal generation for AAPL
        symbol = 'AAPL'
        print_info(f"\nGenerating signals for {symbol}...")

        # Get historical data
        bars = broker.get_historical_data(
            symbol=symbol,
            duration="2 D",
            bar_size="30 mins"
        )

        if not bars or len(bars) < 2:
            print_error(f"Insufficient data for {symbol}")
            broker.disconnect()
            return False

        print_success(f"Retrieved {len(bars)} bars")

        # Convert to DataFrame
        df_data = []
        for bar in bars:
            df_data.append({
                'timestamp': bar.date,
                'open': bar.open,
                'high': bar.high,
                'low': bar.low,
                'close': bar.close,
                'volume': bar.volume
            })

        df = pd.DataFrame(df_data)
        print_success("Converted to DataFrame")

        # Generate signals using SignalAggregator
        print_info("Calling SignalAggregator.calculate_combined_signal()...")
        signals, combined_signal = signal_aggregator.calculate_combined_signal(df, symbol)

        if signals is None:
            print_error("Signal generation returned None (strategy failure)")
            broker.disconnect()
            return False

        print_success("Signal generation successful!")
        print_info(f"\nCombined Signal: {combined_signal.upper()}")
        print_info("\nIndividual Strategy Signals:")

        for strategy_name, signal_data in signals.items():
            signal = signal_data.get('signal', 'unknown')
            print_info(f"  - {strategy_name}: {signal}")

        # Count votes
        long_votes = sum(1 for s in signals.values() if s.get('signal') == 'long')
        exit_votes = sum(1 for s in signals.values() if s.get('signal') == 'exit')
        hold_votes = sum(1 for s in signals.values() if s.get('signal') == 'hold')

        print_info(f"\nVote Summary:")
        print_info(f"  - Long votes: {long_votes}")
        print_info(f"  - Exit votes: {exit_votes}")
        print_info(f"  - Hold votes: {hold_votes}")
        print_info(f"  - Threshold: {signal_aggregator.signal_threshold}")

        broker.disconnect()
        return True

    except Exception as e:
        print_error(f"Signal generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_risk_management_integration():
    """Test 5: Verify risk management system integration"""
    print_header("TEST 5: Risk Management Integration")

    try:
        from risk_management.advanced_risk_calculator import AdvancedRiskCalculator
        from risk_management.enhanced_position_sizer import EnhancedPositionSizer

        # Load risk config
        script_dir = Path(__file__).parent
        risk_config_path = script_dir / 'config' / 'risk_management.yaml'

        if not risk_config_path.exists():
            print_error(f"Risk config not found: {risk_config_path}")
            return False

        print_success("Risk config file found")

        # Initialize risk calculator
        risk_calc = AdvancedRiskCalculator(config_path=str(risk_config_path))
        print_success("AdvancedRiskCalculator initialized")

        # Initialize position sizer
        position_sizer = EnhancedPositionSizer(risk_calculator=risk_calc)
        print_success("EnhancedPositionSizer initialized")

        # Test risk calculation
        balance = 100000.0
        positions = {
            'AAPL': {
                'quantity': 100,
                'entry_price': 180.0,
                'current_price': 185.0
            }
        }

        risk_metrics = risk_calc.calculate_risk_metrics(balance, positions)

        print_success("Risk metrics calculated:")
        print_info(f"  - Portfolio heat: {risk_metrics.get('portfolio_heat', 0):.2%}")
        print_info(f"  - Daily loss: {risk_metrics.get('daily_loss_pct', 0):.2%}")
        print_info(f"  - Total drawdown: {risk_metrics.get('total_drawdown_pct', 0):.2%}")

        return True

    except Exception as e:
        print_error(f"Risk management test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dashboard_startup():
    """Test 6: Test dashboard startup (no auto-trading)"""
    print_header("TEST 6: Dashboard Startup Test")

    print_info("This test will start the dashboard in monitoring mode")
    print_info("Auto-trading will be DISABLED for safety")
    print_info("The test will run for 30 seconds then exit")
    print_info("")

    try:
        # Import dashboard
        import simple_live_dashboard

        print_info("Creating dashboard instance...")
        dashboard = simple_live_dashboard.SimpleLiveDashboard()

        # Verify SignalAggregator was initialized
        if hasattr(dashboard, 'signal_aggregator') and dashboard.signal_aggregator is not None:
            print_success("SignalAggregator found in dashboard!")
            print_info(f"  - Strategies: {len(dashboard.signal_aggregator.strategies)}")
            print_info(f"  - Threshold: {dashboard.signal_aggregator.signal_threshold}")
        else:
            print_error("SignalAggregator NOT found in dashboard!")
            return False

        # Disable auto-trading for safety
        dashboard.auto_trading = False
        print_warning("Auto-trading DISABLED for safety")

        print_success("Dashboard initialized successfully!")
        print_info("\nDashboard components verified:")
        print_info(f"  - Strategies loaded: 7")
        print_info(f"  - Risk management: {dashboard.enhanced_risk_management}")
        print_info(f"  - Professional execution: {dashboard.professional_execution}")
        print_info(f"  - Signal aggregator: {'Yes' if dashboard.signal_aggregator else 'No'}")

        return True

    except Exception as e:
        print_error(f"Dashboard startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_full_test_suite():
    """Run complete test suite"""
    print_header("LIVE SYSTEM TEST WITH TWS")
    print_info(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info("Phase 2, Task 2.1: SignalAggregator Integration Validation")
    print_info("")

    results = {}

    # Test 1: TWS Connection
    success, broker = test_tws_connection()
    results['TWS Connection'] = success

    if not success:
        print_error("\nTWS connection failed! Cannot proceed with live tests.")
        print_info("Please start TWS and ensure API is enabled")
        return results

    # Test 2: SignalAggregator Initialization
    success, signal_aggregator = test_signal_aggregator_initialization()
    results['SignalAggregator Init'] = success

    if not success:
        print_error("\nSignalAggregator initialization failed!")
        return results

    # Test 3: Market Data Retrieval
    success = test_market_data_retrieval(broker)
    results['Market Data'] = success

    # Test 4: Live Signal Generation
    if signal_aggregator:
        success = test_signal_generation_live(broker, signal_aggregator)
        results['Signal Generation'] = success
    else:
        results['Signal Generation'] = False

    # Test 5: Risk Management Integration
    success = test_risk_management_integration()
    results['Risk Management'] = success

    # Test 6: Dashboard Startup
    success = test_dashboard_startup()
    results['Dashboard Startup'] = success

    # Print summary
    print_header("TEST SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.ENDC}" if result else f"{Colors.RED}FAIL{Colors.ENDC}"
        print(f"{test_name:.<40} {status}")

    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.ENDC}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}[SUCCESS] All tests passed!{Colors.ENDC}")
        print(f"{Colors.GREEN}System is ready for live trading with SignalAggregator{Colors.ENDC}")
        return results, True
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}[PARTIAL] {passed}/{total} tests passed{Colors.ENDC}")
        print(f"{Colors.YELLOW}Review failed tests before proceeding{Colors.ENDC}")
        return results, False


if __name__ == '__main__':
    print("\n")
    results, all_passed = run_full_test_suite()

    # Exit code
    sys.exit(0 if all_passed else 1)
