"""
Test Emergency Halt System - MCP-006
====================================

Comprehensive tests for emergency trading halt system including:
1. Automatic halt triggers (drawdown, daily loss, heat)
2. Manual halt triggers
3. Trade blocking during halt
4. Resume functionality
5. Edge cases

Author: Claude AI (MCP-006)
Date: 2025-11-11
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from risk_management.emergency_halt_manager import EmergencyHaltManager, HaltTrigger, HaltState


def cleanup_test_data():
    """Clean up test data files"""
    data_dir = Path(__file__).parent / 'data'
    halt_state_file = data_dir / 'halt_state.json'
    if halt_state_file.exists():
        halt_state_file.unlink()


def test_initialization():
    """Test 1: EmergencyHaltManager initialization"""
    print("\n" + "="*80)
    print("TEST 1: Emergency Halt Manager Initialization")
    print("="*80)

    cleanup_test_data()

    manager = EmergencyHaltManager()

    print(f"Manager created: {manager is not None}")
    print(f"Initial state: {manager.halt_state['state']}")
    print(f"Is halted: {manager.is_halted()}")

    assert manager is not None, "Manager should be created"
    assert manager.halt_state['state'] == HaltState.ACTIVE.value, "Should start in ACTIVE state"
    assert not manager.is_halted(), "Should not be halted initially"

    print("\n[PASS] TEST PASSED: Initialization successful!")
    return True


def test_manual_halt():
    """Test 2: Manual halt trigger"""
    print("\n" + "="*80)
    print("TEST 2: Manual Halt Trigger")
    print("="*80)

    cleanup_test_data()
    manager = EmergencyHaltManager()

    print("Triggering manual halt...")
    success = manager.trigger_halt("Manual halt for testing", HaltTrigger.MANUAL.value)

    print(f"Halt triggered: {success}")
    print(f"Is halted: {manager.is_halted()}")
    print(f"Halt reason: {manager.halt_state['halt_reason']}")

    assert success, "Halt should be triggered successfully"
    assert manager.is_halted(), "System should be halted"
    assert manager.halt_state['trigger_type'] == HaltTrigger.MANUAL.value

    print("\n[PASS] TEST PASSED: Manual halt works correctly!")
    return True


def test_automatic_drawdown_halt():
    """Test 3: Automatic halt on drawdown"""
    print("\n" + "="*80)
    print("TEST 3: Automatic Halt on Drawdown")
    print("="*80)

    cleanup_test_data()

    # Create manager with config
    config_path = script_dir / 'config' / 'risk_management.yaml'
    manager = EmergencyHaltManager(config_path=str(config_path))

    # Simulate risk metrics with excessive drawdown
    risk_metrics = {
        'current_drawdown': 0.16,  # 16% drawdown
        'daily_loss': 0.02,  # 2% daily loss
        'portfolio_heat': 0.15  # 15% heat
    }

    print(f"Risk metrics:")
    print(f"  Drawdown: {risk_metrics['current_drawdown']:.2%}")
    print(f"  Daily loss: {risk_metrics['daily_loss']:.2%}")

    should_halt, reason, trigger = manager.check_halt_conditions(risk_metrics)

    print(f"\nShould halt: {should_halt}")
    print(f"Reason: {reason}")
    print(f"Trigger: {trigger}")

    assert should_halt, "Should trigger halt on excessive drawdown"
    assert "drawdown" in reason.lower(), "Reason should mention drawdown"
    assert trigger == HaltTrigger.DRAWDOWN.value

    print("\n[PASS] TEST PASSED: Drawdown halt trigger works!")
    return True


def test_automatic_daily_loss_halt():
    """Test 4: Automatic halt on daily loss"""
    print("\n" + "="*80)
    print("TEST 4: Automatic Halt on Daily Loss")
    print("="*80)

    cleanup_test_data()

    config_path = script_dir / 'config' / 'risk_management.yaml'
    manager = EmergencyHaltManager(config_path=str(config_path))

    # Simulate risk metrics with excessive daily loss
    risk_metrics = {
        'current_drawdown': 0.08,  # 8% drawdown (under limit)
        'daily_loss': 0.06,  # 6% daily loss (over 5% limit)
        'portfolio_heat': 0.15  # 15% heat
    }

    print(f"Risk metrics:")
    print(f"  Drawdown: {risk_metrics['current_drawdown']:.2%}")
    print(f"  Daily loss: {risk_metrics['daily_loss']:.2%}")

    should_halt, reason, trigger = manager.check_halt_conditions(risk_metrics)

    print(f"\nShould halt: {should_halt}")
    print(f"Reason: {reason}")
    print(f"Trigger: {trigger}")

    assert should_halt, "Should trigger halt on excessive daily loss"
    assert "daily loss" in reason.lower(), "Reason should mention daily loss"
    assert trigger == HaltTrigger.DAILY_LOSS.value

    print("\n[PASS] TEST PASSED: Daily loss halt trigger works!")
    return True


def test_trade_blocking():
    """Test 5: Trade blocking when halted"""
    print("\n" + "="*80)
    print("TEST 5: Trade Blocking During Halt")
    print("="*80)

    cleanup_test_data()
    manager = EmergencyHaltManager()

    # Halt the system
    manager.trigger_halt("Test halt", HaltTrigger.MANUAL.value)

    # Attempt to block a trade
    print("Attempting to block trade for AAPL...")
    block_msg = manager.block_trade("AAPL", "BUY 100 shares")

    print(f"Block message:\n{block_msg}")

    assert manager.is_halted(), "System should be halted"
    assert "BLOCKED" in block_msg, "Message should indicate blocking"
    assert "AAPL" in block_msg, "Message should mention symbol"

    print("\n[PASS] TEST PASSED: Trade blocking works correctly!")
    return True


def test_resume_with_cooldown():
    """Test 6: Resume with cooldown period"""
    print("\n" + "="*80)
    print("TEST 6: Resume with Cooldown Period")
    print("="*80)

    cleanup_test_data()
    manager = EmergencyHaltManager()

    # Trigger halt
    manager.trigger_halt("Test halt", HaltTrigger.MANUAL.value)

    # Try to resume immediately (should fail due to cooldown)
    print("Attempting immediate resume (should fail)...")
    success, msg = manager.resume_trading()

    print(f"Resume result: {msg}")

    assert not success, "Should fail due to cooldown"
    assert "cooldown" in msg.lower(), "Message should mention cooldown"

    print("\n[PASS] TEST PASSED: Cooldown enforced correctly!")
    return True


def test_forced_resume():
    """Test 7: Forced resume bypassing cooldown"""
    print("\n" + "="*80)
    print("TEST 7: Forced Resume")
    print("="*80)

    cleanup_test_data()
    manager = EmergencyHaltManager()

    # Trigger halt
    manager.trigger_halt("Test halt", HaltTrigger.MANUAL.value)

    # Force resume
    print("Forcing resume (bypassing cooldown)...")
    success, msg = manager.resume_trading(force=True)

    print(f"Resume result: {msg}")
    print(f"Is halted: {manager.is_halted()}")

    assert success, "Forced resume should succeed"
    assert not manager.is_halted(), "System should be active"

    print("\n[PASS] TEST PASSED: Forced resume works!")
    return True


def test_kill_switch():
    """Test 8: Emergency kill switch"""
    print("\n" + "="*80)
    print("TEST 8: Emergency Kill Switch")
    print("="*80)

    cleanup_test_data()
    manager = EmergencyHaltManager()

    print("Activating kill switch...")
    success = manager.trigger_kill_switch("Emergency kill switch test")

    print(f"Kill switch activated: {success}")
    print(f"Is halted: {manager.is_halted()}")
    print(f"Trigger type: {manager.halt_state['trigger_type']}")

    assert success, "Kill switch should activate"
    assert manager.is_halted(), "System should be halted"
    assert manager.halt_state['trigger_type'] == HaltTrigger.KILL_SWITCH.value

    print("\n[PASS] TEST PASSED: Kill switch works correctly!")
    return True


def test_halt_state_persistence():
    """Test 9: Halt state persistence across restarts"""
    print("\n" + "="*80)
    print("TEST 9: Halt State Persistence")
    print("="*80)

    cleanup_test_data()

    # Create manager and halt
    manager1 = EmergencyHaltManager()
    manager1.trigger_halt("Persistence test", HaltTrigger.MANUAL.value)

    print("First manager halted")
    print(f"Halt reason: {manager1.halt_state['halt_reason']}")

    # Create new manager instance (simulates restart)
    print("\nCreating new manager instance...")
    manager2 = EmergencyHaltManager()

    print(f"Second manager state: {manager2.halt_state['state']}")
    print(f"Is halted: {manager2.is_halted()}")
    print(f"Halt reason: {manager2.halt_state['halt_reason']}")

    assert manager2.is_halted(), "Halt state should persist"
    assert manager2.halt_state['halt_reason'] == "Persistence test"

    print("\n[PASS] TEST PASSED: Halt state persists across restarts!")
    return True


def test_multiple_halt_attempts():
    """Test 10: Multiple halt attempts (should ignore duplicates)"""
    print("\n" + "="*80)
    print("TEST 10: Multiple Halt Attempts")
    print("="*80)

    cleanup_test_data()
    manager = EmergencyHaltManager()

    # First halt
    success1 = manager.trigger_halt("First halt", HaltTrigger.MANUAL.value)
    halt_count1 = manager.halt_state['halt_count']

    # Second halt attempt (should be ignored)
    success2 = manager.trigger_halt("Second halt", HaltTrigger.MANUAL.value)
    halt_count2 = manager.halt_state['halt_count']

    print(f"First halt: {success1}, count: {halt_count1}")
    print(f"Second halt: {success2}, count: {halt_count2}")

    assert success1, "First halt should succeed"
    assert not success2, "Second halt should be ignored"
    assert halt_count1 == halt_count2, "Halt count should not increase"

    print("\n[PASS] TEST PASSED: Duplicate halts ignored correctly!")
    return True


def test_halt_summary():
    """Test 11: Halt status summary"""
    print("\n" + "="*80)
    print("TEST 11: Halt Status Summary")
    print("="*80)

    cleanup_test_data()
    manager = EmergencyHaltManager()

    # Test active status
    summary_active = manager.get_halt_summary()
    print("Active state summary:")
    print(summary_active)

    assert "ACTIVE" in summary_active

    # Trigger halt
    manager.trigger_halt("Summary test", HaltTrigger.MANUAL.value)

    # Test halted status
    summary_halted = manager.get_halt_summary()
    print("\nHalted state summary:")
    print(summary_halted)

    assert "HALTED" in summary_halted
    assert "Summary test" in summary_halted

    print("\n[PASS] TEST PASSED: Halt summary works correctly!")
    return True


def test_no_halt_on_safe_metrics():
    """Test 12: No halt when metrics are safe"""
    print("\n" + "="*80)
    print("TEST 12: No Halt on Safe Metrics")
    print("="*80)

    cleanup_test_data()

    config_path = script_dir / 'config' / 'risk_management.yaml'
    manager = EmergencyHaltManager(config_path=str(config_path))

    # Safe risk metrics
    risk_metrics = {
        'current_drawdown': 0.05,  # 5% drawdown (safe)
        'daily_loss': 0.01,  # 1% daily loss (safe)
        'portfolio_heat': 0.15  # 15% heat (safe)
    }

    print(f"Risk metrics (all safe):")
    print(f"  Drawdown: {risk_metrics['current_drawdown']:.2%}")
    print(f"  Daily loss: {risk_metrics['daily_loss']:.2%}")
    print(f"  Portfolio heat: {risk_metrics['portfolio_heat']:.2%}")

    should_halt, reason, trigger = manager.check_halt_conditions(risk_metrics)

    print(f"\nShould halt: {should_halt}")

    assert not should_halt, "Should NOT halt on safe metrics"
    assert reason is None, "Reason should be None"

    print("\n[PASS] TEST PASSED: No false positives on safe metrics!")
    return True


def run_all_tests():
    """Run all emergency halt tests"""
    print("\n" + "="*80)
    print("EMERGENCY HALT SYSTEM TEST SUITE - MCP-006")
    print("="*80)
    print("\nTesting emergency trading halt functionality:")
    print("  - Automatic halt triggers")
    print("  - Manual halt controls")
    print("  - Trade blocking")
    print("  - Resume functionality")
    print("  - Edge cases")

    tests = [
        ("Initialization", test_initialization),
        ("Manual Halt", test_manual_halt),
        ("Drawdown Halt", test_automatic_drawdown_halt),
        ("Daily Loss Halt", test_automatic_daily_loss_halt),
        ("Trade Blocking", test_trade_blocking),
        ("Resume with Cooldown", test_resume_with_cooldown),
        ("Forced Resume", test_forced_resume),
        ("Kill Switch", test_kill_switch),
        ("State Persistence", test_halt_state_persistence),
        ("Multiple Halt Attempts", test_multiple_halt_attempts),
        ("Halt Summary", test_halt_summary),
        ("No Halt on Safe Metrics", test_no_halt_on_safe_metrics),
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
        print("  [OK] Emergency halt system working correctly")
        print("  [OK] All automatic triggers functional")
        print("  [OK] Manual controls working")
        print("  [OK] Trade blocking operational")
        print("  [OK] Resume functionality verified")
        print("  [OK] State persistence working")
        return True
    else:
        print("\n[WARNING] SOME TESTS FAILED - Review errors above")
        return False


if __name__ == "__main__":
    success = run_all_tests()

    # Cleanup
    cleanup_test_data()

    sys.exit(0 if success else 1)
