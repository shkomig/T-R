"""
Test Failure Tracking System - Task 1.6
========================================

Comprehensive tests for failure tracking, emergency halt integration,
and proper error handling without fallbacks.

Author: Claude AI (Phase 1 - Task 1.6)
Date: 2025-11-11
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import time

# Add project root to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from execution.failure_tracker import (
    FailureTracker,
    SignalGenerationFailure,
    FailureType,
    get_failure_tracker
)


def test_initialization():
    """Test 1: Failure Tracker Initialization"""
    print("\n" + "="*80)
    print("TEST 1: Failure Tracker Initialization")
    print("="*80)

    tracker = FailureTracker(failure_threshold=3)

    print(f"Tracker created: {tracker is not None}")
    print(f"Consecutive failures: {tracker.consecutive_failures}")
    print(f"Failure threshold: {tracker.failure_threshold}")
    print(f"Halt triggered: {tracker.halt_triggered}")

    assert tracker is not None, "Tracker should be created"
    assert tracker.consecutive_failures == 0, "Should start with 0 failures"
    assert tracker.failure_threshold == 3, "Threshold should be 3"
    assert not tracker.halt_triggered, "Should not be halted initially"

    print("\n[PASS] TEST PASSED: Initialization successful!")
    return True


def test_record_single_failure():
    """Test 2: Record single failure"""
    print("\n" + "="*80)
    print("TEST 2: Record Single Failure")
    print("="*80)

    tracker = FailureTracker(failure_threshold=3)

    try:
        raise ValueError("Test error")
    except Exception as e:
        failure = tracker.record_failure(
            strategy_name="VWAP",
            symbol="AAPL",
            error=e,
            failure_type=FailureType.STRATEGY_ERROR
        )

    print(f"Failure recorded: {failure is not None}")
    print(f"Consecutive failures: {tracker.consecutive_failures}")
    print(f"Total failures: {tracker.total_failures}")
    print(f"Strategy: {failure.strategy_name}")
    print(f"Symbol: {failure.symbol}")

    assert failure is not None, "Failure object should be created"
    assert tracker.consecutive_failures == 1, "Consecutive count should be 1"
    assert tracker.total_failures == 1, "Total count should be 1"
    assert failure.strategy_name == "VWAP"
    assert failure.symbol == "AAPL"
    assert not tracker.halt_triggered, "Should not trigger halt on single failure"

    print("\n[PASS] TEST PASSED: Single failure recorded correctly!")
    return True


def test_multiple_failures_no_halt():
    """Test 3: Multiple failures below threshold"""
    print("\n" + "="*80)
    print("TEST 3: Multiple Failures Below Threshold")
    print("="*80)

    tracker = FailureTracker(failure_threshold=3)

    # Record 2 failures (below threshold of 3)
    for i in range(2):
        try:
            raise ValueError(f"Test error {i+1}")
        except Exception as e:
            tracker.record_failure(
                strategy_name="Momentum",
                symbol="GOOGL",
                error=e
            )

    print(f"Consecutive failures: {tracker.consecutive_failures}")
    print(f"Halt triggered: {tracker.halt_triggered}")

    assert tracker.consecutive_failures == 2, "Should have 2 consecutive failures"
    assert not tracker.halt_triggered, "Should not halt below threshold"

    print("\n[PASS] TEST PASSED: Multiple failures tracked without halt!")
    return True


def test_halt_on_threshold():
    """Test 4: Halt triggered at threshold"""
    print("\n" + "="*80)
    print("TEST 4: Halt Triggered at Threshold")
    print("="*80)

    halt_called = {'called': False, 'reason': None}

    def halt_callback(reason, failure):
        halt_called['called'] = True
        halt_called['reason'] = reason

    tracker = FailureTracker(failure_threshold=3, halt_callback=halt_callback)

    # Record 3 failures to reach threshold
    for i in range(3):
        try:
            raise ValueError(f"Critical error {i+1}")
        except Exception as e:
            tracker.record_failure(
                strategy_name="RSI",
                symbol="MSFT",
                error=e
            )

    print(f"Consecutive failures: {tracker.consecutive_failures}")
    print(f"Halt triggered: {tracker.halt_triggered}")
    print(f"Halt callback called: {halt_called['called']}")
    print(f"Halt reason: {tracker.halt_reason}")

    assert tracker.consecutive_failures == 3, "Should have 3 consecutive failures"
    assert tracker.halt_triggered, "Should trigger halt at threshold"
    assert halt_called['called'], "Halt callback should be called"
    assert "threshold exceeded" in tracker.halt_reason.lower()

    print("\n[PASS] TEST PASSED: Halt triggered correctly at threshold!")
    return True


def test_success_resets_counter():
    """Test 5: Success resets consecutive failure counter"""
    print("\n" + "="*80)
    print("TEST 5: Success Resets Failure Counter")
    print("="*80)

    tracker = FailureTracker(failure_threshold=3)

    # Record 2 failures
    for i in range(2):
        try:
            raise ValueError(f"Error {i+1}")
        except Exception as e:
            tracker.record_failure("Strategy", "AAPL", e)

    print(f"Consecutive failures before success: {tracker.consecutive_failures}")

    # Record success
    tracker.record_success("Strategy", "AAPL")

    print(f"Consecutive failures after success: {tracker.consecutive_failures}")
    print(f"Total failures (unchanged): {tracker.total_failures}")

    assert tracker.consecutive_failures == 0, "Consecutive should reset to 0"
    assert tracker.total_failures == 2, "Total should not change"

    print("\n[PASS] TEST PASSED: Success resets consecutive counter!")
    return True


def test_signal_generation_failure_class():
    """Test 6: SignalGenerationFailure class"""
    print("\n" + "="*80)
    print("TEST 6: SignalGenerationFailure Class")
    print("="*80)

    try:
        raise ValueError("Test error for failure class")
    except Exception as e:
        failure = SignalGenerationFailure(
            strategy_name="VWAP",
            symbol="AAPL",
            error_message=str(e),
            failure_type=FailureType.STRATEGY_ERROR,
            additional_context={'data_points': 100, 'timeframe': '5m'}
        )

    print(f"Failure created: {failure is not None}")
    print(f"Strategy: {failure.strategy_name}")
    print(f"Symbol: {failure.symbol}")
    print(f"Type: {failure.failure_type.value}")
    print(f"Context: {failure.additional_context}")

    assert failure is not None, "Failure object should be created"
    assert failure.strategy_name == "VWAP"
    assert failure.symbol == "AAPL"
    assert failure.failure_type == FailureType.STRATEGY_ERROR
    assert 'data_points' in failure.additional_context

    # Test to_dict conversion
    failure_dict = failure.to_dict()
    assert 'strategy' in failure_dict
    assert 'error' in failure_dict
    assert 'timestamp' in failure_dict

    print("\n[PASS] TEST PASSED: SignalGenerationFailure class works!")
    return True


def test_strategy_specific_tracking():
    """Test 7: Strategy-specific failure tracking"""
    print("\n" + "="*80)
    print("TEST 7: Strategy-Specific Failure Tracking")
    print("="*80)

    tracker = FailureTracker(failure_threshold=5)

    # Record failures for different strategies
    strategies = [
        ("VWAP", "AAPL", 3),
        ("Momentum", "GOOGL", 2),
        ("RSI", "MSFT", 1)
    ]

    for strategy, symbol, count in strategies:
        for i in range(count):
            try:
                raise ValueError(f"{strategy} error {i+1}")
            except Exception as e:
                tracker.record_failure(strategy, symbol, e)

    print(f"Total failures: {tracker.total_failures}")
    print("Strategy-specific counts:")
    for strategy, count in tracker.strategy_failures.items():
        print(f"  {strategy}: {count}")

    assert tracker.total_failures == 6, "Should have 6 total failures"
    assert tracker.strategy_failures["VWAP"] == 3
    assert tracker.strategy_failures["Momentum"] == 2
    assert tracker.strategy_failures["RSI"] == 1

    print("\n[PASS] TEST PASSED: Strategy-specific tracking works!")
    return True


def test_symbol_specific_tracking():
    """Test 8: Symbol-specific failure tracking"""
    print("\n" + "="*80)
    print("TEST 8: Symbol-Specific Failure Tracking")
    print("="*80)

    tracker = FailureTracker(failure_threshold=5)

    # Record failures for different symbols
    symbols = ["AAPL", "GOOGL", "MSFT", "AAPL", "AAPL"]

    for symbol in symbols:
        try:
            raise ValueError(f"Error for {symbol}")
        except Exception as e:
            tracker.record_failure("Strategy", symbol, e)

    print(f"Total failures: {tracker.total_failures}")
    print("Symbol-specific counts:")
    for symbol, count in tracker.symbol_failures.items():
        print(f"  {symbol}: {count}")

    assert tracker.symbol_failures["AAPL"] == 3
    assert tracker.symbol_failures["GOOGL"] == 1
    assert tracker.symbol_failures["MSFT"] == 1

    print("\n[PASS] TEST PASSED: Symbol-specific tracking works!")
    return True


def test_failure_history():
    """Test 9: Failure history tracking"""
    print("\n" + "="*80)
    print("TEST 9: Failure History Tracking")
    print("="*80)

    tracker = FailureTracker(failure_threshold=5)

    # Record 5 failures
    for i in range(5):
        try:
            raise ValueError(f"Historical error {i+1}")
        except Exception as e:
            tracker.record_failure("Strategy", "AAPL", e)

    print(f"Failure history length: {len(tracker.failure_history)}")
    print(f"Latest failure: {tracker.failure_history[-1].error_message}")

    assert len(tracker.failure_history) == 5, "Should have 5 failures in history"
    assert "Historical error 5" in tracker.failure_history[-1].error_message

    print("\n[PASS] TEST PASSED: Failure history tracked correctly!")
    return True


def test_status_report():
    """Test 10: Status report generation"""
    print("\n" + "="*80)
    print("TEST 10: Status Report Generation")
    print("="*80)

    tracker = FailureTracker(failure_threshold=3)

    # Record some failures
    for i in range(2):
        try:
            raise ValueError(f"Status test error {i+1}")
        except Exception as e:
            tracker.record_failure("TestStrategy", "TEST", e)

    status = tracker.get_status()
    summary = tracker.get_failure_summary()

    print("Status dict keys:", list(status.keys()))
    print(f"Consecutive: {status['consecutive_failures']}")
    print(f"Total: {status['total_failures']}")
    print("\nSummary:")
    print(summary)

    assert 'consecutive_failures' in status
    assert 'total_failures' in status
    assert 'halt_triggered' in status
    assert status['consecutive_failures'] == 2
    assert status['total_failures'] == 2
    assert len(summary) > 0

    print("\n[PASS] TEST PASSED: Status reporting works!")
    return True


def test_manual_reset():
    """Test 11: Manual reset of failure counter"""
    print("\n" + "="*80)
    print("TEST 11: Manual Reset")
    print("="*80)

    tracker = FailureTracker(failure_threshold=3)

    # Record 2 failures
    for i in range(2):
        try:
            raise ValueError(f"Pre-reset error {i+1}")
        except Exception as e:
            tracker.record_failure("Strategy", "AAPL", e)

    print(f"Consecutive before reset: {tracker.consecutive_failures}")

    # Manual reset
    tracker.reset()

    print(f"Consecutive after reset: {tracker.consecutive_failures}")
    print(f"Total failures (unchanged): {tracker.total_failures}")

    assert tracker.consecutive_failures == 0, "Consecutive should be 0 after reset"
    assert tracker.total_failures == 2, "Total should not change"

    print("\n[PASS] TEST PASSED: Manual reset works!")
    return True


def test_singleton_pattern():
    """Test 12: Singleton pattern for failure tracker"""
    print("\n" + "="*80)
    print("TEST 12: Singleton Pattern")
    print("="*80)

    tracker1 = get_failure_tracker(failure_threshold=3)
    tracker2 = get_failure_tracker()

    print(f"Tracker1 id: {id(tracker1)}")
    print(f"Tracker2 id: {id(tracker2)}")
    print(f"Same instance: {tracker1 is tracker2}")

    assert tracker1 is tracker2, "Should return same instance"

    print("\n[PASS] TEST PASSED: Singleton pattern works!")
    return True


def run_all_tests():
    """Run all failure tracker tests"""
    print("\n" + "="*80)
    print("FAILURE TRACKING SYSTEM TEST SUITE - Task 1.6")
    print("="*80)
    print("\nTesting failure tracking, error handling, and emergency halt integration:")
    print("  - SignalGenerationFailure class")
    print("  - Failure counter and tracking")
    print("  - Automatic halt trigger")
    print("  - Success resets")
    print("  - Strategy/symbol-specific tracking")

    tests = [
        ("Initialization", test_initialization),
        ("Record Single Failure", test_record_single_failure),
        ("Multiple Failures Below Threshold", test_multiple_failures_no_halt),
        ("Halt at Threshold", test_halt_on_threshold),
        ("Success Resets Counter", test_success_resets_counter),
        ("SignalGenerationFailure Class", test_signal_generation_failure_class),
        ("Strategy-Specific Tracking", test_strategy_specific_tracking),
        ("Symbol-Specific Tracking", test_symbol_specific_tracking),
        ("Failure History", test_failure_history),
        ("Status Report", test_status_report),
        ("Manual Reset", test_manual_reset),
        ("Singleton Pattern", test_singleton_pattern),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n[FAIL] TEST FAILED: {test_name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n[FAIL] TEST ERROR: {test_name}")
            print(f"   Exception: {e}")
            failed += 1

    # Summary
    print("\n" + "="*80)
    print("TEST SUITE SUMMARY")
    print("="*80)
    print(f"Total Tests: {len(tests)}")
    print(f"[PASS] Passed: {passed}")
    print(f"[FAIL] Failed: {failed}")

    if failed == 0:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        print("\nConclusion:")
        print("  [OK] Failure tracking system working correctly")
        print("  [OK] SignalGenerationFailure class functional")
        print("  [OK] Consecutive failure counter operational")
        print("  [OK] Emergency halt trigger working")
        print("  [OK] Success reset working")
        print("  [OK] Strategy/symbol-specific tracking operational")
        print("  [OK] Status reporting working")
        return True
    else:
        print("\n[WARNING] SOME TESTS FAILED - Review errors above")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
