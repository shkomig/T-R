"""
Debug Strategy Filters
======================
Detailed analysis of why strategies aren't generating signals
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

# Load config
with open('config/trading_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

def create_crossover_data():
    """Create data with clear EMA crossover"""
    bars = 100
    dates = [datetime.now() - timedelta(minutes=30*i) for i in range(bars)]
    dates.reverse()

    # Create downtrend then uptrend (to trigger bullish cross)
    prices = []
    for i in range(50):
        # Downtrend first 50 bars
        prices.append(100 - i*0.3 + np.random.randn()*0.1)
    for i in range(50):
        # Strong uptrend next 50 bars
        prices.append(85 + i*0.8 + np.random.randn()*0.1)

    data = {
        'timestamp': dates,
        'open': [p + np.random.randn()*0.1 for p in prices],
        'high': [p + abs(np.random.randn()*0.3) for p in prices],
        'low': [p - abs(np.random.randn()*0.3) for p in prices],
        'close': prices,
        'volume': [2000000 + np.random.randint(-500000, 500000) for _ in range(bars)]
    }

    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    return df

def debug_ema_strategy():
    """Debug EMA Cross Strategy"""
    print("="*60)
    print("DEBUGGING EMA CROSS STRATEGY")
    print("="*60)

    data = create_crossover_data()
    strategy = EMACrossStrategy(config['strategies']['ema_cross'])

    # Analyze
    analyzed = strategy.analyze(data)

    # Check last few bars
    print("\nLast 5 bars analysis:")
    cols = ['close', 'ema_20', 'ema_50', 'rsi', 'relative_volume', 'macd', 'macd_signal', 'trend']
    print(analyzed[cols].tail(5).to_string())

    # Check for crossover manually
    print("\n\nChecking for EMA crossover:")
    for i in range(-5, 0):
        current = analyzed.iloc[i]
        previous = analyzed.iloc[i-1]

        fast_col = f'ema_{strategy.fast_ema}'
        slow_col = f'ema_{strategy.slow_ema}'

        current_fast = current[fast_col]
        current_slow = current[slow_col]
        prev_fast = previous[fast_col]
        prev_slow = previous[slow_col]

        print(f"\n  Bar {i}:")
        print(f"    Previous: Fast={prev_fast:.2f}, Slow={prev_slow:.2f}")
        print(f"    Current:  Fast={current_fast:.2f}, Slow={current_slow:.2f}")

        # Check bullish cross
        if prev_fast <= prev_slow and current_fast > current_slow:
            print("    >>> BULLISH CROSS DETECTED!")

            # Check filters
            print(f"\n    Filter checks:")
            print(f"      RSI: {current['rsi']:.1f} (overbought > {strategy.rsi_overbought})")
            print(f"      Volume: {current.get('relative_volume', 1.0):.2f}x (threshold: {strategy.volume_threshold}x)")
            print(f"      Price vs EMA50: {current['close']:.2f} vs {current['ema_50']:.2f}")
            print(f"      MACD: {current['macd']:.3f} vs Signal: {current['macd_signal']:.3f}")

            # Determine pass/fail for each filter
            rsi_pass = current['rsi'] <= strategy.rsi_overbought
            volume_pass = current.get('relative_volume', 1.0) >= strategy.volume_threshold
            ema50_pass = current['close'] >= current['ema_50']
            macd_pass = current['macd'] >= current['macd_signal']

            print(f"\n    Filter Results:")
            print(f"      RSI not overbought: {'PASS' if rsi_pass else 'FAIL'}")
            print(f"      Volume sufficient: {'PASS' if volume_pass else 'FAIL'}")
            print(f"      Price above EMA50: {'PASS' if ema50_pass else 'FAIL'}")
            print(f"      MACD bullish: {'PASS' if macd_pass else 'FAIL'}")

            all_pass = rsi_pass and volume_pass and ema50_pass and macd_pass
            print(f"\n    >>> {'SIGNAL WOULD BE GENERATED' if all_pass else 'SIGNAL BLOCKED'}")

    # Try to generate signals
    signals = strategy.generate_signals(analyzed)
    print(f"\n\nActual signals generated: {len(signals)}")

def debug_vwap_strategy():
    """Debug VWAP Strategy"""
    print("\n\n" + "="*60)
    print("DEBUGGING VWAP STRATEGY")
    print("="*60)

    data = create_crossover_data()
    strategy = VWAPStrategy(config['strategies']['vwap'])

    # Analyze
    analyzed = strategy.analyze(data)

    # Check last few bars
    print("\nLast 5 bars analysis:")
    cols = ['close', 'vwap', 'vwap_distance_pct', 'relative_volume', 'rsi', 'trend']
    print(analyzed[cols].tail(5).to_string())

    # Check for crossover manually
    print("\n\nChecking for VWAP crossover:")
    for i in range(-5, 0):
        current = analyzed.iloc[i]
        previous = analyzed.iloc[i-1]

        current_price = current['close']
        current_vwap = current['vwap']
        prev_price = previous['close']
        prev_vwap = previous['vwap']

        print(f"\n  Bar {i}:")
        print(f"    Previous: Price={prev_price:.2f}, VWAP={prev_vwap:.2f}")
        print(f"    Current:  Price={current_price:.2f}, VWAP={current_vwap:.2f}")

        # Check bullish cross
        if prev_price <= prev_vwap and current_price > current_vwap:
            print("    >>> BULLISH VWAP CROSS DETECTED!")

            distance_pct = abs(current['vwap_distance_pct'])

            print(f"\n    Filter checks:")
            print(f"      Distance: {distance_pct:.2f}% (min: {strategy.min_distance_percent}%, max: {strategy.max_distance_percent}%)")
            print(f"      Volume: {current.get('relative_volume', 1.0):.2f}x (threshold: {strategy.volume_threshold}x)")
            print(f"      RSI: {current['rsi']:.1f} (overbought > 70)")
            print(f"      Trend: {current['trend']}")

            # Determine pass/fail
            distance_pass = strategy.min_distance_percent <= distance_pct <= strategy.max_distance_percent
            volume_pass = current.get('relative_volume', 1.0) >= strategy.volume_threshold
            rsi_pass = current['rsi'] <= 70

            print(f"\n    Filter Results:")
            print(f"      Distance OK: {'PASS' if distance_pass else 'FAIL'}")
            print(f"      Volume sufficient: {'PASS' if volume_pass else 'FAIL'}")
            print(f"      RSI not overbought: {'PASS' if rsi_pass else 'FAIL'}")

            all_pass = distance_pass and volume_pass and rsi_pass
            print(f"\n    >>> {'SIGNAL WOULD BE GENERATED' if all_pass else 'SIGNAL BLOCKED'}")

    # Try to generate signals
    signals = strategy.generate_signals(analyzed)
    print(f"\n\nActual signals generated: {len(signals)}")

if __name__ == "__main__":
    debug_ema_strategy()
    debug_vwap_strategy()
