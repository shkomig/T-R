"""
Test Signal Generation
=====================
Verify that strategies are generating signals correctly with test data
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yaml

from strategies.vwap_strategy import VWAPStrategy
from strategies.ema_cross_strategy import EMACrossStrategy
from strategies.advanced_volume_breakout_strategy import VolumeBreakoutStrategy
from strategies.base_strategy import SignalType

# Load config
with open('config/trading_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

def create_test_data(bars=100, trend='bullish'):
    """Create synthetic test data with specific characteristics"""
    dates = [datetime.now() - timedelta(minutes=30*i) for i in range(bars)]
    dates.reverse()

    # Create price data with trend
    base_price = 100
    if trend == 'bullish':
        # Uptrend with VWAP cross
        prices = [base_price + i*0.5 + np.random.randn()*0.2 for i in range(bars)]
    elif trend == 'bearish':
        # Downtrend
        prices = [base_price - i*0.5 + np.random.randn()*0.2 for i in range(bars)]
    else:
        # Sideways
        prices = [base_price + np.random.randn()*0.5 for i in range(bars)]

    # Create OHLC
    data = {
        'timestamp': dates,
        'open': [p + np.random.randn()*0.1 for p in prices],
        'high': [p + abs(np.random.randn()*0.3) for p in prices],
        'low': [p - abs(np.random.randn()*0.3) for p in prices],
        'close': prices,
        'volume': [1000000 + np.random.randint(-100000, 100000) for _ in range(bars)]
    }

    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)

    return df

def test_strategy(strategy, name, data):
    """Test a strategy with data"""
    print(f"\n{'='*60}")
    print(f"Testing {name}")
    print(f"{'='*60}")

    try:
        # Analyze data
        analyzed_data = strategy.analyze(data)
        print(f"[OK] Analysis complete: {len(analyzed_data)} bars analyzed")

        # Generate signals
        signals = strategy.generate_signals(analyzed_data)

        print(f"\n[SIGNALS] Generated: {len(signals)}")

        if signals:
            for i, signal in enumerate(signals, 1):
                print(f"\n  Signal #{i}:")
                print(f"    Type: {signal.signal_type.value}")
                print(f"    Price: ${signal.price:.2f}")
                print(f"    Strength: {signal.strength.name}")
                print(f"    Reason: {signal.reason}")
                if signal.confidence:
                    print(f"    Confidence: {signal.confidence:.2%}")
        else:
            print("  [WARN] No signals generated")
            print("  This could mean:")
            print("    - Market conditions don't match strategy criteria")
            print("    - Filters are too strict")
            print("    - Not enough data for indicators")

        return len(signals)

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return 0

def main():
    print("\n" + "="*60)
    print("SIGNAL GENERATION TEST")
    print("="*60)

    # Create test scenarios
    scenarios = [
        ('Bullish Trend', 'bullish'),
        ('Bearish Trend', 'bearish'),
        ('Sideways', 'sideways')
    ]

    total_signals = 0

    for scenario_name, trend in scenarios:
        print(f"\n\n{'#'*60}")
        print(f"# SCENARIO: {scenario_name}")
        print(f"{'#'*60}")

        # Create test data
        test_data = create_test_data(bars=100, trend=trend)
        print(f"\nTest data created: {len(test_data)} bars")
        print(f"Price range: ${test_data['close'].min():.2f} - ${test_data['close'].max():.2f}")
        print(f"Trend: {trend}")

        # Test VWAP Strategy
        vwap_strategy = VWAPStrategy(config['strategies']['vwap'])
        total_signals += test_strategy(vwap_strategy, "VWAP Strategy", test_data.copy())

        # Test EMA Cross Strategy
        ema_strategy = EMACrossStrategy(config['strategies']['ema_cross'])
        total_signals += test_strategy(ema_strategy, "EMA Cross Strategy", test_data.copy())

        # Test Volume Breakout Strategy
        volume_strategy = VolumeBreakoutStrategy(config['strategies']['volume_breakout'])
        total_signals += test_strategy(volume_strategy, "Volume Breakout Strategy", test_data.copy())

    print("\n\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total signals generated: {total_signals}")

    if total_signals > 0:
        print("\n[SUCCESS] Strategies are generating signals!")
        print("   The issue is likely with live market data or timing")
    else:
        print("\n[WARNING] No signals generated in any scenario")
        print("   Strategy filters may be too strict")
        print("   Recommendation: Adjust strategy parameters")

if __name__ == "__main__":
    main()
