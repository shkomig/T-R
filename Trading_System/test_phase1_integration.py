"""
Phase 1 Integration Tests - Staging Validation
==============================================

Comprehensive integration tests validating all Phase 1 components
work together correctly in a simulated trading environment.

Tests:
- Risk configuration loading and validation
- Emergency halt integration with risk calculator
- Failure tracker integration with halt system
- Complete trading workflow simulation
- Edge cases and failure scenarios

Author: Claude AI (Phase 1 Validation)
Date: 2025-11-11
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import time

# Add project root to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from risk_management.advanced_risk_calculator import AdvancedRiskCalculator
from risk_management.emergency_halt_manager import EmergencyHaltManager, HaltTrigger
from execution.failure_tracker import FailureTracker, SignalGenerationFailure, FailureType


def cleanup_test_data():
    """Clean up test data files"""
    data_dir = Path(__file__).parent / 'data'
    halt_state_file = data_dir / 'halt_state.json'
    if halt_state_file.exists():
        halt_state_file.unlink()


def test_configuration_loading():
    """Test 1: Risk configuration loads correctly"""
    print("\n" + "="*80)
    print("TEST 1: Risk Configuration Loading")
    print("="*80)

    config_path = script_dir / 'config' / 'risk_management.yaml'

    try:
        risk_calc = AdvancedRiskCalculator(config_path=str(config_path))

        print(f"Config loaded: {risk_calc is not None}")
        print(f"Stop loss percent: {risk_calc.stop_loss_percent}")
        print(f"Max daily loss: {risk_calc.max_daily_loss}")
        print(f"Max drawdown: {risk_calc.max_total_drawdown}")
        print(f"Max portfolio heat: {risk_calc.max_portfolio_heat}")

        assert risk_calc is not None, "Risk calculator should initialize"
        assert risk_calc.stop_loss_percent == 0.03, "Stop loss should be 3%"
        assert risk_calc.max_daily_loss == 0.02, "Max daily loss should be 2%"
        assert risk_calc.max_total_drawdown == 0.10, "Max drawdown should be 10%"
        assert risk_calc.max_portfolio_heat == 0.25, "Max heat should be 25%"

        print("\n[PASS] TEST PASSED: Configuration loaded correctly!")
        return True

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        return False


def test_halt_manager_initialization():
    """Test 2: Emergency halt manager initializes with config"""
    print("\n" + "="*80)
    print("TEST 2: Emergency Halt Manager Initialization")
    print("="*80)

    cleanup_test_data()
    config_path = script_dir / 'config' / 'risk_management.yaml'

    try:
        halt_manager = EmergencyHaltManager(config_path=str(config_path))

        print(f"Halt manager created: {halt_manager is not None}")
        print(f"Initial state: {halt_manager.halt_state['state']}")
        print(f"Config loaded: {halt_manager.config is not None}")
        print(f"Kill switch enabled: {halt_manager.config.get('enable_kill_switch')}")

        assert halt_manager is not None
        assert not halt_manager.is_halted()
        assert halt_manager.config.get('enable_kill_switch') == True

        print("\n[PASS] TEST PASSED: Halt manager initialized correctly!")
        return True

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        return False


def test_risk_halt_integration():
    """Test 3: Risk calculator integrates with halt manager"""
    print("\n" + "="*80)
    print("TEST 3: Risk Calculator + Halt Manager Integration")
    print("="*80)

    cleanup_test_data()
    config_path = script_dir / 'config' / 'risk_management.yaml'

    try:
        risk_calc = AdvancedRiskCalculator(config_path=str(config_path))
        halt_manager = EmergencyHaltManager(config_path=str(config_path))

        # Simulate excessive drawdown
        # First establish peak balance by calling with high balance
        peak_balance = 120000.0
        positions = {}
        _ = risk_calc.calculate_risk_metrics(peak_balance, positions)  # Establish peak

        # Now with lower balance (16.67% drawdown)
        balance = 100000.0

        # Calculate risk metrics with lower balance
        risk_metrics = risk_calc.calculate_risk_metrics(balance, positions)

        print(f"Current drawdown: {risk_metrics['current_drawdown']:.2%}")
        print(f"Safe to trade: {risk_metrics['is_safe_to_trade']}")

        # Check if should halt
        should_halt, reason, trigger = halt_manager.check_halt_conditions(risk_metrics)

        print(f"Should halt: {should_halt}")
        if should_halt:
            print(f"Halt reason: {reason}")
            print(f"Trigger type: {trigger}")

        # 16.67% drawdown should trigger halt (> 15% threshold)
        assert should_halt, "Should trigger halt on excessive drawdown"
        assert trigger == HaltTrigger.DRAWDOWN.value

        print("\n[PASS] TEST PASSED: Risk/halt integration working!")
        return True

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        return False


def test_failure_tracker_halt_integration():
    """Test 4: Failure tracker triggers emergency halt"""
    print("\n" + "="*80)
    print("TEST 4: Failure Tracker + Halt Manager Integration")
    print("="*80)

    cleanup_test_data()

    halt_triggered = {'triggered': False, 'reason': None}

    def halt_callback(reason, failure):
        halt_triggered['triggered'] = True
        halt_triggered['reason'] = reason
        print(f"[HALT] Halt callback triggered: {reason}")

    try:
        failure_tracker = FailureTracker(
            failure_threshold=3,
            halt_callback=halt_callback
        )

        print("Recording 3 consecutive failures...")

        # Simulate 3 consecutive strategy failures
        for i in range(3):
            try:
                raise ValueError(f"Strategy failure {i+1}")
            except Exception as e:
                failure = failure_tracker.record_failure(
                    strategy_name="TestStrategy",
                    symbol="TEST",
                    error=e,
                    failure_type=FailureType.STRATEGY_ERROR
                )
                print(f"  Failure {i+1} recorded, consecutive: {failure_tracker.consecutive_failures}")

        print(f"\nHalt callback triggered: {halt_triggered['triggered']}")
        print(f"Halt reason: {halt_triggered['reason']}")

        assert halt_triggered['triggered'], "Halt callback should be triggered"
        assert "threshold exceeded" in halt_triggered['reason'].lower()

        print("\n[PASS] TEST PASSED: Failure tracker triggers halt correctly!")
        return True

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        return False


def test_complete_trading_workflow():
    """Test 5: Complete trading workflow simulation"""
    print("\n" + "="*80)
    print("TEST 5: Complete Trading Workflow Simulation")
    print("="*80)

    cleanup_test_data()
    config_path = script_dir / 'config' / 'risk_management.yaml'

    try:
        # Initialize all components
        risk_calc = AdvancedRiskCalculator(config_path=str(config_path))
        halt_manager = EmergencyHaltManager(config_path=str(config_path))

        def halt_callback(reason, failure):
            halt_manager.trigger_halt(
                reason=f"Strategy failures: {reason}",
                trigger_type=HaltTrigger.TECHNICAL_FAILURE.value
            )

        failure_tracker = FailureTracker(
            failure_threshold=3,
            halt_callback=halt_callback
        )

        print("\n1. Starting with normal trading conditions...")
        balance = 100000.0
        positions = {
            'AAPL': {'quantity': 50, 'entry_price': 180.0, 'current_price': 185.0}
        }

        # Calculate risk
        risk_metrics = risk_calc.calculate_risk_metrics(balance, positions)
        print(f"   Portfolio heat: {risk_metrics['portfolio_heat']:.2%}")
        print(f"   Safe to trade: {risk_metrics['is_safe_to_trade']}")

        # Check halt conditions
        should_halt, _, _ = halt_manager.check_halt_conditions(risk_metrics)
        print(f"   Should halt: {should_halt}")

        assert not should_halt, "Should not halt on normal conditions"
        assert risk_metrics['is_safe_to_trade'], "Should be safe to trade"

        print("\n2. Simulating successful strategy execution...")
        failure_tracker.record_success("VWAP", "AAPL")
        print(f"   Consecutive failures: {failure_tracker.consecutive_failures}")

        assert failure_tracker.consecutive_failures == 0

        print("\n3. Simulating market downturn (excessive drawdown)...")
        # Set peak balance first
        risk_calc.peak_balance = 100000.0

        # Now balance drops to 85000 (15% loss from peak)
        balance_after_loss = 85000.0

        risk_metrics = risk_calc.calculate_risk_metrics(balance_after_loss, positions)
        print(f"   Current drawdown: {risk_metrics['current_drawdown']:.2%}")

        should_halt, reason, trigger = halt_manager.check_halt_conditions(risk_metrics)
        print(f"   Should halt: {should_halt}")
        print(f"   Reason: {reason}")

        if should_halt:
            halt_manager.trigger_halt(reason, trigger)

        assert should_halt, "Should halt on excessive drawdown"
        assert halt_manager.is_halted(), "System should be halted"

        print("\n4. Attempting trade while halted...")
        block_msg = halt_manager.block_trade("GOOGL", "BUY 100")
        print(f"   Trade blocked: {'BLOCKED' in block_msg}")

        assert "BLOCKED" in block_msg

        print("\n5. Resuming after halt...")
        success, msg = halt_manager.resume_trading(force=True)
        print(f"   Resume success: {success}")
        print(f"   Message: {msg}")

        assert success, "Resume should succeed"
        assert not halt_manager.is_halted(), "System should be active"

        print("\n[PASS] TEST PASSED: Complete workflow executed correctly!")
        return True

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_portfolio_heat_with_multiple_positions():
    """Test 6: Portfolio heat calculation with realistic positions"""
    print("\n" + "="*80)
    print("TEST 6: Portfolio Heat with Multiple Positions")
    print("="*80)

    config_path = script_dir / 'config' / 'risk_management.yaml'

    try:
        risk_calc = AdvancedRiskCalculator(config_path=str(config_path))

        balance = 100000.0
        positions = {
            'AAPL': {'quantity': 50, 'entry_price': 180.0, 'current_price': 185.0},
            'GOOGL': {'quantity': 10, 'entry_price': 2800.0, 'current_price': 2850.0},
            'MSFT': {'quantity': 40, 'entry_price': 380.0, 'current_price': 385.0}
        }

        print("\nPositions:")
        total_value = 0
        for symbol, pos in positions.items():
            value = pos['quantity'] * pos['current_price']
            total_value += value
            print(f"   {symbol}: {pos['quantity']} @ ${pos['current_price']:.2f} = ${value:,.2f}")

        print(f"\nTotal position value: ${total_value:,.2f}")
        print(f"Account balance: ${balance:,.2f}")

        # Calculate risk metrics
        risk_metrics = risk_calc.calculate_risk_metrics(balance, positions)

        print(f"\nRisk Metrics:")
        print(f"   Portfolio heat: {risk_metrics['portfolio_heat']:.2%}")
        print(f"   Safe to trade: {risk_metrics['is_safe_to_trade']}")

        # Expected heat calculation:
        # AAPL: 50 * 185 * 0.03 = 277.5
        # GOOGL: 10 * 2850 * 0.03 = 855
        # MSFT: 40 * 385 * 0.03 = 462
        # Total risk: 1594.5
        # Heat: 1594.5 / 100000 = 0.015945 (1.59%)

        expected_heat = (50 * 185 * 0.03 + 10 * 2850 * 0.03 + 40 * 385 * 0.03) / balance

        print(f"\nExpected heat: {expected_heat:.2%}")
        print(f"Actual heat: {risk_metrics['portfolio_heat']:.2%}")
        print(f"Difference: {abs(expected_heat - risk_metrics['portfolio_heat']):.4%}")

        assert abs(expected_heat - risk_metrics['portfolio_heat']) < 0.0001, "Heat calculation mismatch"
        assert risk_metrics['portfolio_heat'] < 0.25, "Heat should be under 25% limit"

        print("\n[PASS] TEST PASSED: Portfolio heat calculated correctly!")
        return True

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_edge_case_simultaneous_triggers():
    """Test 7: Multiple halt triggers simultaneously"""
    print("\n" + "="*80)
    print("TEST 7: Simultaneous Halt Triggers")
    print("="*80)

    cleanup_test_data()
    config_path = script_dir / 'config' / 'risk_management.yaml'

    try:
        halt_manager = EmergencyHaltManager(config_path=str(config_path))

        # Simulate both drawdown AND daily loss exceeding limits
        risk_metrics = {
            'current_drawdown': 0.16,  # 16% > 15% limit
            'daily_loss': 0.06,  # 6% > 5% limit
            'portfolio_heat': 0.20  # 20% (under limit)
        }

        print("Risk metrics (multiple violations):")
        print(f"   Drawdown: {risk_metrics['current_drawdown']:.2%} (limit: 15%)")
        print(f"   Daily loss: {risk_metrics['daily_loss']:.2%} (limit: 5%)")
        print(f"   Portfolio heat: {risk_metrics['portfolio_heat']:.2%} (limit: 25%)")

        should_halt, reason, trigger = halt_manager.check_halt_conditions(risk_metrics)

        print(f"\nShould halt: {should_halt}")
        print(f"Reason: {reason}")
        print(f"Primary trigger: {trigger}")

        assert should_halt, "Should trigger halt on multiple violations"
        # Should trigger on first violation found (drawdown)
        assert trigger in [HaltTrigger.DRAWDOWN.value, HaltTrigger.DAILY_LOSS.value]

        print("\n[PASS] TEST PASSED: Simultaneous triggers handled correctly!")
        return True

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        return False


def test_system_recovery_after_halt():
    """Test 8: System recovery and state persistence"""
    print("\n" + "="*80)
    print("TEST 8: System Recovery After Halt")
    print("="*80)

    cleanup_test_data()

    try:
        # First instance - trigger halt
        halt_manager1 = EmergencyHaltManager()
        halt_manager1.trigger_halt("Test halt for persistence", HaltTrigger.MANUAL.value)

        print("1. First instance halted")
        print(f"   Is halted: {halt_manager1.is_halted()}")
        print(f"   Halt reason: {halt_manager1.halt_state['halt_reason']}")

        # Simulate system restart - create new instance
        print("\n2. Simulating system restart (new instance)...")
        halt_manager2 = EmergencyHaltManager()

        print(f"   Second instance is halted: {halt_manager2.is_halted()}")
        print(f"   Halt reason persisted: {halt_manager2.halt_state['halt_reason']}")

        assert halt_manager2.is_halted(), "Halt state should persist across restart"
        assert halt_manager2.halt_state['halt_reason'] == "Test halt for persistence"

        # Resume
        print("\n3. Resuming trading...")
        success, msg = halt_manager2.resume_trading(force=True)
        print(f"   Resume success: {success}")

        # Verify state persists after resume
        print("\n4. Creating third instance to verify resume persisted...")
        halt_manager3 = EmergencyHaltManager()
        print(f"   Third instance is halted: {halt_manager3.is_halted()}")

        assert not halt_manager3.is_halted(), "Resume should persist"

        print("\n[PASS] TEST PASSED: State persistence working correctly!")
        return True

    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_integration_tests():
    """Run all Phase 1 integration tests"""
    print("\n" + "="*80)
    print("PHASE 1 INTEGRATION TEST SUITE - STAGING VALIDATION")
    print("="*80)
    print("\nValidating all Phase 1 components work together:")
    print("  - Risk configuration loading")
    print("  - Emergency halt system")
    print("  - Failure tracking")
    print("  - Portfolio heat calculations")
    print("  - Complete trading workflows")
    print("  - Edge cases and recovery")

    tests = [
        ("Configuration Loading", test_configuration_loading),
        ("Halt Manager Initialization", test_halt_manager_initialization),
        ("Risk + Halt Integration", test_risk_halt_integration),
        ("Failure Tracker + Halt Integration", test_failure_tracker_halt_integration),
        ("Complete Trading Workflow", test_complete_trading_workflow),
        ("Portfolio Heat Multi-Position", test_portfolio_heat_with_multiple_positions),
        ("Simultaneous Halt Triggers", test_edge_case_simultaneous_triggers),
        ("System Recovery & Persistence", test_system_recovery_after_halt),
    ]

    passed = 0
    failed = 0
    failed_tests = []

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                failed_tests.append(test_name)
        except Exception as e:
            print(f"\n[FAIL] TEST ERROR: {test_name}")
            print(f"   Exception: {e}")
            failed += 1
            failed_tests.append(test_name)

    # Cleanup
    cleanup_test_data()

    # Summary
    print("\n" + "="*80)
    print("INTEGRATION TEST SUITE SUMMARY")
    print("="*80)
    print(f"Total Tests: {len(tests)}")
    print(f"[PASS] Passed: {passed}")
    print(f"[FAIL] Failed: {failed}")

    if failed > 0:
        print("\nFailed tests:")
        for test in failed_tests:
            print(f"  - {test}")

    if failed == 0:
        print("\n[SUCCESS] ALL INTEGRATION TESTS PASSED!")
        print("\nValidation Results:")
        print("  [OK] Risk configuration system working")
        print("  [OK] Emergency halt system operational")
        print("  [OK] Failure tracking integrated correctly")
        print("  [OK] Portfolio calculations accurate")
        print("  [OK] Complete workflows validated")
        print("  [OK] Edge cases handled properly")
        print("  [OK] State persistence verified")
        print("\n[READY] PHASE 1 VALIDATED FOR PRODUCTION")
        return True
    else:
        print("\n[WARNING] SOME TESTS FAILED - Review errors above")
        print("[NOT READY] Phase 1 requires fixes before production")
        return False


if __name__ == "__main__":
    success = run_all_integration_tests()
    sys.exit(0 if success else 1)
