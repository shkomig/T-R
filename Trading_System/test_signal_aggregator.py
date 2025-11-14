"""
Unit Tests for SignalAggregator
================================

Comprehensive test suite for the SignalAggregator module.

Phase 2, Task 2.1: Dashboard Refactoring - SignalAggregator Tests
Author: Claude AI
Date: 2025-11-11
"""

import unittest
import pandas as pd
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from Trading_Dashboard.core.signal_aggregator import SignalAggregator


class TestSignalAggregator(unittest.TestCase):
    """Test suite for SignalAggregator class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create mock strategy instances
        self.mock_strategies = {
            'vwap': Mock(),
            'momentum': Mock(),
            'bollinger': Mock(),
            'mean_reversion': Mock(),
            'pairs_trading': Mock(),
            'rsi_divergence': Mock(),
            'volume_breakout': Mock()
        }

        # Active strategies configuration
        self.active_strategies = {
            'vwap': True,
            'momentum': True,
            'bollinger': True,
            'mean_reversion': True,
            'pairs_trading': True,
            'rsi_divergence': True,
            'volume_breakout': True
        }

        # Create SignalAggregator instance
        self.aggregator = SignalAggregator(
            strategies=self.mock_strategies,
            active_strategies=self.active_strategies,
            signal_threshold=2
        )

        # Create test DataFrame
        self.test_df = pd.DataFrame({
            'timestamp': pd.date_range('2025-01-01', periods=100, freq='1min'),
            'open': np.random.uniform(100, 110, 100),
            'high': np.random.uniform(110, 120, 100),
            'low': np.random.uniform(90, 100, 100),
            'close': np.random.uniform(100, 110, 100),
            'volume': np.random.uniform(1000, 5000, 100)
        })

    def test_initialization(self):
        """Test 1: SignalAggregator initialization"""
        print("\n=== Test 1: Initialization ===")

        self.assertEqual(len(self.aggregator.strategies), 7)
        self.assertEqual(self.aggregator.signal_threshold, 2)
        self.assertEqual(len(self.aggregator.active_strategies), 7)

        print("[PASS] SignalAggregator initialized correctly")
        print(f"  - Strategies loaded: {len(self.aggregator.strategies)}")
        print(f"  - Signal threshold: {self.aggregator.signal_threshold}")

    def test_get_session_strategies_regular(self):
        """Test 2: Get strategies for regular trading session"""
        print("\n=== Test 2: Get Session Strategies (Regular) ===")

        strategies = self.aggregator.get_session_strategies("regular")

        self.assertIsInstance(strategies, list)
        self.assertIn("VWAP", strategies)
        self.assertIn("Momentum", strategies)
        self.assertIn("Pairs Trading", strategies)

        print("[PASS] Regular session strategies returned correctly")
        print(f"  - Strategies: {strategies}")

    def test_get_session_strategies_extended_hours(self):
        """Test 3: Get strategies for extended hours"""
        print("\n=== Test 3: Get Session Strategies (Extended Hours) ===")

        pre_market = self.aggregator.get_session_strategies("PRE-MARKET")
        after_hours = self.aggregator.get_session_strategies("AFTER-HOURS")

        self.assertIn("VWAP", pre_market)
        self.assertIn("Volume Breakout", pre_market)
        self.assertEqual(pre_market, after_hours)  # Should be same for both

        print("[PASS] Extended hours strategies returned correctly")
        print(f"  - Pre-Market: {pre_market}")
        print(f"  - After-Hours: {after_hours}")

    def test_aggregate_signals_long_consensus(self):
        """Test 4: Aggregate signals with long consensus"""
        print("\n=== Test 4: Aggregate Signals (Long Consensus) ===")

        signals = {
            'vwap': {'signal': 'long'},
            'momentum': {'signal': 'long'},
            'bollinger': {'signal': 'hold'},
            'mean_reversion': {'signal': 'long'}
        }

        result = self.aggregator.aggregate_signals(signals)

        self.assertEqual(result, 'long')
        print("[PASS] Long consensus detected correctly")
        print(f"  - Input: 3 long, 1 hold")
        print(f"  - Output: {result}")

    def test_aggregate_signals_exit_consensus(self):
        """Test 5: Aggregate signals with exit consensus"""
        print("\n=== Test 5: Aggregate Signals (Exit Consensus) ===")

        signals = {
            'vwap': {'signal': 'exit'},
            'momentum': {'signal': 'exit'},
            'bollinger': {'signal': 'hold'},
            'mean_reversion': {'signal': 'hold'}
        }

        result = self.aggregator.aggregate_signals(signals)

        self.assertEqual(result, 'exit')
        print("[PASS] Exit consensus detected correctly")
        print(f"  - Input: 2 exit, 2 hold")
        print(f"  - Output: {result}")

    def test_aggregate_signals_no_consensus(self):
        """Test 6: Aggregate signals with no consensus"""
        print("\n=== Test 6: Aggregate Signals (No Consensus) ===")

        signals = {
            'vwap': {'signal': 'long'},
            'momentum': {'signal': 'exit'},
            'bollinger': {'signal': 'hold'},
            'mean_reversion': {'signal': 'hold'}
        }

        result = self.aggregator.aggregate_signals(signals)

        self.assertEqual(result, 'hold')
        print("[PASS] No consensus defaults to hold")
        print(f"  - Input: 1 long, 1 exit, 2 hold")
        print(f"  - Output: {result}")

    def test_prepare_signal_data_long(self):
        """Test 7: Prepare signal data for long signal"""
        print("\n=== Test 7: Prepare Signal Data (Long) ===")

        signal_data = self.aggregator.prepare_signal_data('AAPL', 'long')

        self.assertEqual(signal_data['signal_count'], 4)
        self.assertEqual(signal_data['total_strategies'], 7)
        self.assertEqual(signal_data['momentum_score'], 1.8)
        self.assertIn('momentum', signal_data['signals'])

        print("[PASS] Long signal data prepared correctly")
        print(f"  - Signal count: {signal_data['signal_count']}")
        print(f"  - Momentum score: {signal_data['momentum_score']}")

    def test_prepare_signal_data_exit(self):
        """Test 8: Prepare signal data for exit signal"""
        print("\n=== Test 8: Prepare Signal Data (Exit) ===")

        signal_data = self.aggregator.prepare_signal_data('AAPL', 'exit')

        self.assertEqual(signal_data['signal_count'], 2)
        self.assertIn('risk_management', signal_data['signals'])

        print("[PASS] Exit signal data prepared correctly")
        print(f"  - Signal count: {signal_data['signal_count']}")
        print(f"  - Signals: {list(signal_data['signals'].keys())}")

    def test_calculate_base_confidence_high(self):
        """Test 9: Calculate confidence with high agreement"""
        print("\n=== Test 9: Calculate Base Confidence (High) ===")

        signal_data = {
            'signal_count': 5,
            'total_strategies': 7,
            'momentum_score': 1.8,
            'volume_confirmation': 1.5
        }

        confidence = self.aggregator.calculate_base_confidence(signal_data)

        self.assertGreaterEqual(confidence, 0.80)
        self.assertLessEqual(confidence, 0.95)

        print("[PASS] High confidence calculated correctly")
        print(f"  - Input: 5/7 strategies, momentum=1.8")
        print(f"  - Confidence: {confidence:.2f}")

    def test_calculate_base_confidence_low(self):
        """Test 10: Calculate confidence with low agreement"""
        print("\n=== Test 10: Calculate Base Confidence (Low) ===")

        signal_data = {
            'signal_count': 1,
            'total_strategies': 7,
            'momentum_score': 1.0,
            'volume_confirmation': 1.0
        }

        confidence = self.aggregator.calculate_base_confidence(signal_data)

        self.assertGreaterEqual(confidence, 0.65)
        self.assertLess(confidence, 0.75)

        print("[PASS] Low confidence calculated correctly")
        print(f"  - Input: 1/7 strategies, momentum=1.0")
        print(f"  - Confidence: {confidence:.2f}")

    def test_calculate_base_confidence_no_data(self):
        """Test 11: Calculate confidence with no data"""
        print("\n=== Test 11: Calculate Base Confidence (No Data) ===")

        confidence = self.aggregator.calculate_base_confidence(None)

        self.assertEqual(confidence, 0.75)

        print("[PASS] Default confidence returned when no data")
        print(f"  - Confidence: {confidence:.2f}")

    def test_collect_signals_success(self):
        """Test 12: Collect signals from all strategies successfully"""
        print("\n=== Test 12: Collect Signals (Success) ===")

        # Mock signal objects
        mock_signal_long = Mock()
        mock_signal_long.signal_type = 'SignalType.LONG'
        mock_signal_long.data = {'vwap': 105.0}

        mock_signal_exit = Mock()
        mock_signal_exit.signal_type = 'SignalType.EXIT'

        # Configure mocks
        self.mock_strategies['vwap'].generate_signals.return_value = [mock_signal_long]
        self.mock_strategies['momentum'].generate_signals.return_value = [mock_signal_long]
        self.mock_strategies['bollinger'].generate_signals.return_value = [mock_signal_exit]
        self.mock_strategies['mean_reversion'].generate_signals.return_value = [mock_signal_long]

        # Configure pairs trading (has pair_symbols attribute)
        self.mock_strategies['pairs_trading'].pair_symbols = ['AAPL', 'MSFT']
        self.mock_strategies['pairs_trading'].generate_signals.return_value = [mock_signal_long]

        # Configure RSI and Volume Breakout
        mock_rsi_signal = Mock()
        mock_rsi_signal.signal_type = Mock(value='BUY')
        self.mock_strategies['rsi_divergence'].generate_signals.return_value = [mock_rsi_signal]

        mock_breakout_signal = Mock()
        mock_breakout_signal.signal_type = Mock(value='BUY')
        self.mock_strategies['volume_breakout'].generate_signals.return_value = [mock_breakout_signal]

        # Collect signals
        signals = self.aggregator.collect_signals(self.test_df, 'AAPL')

        self.assertIsNotNone(signals)
        self.assertIn('vwap', signals)
        self.assertIn('momentum', signals)
        self.assertEqual(signals['vwap']['signal'], 'long')
        self.assertEqual(signals['momentum']['signal'], 'long')

        print("[PASS] Signals collected successfully from all strategies")
        print(f"  - Strategies processed: {len(signals)}")
        print(f"  - VWAP signal: {signals['vwap']['signal']}")
        print(f"  - Momentum signal: {signals['momentum']['signal']}")

    def test_collect_signals_strategy_failure(self):
        """Test 13: Collect signals with strategy failure"""
        print("\n=== Test 13: Collect Signals (Strategy Failure) ===")

        # Configure VWAP to raise exception
        self.mock_strategies['vwap'].generate_signals.side_effect = Exception("Strategy failed")

        # Attempt to collect signals
        signals = self.aggregator.collect_signals(self.test_df, 'AAPL')

        self.assertIsNone(signals)  # Should return None on strategy failure

        print("[PASS] Strategy failure handled correctly")
        print(f"  - Result: {signals} (expected None)")

    def test_calculate_combined_signal_long(self):
        """Test 14: Calculate combined signal with long consensus"""
        print("\n=== Test 14: Calculate Combined Signal (Long) ===")

        # Mock signal objects
        mock_signal_long = Mock()
        mock_signal_long.signal_type = 'SignalType.LONG'
        mock_signal_long.data = {}

        # Configure strategies to return long signals
        for strategy_name, strategy in self.mock_strategies.items():
            if strategy_name == 'pairs_trading':
                strategy.pair_symbols = ['AAPL']
            strategy.generate_signals.return_value = [mock_signal_long]

        # Calculate combined signal
        signals, combined = self.aggregator.calculate_combined_signal(self.test_df, 'AAPL')

        self.assertIsNotNone(signals)
        self.assertEqual(combined, 'long')

        print("[PASS] Combined long signal calculated correctly")
        print(f"  - Combined signal: {combined}")

    def test_calculate_combined_signal_hold(self):
        """Test 15: Calculate combined signal with no consensus"""
        print("\n=== Test 15: Calculate Combined Signal (Hold) ===")

        # Mock signal objects - mixed signals
        mock_signal_long = Mock()
        mock_signal_long.signal_type = 'SignalType.LONG'
        mock_signal_long.data = {}

        mock_signal_hold = Mock()
        mock_signal_hold.signal_type = 'SignalType.HOLD'
        mock_signal_hold.data = {}

        # Configure strategies with mixed signals
        self.mock_strategies['vwap'].generate_signals.return_value = [mock_signal_long]
        self.mock_strategies['momentum'].generate_signals.return_value = [mock_signal_hold]
        self.mock_strategies['bollinger'].generate_signals.return_value = [mock_signal_hold]
        self.mock_strategies['mean_reversion'].generate_signals.return_value = [mock_signal_hold]

        # Pairs trading
        self.mock_strategies['pairs_trading'].pair_symbols = ['AAPL']
        self.mock_strategies['pairs_trading'].generate_signals.return_value = [mock_signal_hold]

        # RSI and Volume Breakout
        mock_rsi_signal = Mock()
        mock_rsi_signal.signal_type = Mock(value='HOLD')
        self.mock_strategies['rsi_divergence'].generate_signals.return_value = [mock_rsi_signal]

        mock_breakout_signal = Mock()
        mock_breakout_signal.signal_type = Mock(value='HOLD')
        self.mock_strategies['volume_breakout'].generate_signals.return_value = [mock_breakout_signal]

        # Calculate combined signal
        signals, combined = self.aggregator.calculate_combined_signal(self.test_df, 'AAPL')

        self.assertEqual(combined, 'hold')  # Only 1 long vote, threshold is 2

        print("[PASS] Combined hold signal (no consensus) calculated correctly")
        print(f"  - Combined signal: {combined}")


    def test_signal_threshold_enforcement(self):
        """Test 16: Signal threshold is enforced correctly"""
        print("\n=== Test 16: Signal Threshold Enforcement ===")

        # Create aggregator with threshold of 3
        aggregator_high_threshold = SignalAggregator(
            strategies=self.mock_strategies,
            active_strategies=self.active_strategies,
            signal_threshold=3
        )

        # Only 2 long votes - should not trigger with threshold=3
        signals = {
            'vwap': {'signal': 'long'},
            'momentum': {'signal': 'long'},
            'bollinger': {'signal': 'hold'}
        }

        result = aggregator_high_threshold.aggregate_signals(signals)

        self.assertEqual(result, 'hold')  # Not enough votes

        print("[PASS] Signal threshold enforced correctly")
        print(f"  - Threshold: 3, Long votes: 2")
        print(f"  - Result: {result} (expected hold)")


def run_tests():
    """Run all tests and print summary"""
    print("\n" + "="*80)
    print("SIGNAL AGGREGATOR TEST SUITE")
    print("Phase 2, Task 2.1: Dashboard Refactoring")
    print("="*80)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSignalAggregator)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print("\n[FAILURE] Some tests failed")
        return 1


if __name__ == '__main__':
    exit(run_tests())
