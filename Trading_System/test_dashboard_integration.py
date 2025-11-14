"""
Integration Test for Dashboard with SignalAggregator
====================================================

Verifies that SimpleLiveDashboard properly integrates with the new
modular SignalAggregator component.

Phase 2, Task 2.1: Dashboard Refactoring - Integration Test
Author: Claude AI
Date: 2025-11-11
"""

import unittest
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np


class TestDashboardIntegration(unittest.TestCase):
    """Integration tests for Dashboard + SignalAggregator"""

    @patch('simple_live_dashboard.yaml.safe_load')
    @patch('builtins.open')
    def test_dashboard_initialization_with_signal_aggregator(self, mock_open, mock_yaml):
        """Test 1: Dashboard initializes SignalAggregator correctly"""
        print("\n=== Test 1: Dashboard Initialization with SignalAggregator ===")

        # Mock configuration
        mock_config = {
            'strategies': {
                'vwap': {'enabled': True},
                'Momentum': {'enabled': True},
                'Bollinger_Bands': {'enabled': True},
                'Mean_Reversion': {'enabled': True},
                'Pairs_Trading': {'enabled': True},
                'rsi_divergence': {'enabled': True},
                'advanced_volume_breakout': {'enabled': True}
            }
        }
        mock_yaml.return_value = mock_config

        # Import and create dashboard
        import simple_live_dashboard
        dashboard = simple_live_dashboard.SimpleLiveDashboard()

        # Verify SignalAggregator was initialized
        self.assertTrue(hasattr(dashboard, 'signal_aggregator'))
        self.assertIsNotNone(dashboard.signal_aggregator)

        print("[PASS] SignalAggregator initialized in dashboard")
        print(f"  - Signal Aggregator: {dashboard.signal_aggregator}")
        print(f"  - Signal Threshold: {dashboard.signal_aggregator.signal_threshold}")

    @patch('simple_live_dashboard.yaml.safe_load')
    @patch('builtins.open')
    def test_signal_aggregator_integration(self, mock_open, mock_yaml):
        """Test 2: SignalAggregator is used for signal calculation"""
        print("\n=== Test 2: SignalAggregator Integration ===")

        # Mock configuration
        mock_config = {
            'strategies': {
                'vwap': {'enabled': True},
                'Momentum': {'enabled': True},
                'Bollinger_Bands': {'enabled': True},
                'Mean_Reversion': {'enabled': True},
                'Pairs_Trading': {'enabled': True},
                'rsi_divergence': {'enabled': True},
                'advanced_volume_breakout': {'enabled': True}
            }
        }
        mock_yaml.return_value = mock_config

        # Import and create dashboard
        import simple_live_dashboard
        dashboard = simple_live_dashboard.SimpleLiveDashboard()

        # Verify signal aggregator has all strategies
        self.assertEqual(len(dashboard.signal_aggregator.strategies), 7)

        # Verify strategies are accessible
        self.assertIn('vwap', dashboard.signal_aggregator.strategies)
        self.assertIn('momentum', dashboard.signal_aggregator.strategies)
        self.assertIn('rsi_divergence', dashboard.signal_aggregator.strategies)

        print("[PASS] Signal Aggregator has all strategies")
        print(f"  - Strategies: {list(dashboard.signal_aggregator.strategies.keys())}")

    @patch('simple_live_dashboard.yaml.safe_load')
    @patch('builtins.open')
    def test_prepare_signal_data_integration(self, mock_open, mock_yaml):
        """Test 3: prepare_signal_data works through aggregator"""
        print("\n=== Test 3: prepare_signal_data Integration ===")

        # Mock configuration
        mock_config = {
            'strategies': {
                'vwap': {'enabled': True},
                'Momentum': {'enabled': True},
                'Bollinger_Bands': {'enabled': True},
                'Mean_Reversion': {'enabled': True},
                'Pairs_Trading': {'enabled': True},
                'rsi_divergence': {'enabled': True},
                'advanced_volume_breakout': {'enabled': True}
            }
        }
        mock_yaml.return_value = mock_config

        # Import and create dashboard
        import simple_live_dashboard
        dashboard = simple_live_dashboard.SimpleLiveDashboard()

        # Call prepare_signal_data
        signal_data = dashboard.signal_aggregator.prepare_signal_data('AAPL', 'long')

        self.assertIsNotNone(signal_data)
        self.assertEqual(signal_data['signal_count'], 4)
        self.assertIn('signals', signal_data)

        print("[PASS] prepare_signal_data works correctly")
        print(f"  - Signal count: {signal_data['signal_count']}")
        print(f"  - Signals: {list(signal_data['signals'].keys())}")

    @patch('simple_live_dashboard.yaml.safe_load')
    @patch('builtins.open')
    def test_calculate_confidence_integration(self, mock_open, mock_yaml):
        """Test 4: calculate_base_confidence works through aggregator"""
        print("\n=== Test 4: calculate_base_confidence Integration ===")

        # Mock configuration
        mock_config = {
            'strategies': {
                'vwap': {'enabled': True},
                'Momentum': {'enabled': True},
                'Bollinger_Bands': {'enabled': True},
                'Mean_Reversion': {'enabled': True},
                'Pairs_Trading': {'enabled': True},
                'rsi_divergence': {'enabled': True},
                'advanced_volume_breakout': {'enabled': True}
            }
        }
        mock_yaml.return_value = mock_config

        # Import and create dashboard
        import simple_live_dashboard
        dashboard = simple_live_dashboard.SimpleLiveDashboard()

        # Prepare signal data and calculate confidence
        signal_data = dashboard.signal_aggregator.prepare_signal_data('AAPL', 'long')
        confidence = dashboard.signal_aggregator.calculate_base_confidence(signal_data)

        self.assertIsNotNone(confidence)
        self.assertGreaterEqual(confidence, 0.65)
        self.assertLessEqual(confidence, 0.95)

        print("[PASS] calculate_base_confidence works correctly")
        print(f"  - Confidence: {confidence:.2f}")


def run_integration_tests():
    """Run all integration tests"""
    print("\n" + "="*80)
    print("DASHBOARD INTEGRATION TEST SUITE")
    print("Phase 2, Task 2.1: SignalAggregator Integration")
    print("="*80)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDashboardIntegration)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*80)
    print("INTEGRATION TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n[SUCCESS] All integration tests passed!")
        return 0
    else:
        print("\n[FAILURE] Some integration tests failed")
        return 1


if __name__ == '__main__':
    exit(run_integration_tests())
