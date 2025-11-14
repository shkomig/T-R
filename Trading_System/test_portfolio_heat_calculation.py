"""
Test Portfolio Heat Calculation - MCP-005
==========================================

Comprehensive tests to verify portfolio heat calculation uses correct
stop_loss_percent from consolidated risk configuration.

This test suite validates:
1. Portfolio heat uses config value (3% stop loss)
2. Correct detection of overexposure
3. Accurate risk calculations for various scenarios
4. Proper integration with config system

Author: Claude AI (MCP-005)
Date: 2025-11-11
"""

import sys
import os
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from risk_management.advanced_risk_calculator import AdvancedRiskCalculator


def test_single_position_heat():
    """
    Test Scenario 1: Single Position Heat Calculation

    Setup:
    - Balance: $100,000
    - Position: 100 shares @ $200 = $20,000
    - Stop loss: 3% (from config)

    Expected:
    - Position risk: $20,000 × 0.03 = $600
    - Portfolio heat: $600 / $100,000 = 0.006 (0.6%)
    """
    print("\n" + "="*80)
    print("TEST 1: Single Position Heat Calculation")
    print("="*80)

    # Initialize with config
    config_path = os.path.join(script_dir, 'config', 'risk_management.yaml')
    risk_calc = AdvancedRiskCalculator(config_path=config_path)

    # Verify config loaded correctly
    print(f"[OK] Config loaded: stop_loss_percent = {risk_calc.stop_loss_percent}")
    assert risk_calc.stop_loss_percent == 0.03, f"Expected 0.03, got {risk_calc.stop_loss_percent}"

    # Setup test data
    balance = 100000.0
    positions = {
        'AAPL': {
            'quantity': 100,
            'entry_price': 200.0,
            'current_price': 200.0
        }
    }

    # Calculate heat
    heat = risk_calc._calculate_portfolio_heat(positions, balance)

    # Expected calculations
    position_value = 100 * 200  # $20,000
    position_risk = position_value * 0.03  # $600
    expected_heat = position_risk / balance  # 0.006 (0.6%)

    print(f"\nSetup:")
    print(f"  Balance: ${balance:,.2f}")
    print(f"  Position: 100 shares @ $200 = ${position_value:,.2f}")
    print(f"  Stop Loss: {risk_calc.stop_loss_percent:.1%}")

    print(f"\nCalculations:")
    print(f"  Position Risk: ${position_value:,.2f} × {risk_calc.stop_loss_percent:.3f} = ${position_risk:,.2f}")
    print(f"  Portfolio Heat: ${position_risk:,.2f} / ${balance:,.2f} = {expected_heat:.4f} ({expected_heat:.2%})")

    print(f"\nResults:")
    print(f"  Calculated Heat: {heat:.4f} ({heat:.2%})")
    print(f"  Expected Heat: {expected_heat:.4f} ({expected_heat:.2%})")

    # Validate
    assert abs(heat - expected_heat) < 0.0001, f"Heat mismatch: {heat} vs {expected_heat}"
    print(f"\n[PASS] TEST PASSED: Portfolio heat calculated correctly!")

    return True


def test_multiple_positions_heat():
    """
    Test Scenario 2: Multiple Positions Heat Calculation

    Setup:
    - Balance: $100,000
    - Position 1: 100 shares @ $150 = $15,000
    - Position 2: 50 shares @ $300 = $15,000
    - Stop loss: 3%

    Expected:
    - Position 1 risk: $15,000 × 0.03 = $450
    - Position 2 risk: $15,000 × 0.03 = $450
    - Total risk: $900
    - Portfolio heat: $900 / $100,000 = 0.009 (0.9%)
    """
    print("\n" + "="*80)
    print("TEST 2: Multiple Positions Heat Calculation")
    print("="*80)

    # Initialize with config
    config_path = os.path.join(script_dir, 'config', 'risk_management.yaml')
    risk_calc = AdvancedRiskCalculator(config_path=config_path)

    # Setup test data
    balance = 100000.0
    positions = {
        'AAPL': {
            'quantity': 100,
            'entry_price': 150.0,
            'current_price': 150.0
        },
        'GOOGL': {
            'quantity': 50,
            'entry_price': 300.0,
            'current_price': 300.0
        }
    }

    # Calculate heat
    heat = risk_calc._calculate_portfolio_heat(positions, balance)

    # Expected calculations
    pos1_value = 100 * 150  # $15,000
    pos2_value = 50 * 300   # $15,000
    pos1_risk = pos1_value * 0.03  # $450
    pos2_risk = pos2_value * 0.03  # $450
    total_risk = pos1_risk + pos2_risk  # $900
    expected_heat = total_risk / balance  # 0.009 (0.9%)

    print(f"\nSetup:")
    print(f"  Balance: ${balance:,.2f}")
    print(f"  Position 1: 100 shares @ $150 = ${pos1_value:,.2f}")
    print(f"  Position 2: 50 shares @ $300 = ${pos2_value:,.2f}")
    print(f"  Stop Loss: {risk_calc.stop_loss_percent:.1%}")

    print(f"\nCalculations:")
    print(f"  Position 1 Risk: ${pos1_value:,.2f} × 0.03 = ${pos1_risk:,.2f}")
    print(f"  Position 2 Risk: ${pos2_value:,.2f} × 0.03 = ${pos2_risk:,.2f}")
    print(f"  Total Risk: ${pos1_risk:,.2f} + ${pos2_risk:,.2f} = ${total_risk:,.2f}")
    print(f"  Portfolio Heat: ${total_risk:,.2f} / ${balance:,.2f} = {expected_heat:.4f} ({expected_heat:.2%})")

    print(f"\nResults:")
    print(f"  Calculated Heat: {heat:.4f} ({heat:.2%})")
    print(f"  Expected Heat: {expected_heat:.4f} ({expected_heat:.2%})")

    # Validate
    assert abs(heat - expected_heat) < 0.0001, f"Heat mismatch: {heat} vs {expected_heat}"
    print(f"\n[PASS] TEST PASSED: Multiple positions heat calculated correctly!")

    return True


def test_at_heat_limit():
    """
    Test Scenario 3: At Heat Limit

    Setup:
    - Balance: $100,000
    - Max heat: 25% (from config)
    - Stop loss: 3%

    Calculate maximum exposure before hitting limit.

    Expected:
    - Maximum total position value: $100,000 × 0.25 / 0.03 = $833,333
    - At this exposure, heat = 25% (at limit)
    """
    print("\n" + "="*80)
    print("TEST 3: At Heat Limit Detection")
    print("="*80)

    # Initialize with config
    config_path = os.path.join(script_dir, 'config', 'risk_management.yaml')
    risk_calc = AdvancedRiskCalculator(config_path=config_path)

    # Setup test data
    balance = 100000.0
    max_heat = risk_calc.max_portfolio_heat  # 0.25 (25%)
    stop_loss = risk_calc.stop_loss_percent  # 0.03 (3%)

    # Calculate maximum exposure
    max_exposure = (balance * max_heat) / stop_loss

    print(f"\nSetup:")
    print(f"  Balance: ${balance:,.2f}")
    print(f"  Max Heat: {max_heat:.1%}")
    print(f"  Stop Loss: {stop_loss:.1%}")

    print(f"\nCalculations:")
    print(f"  Max Exposure = (Balance × Max Heat) / Stop Loss")
    print(f"  Max Exposure = (${balance:,.2f} × {max_heat}) / {stop_loss}")
    print(f"  Max Exposure = ${max_exposure:,.2f}")

    # Create positions at max exposure
    # Using 10 positions of equal size
    position_size = max_exposure / 10
    positions = {}
    for i in range(10):
        positions[f'STOCK{i}'] = {
            'quantity': 100,
            'entry_price': position_size / 100,
            'current_price': position_size / 100
        }

    # Calculate heat
    heat = risk_calc._calculate_portfolio_heat(positions, balance)

    print(f"\nTest:")
    print(f"  Created 10 positions totaling ${max_exposure:,.2f}")
    print(f"  Calculated Heat: {heat:.4f} ({heat:.2%})")
    print(f"  Max Heat Limit: {max_heat:.4f} ({max_heat:.2%})")

    # Validate (should be very close to limit)
    assert abs(heat - max_heat) < 0.01, f"Heat should be near limit: {heat} vs {max_heat}"
    print(f"\n[PASS] TEST PASSED: Heat at limit calculated correctly!")

    return True


def test_overexposure_detection():
    """
    Test Scenario 4: Overexposure Detection

    Setup:
    - Balance: $100,000
    - Max heat: 25%
    - Position value: $1,000,000 (10x balance - extreme case)
    - Stop loss: 3%

    Expected:
    - Position risk: $1,000,000 × 0.03 = $30,000
    - Portfolio heat: $30,000 / $100,000 = 0.30 (30%)
    - Should EXCEED 25% limit → trading blocked
    """
    print("\n" + "="*80)
    print("TEST 4: Overexposure Detection")
    print("="*80)

    # Initialize with config
    config_path = os.path.join(script_dir, 'config', 'risk_management.yaml')
    risk_calc = AdvancedRiskCalculator(config_path=config_path)

    # Setup test data - EXTREME overexposure
    balance = 100000.0
    positions = {
        'TSLA': {
            'quantity': 1000,
            'entry_price': 1000.0,
            'current_price': 1000.0  # $1M position!
        }
    }

    # Calculate heat
    heat = risk_calc._calculate_portfolio_heat(positions, balance)

    # Expected calculations
    position_value = 1000 * 1000  # $1,000,000
    position_risk = position_value * 0.03  # $30,000
    expected_heat = position_risk / balance  # 0.30 (30%)
    max_heat = risk_calc.max_portfolio_heat  # 0.25 (25%)

    print(f"\nSetup:")
    print(f"  Balance: ${balance:,.2f}")
    print(f"  Position: 1000 shares @ $1,000 = ${position_value:,.2f} (10x balance!)")
    print(f"  Stop Loss: {risk_calc.stop_loss_percent:.1%}")
    print(f"  Max Heat Limit: {max_heat:.1%}")

    print(f"\nCalculations:")
    print(f"  Position Risk: ${position_value:,.2f} × 0.03 = ${position_risk:,.2f}")
    print(f"  Portfolio Heat: ${position_risk:,.2f} / ${balance:,.2f} = {expected_heat:.4f} ({expected_heat:.2%})")

    print(f"\nResults:")
    print(f"  Calculated Heat: {heat:.4f} ({heat:.2%})")
    print(f"  Expected Heat: {expected_heat:.4f} ({expected_heat:.2%})")
    print(f"  Max Allowed: {max_heat:.4f} ({max_heat:.2%})")

    # Validate
    assert abs(heat - expected_heat) < 0.0001, f"Heat mismatch: {heat} vs {expected_heat}"
    assert heat > max_heat, f"Should detect overexposure: {heat} should be > {max_heat}"

    print(f"\n[WARNING] OVEREXPOSURE DETECTED: {heat:.2%} > {max_heat:.2%}")
    print(f"[PASS] TEST PASSED: Overexposure correctly detected!")

    return True


def test_realistic_portfolio_scenario():
    """
    Test Scenario 5: Realistic Portfolio

    Setup:
    - Balance: $100,000
    - 5 positions with varying sizes
    - Stop loss: 3%

    Demonstrates typical portfolio heat calculation.
    """
    print("\n" + "="*80)
    print("TEST 5: Realistic Portfolio Scenario")
    print("="*80)

    # Initialize with config
    config_path = os.path.join(script_dir, 'config', 'risk_management.yaml')
    risk_calc = AdvancedRiskCalculator(config_path=config_path)

    # Setup realistic portfolio
    balance = 100000.0
    positions = {
        'AAPL': {'quantity': 50, 'entry_price': 180.0, 'current_price': 185.0},  # $9,250
        'MSFT': {'quantity': 30, 'entry_price': 380.0, 'current_price': 375.0},  # $11,250
        'GOOGL': {'quantity': 10, 'entry_price': 140.0, 'current_price': 145.0}, # $1,450
        'TSLA': {'quantity': 15, 'entry_price': 250.0, 'current_price': 260.0},  # $3,900
        'NVDA': {'quantity': 20, 'entry_price': 480.0, 'current_price': 495.0},  # $9,900
    }

    # Calculate heat
    heat = risk_calc._calculate_portfolio_heat(positions, balance)

    print(f"\nPortfolio:")
    print(f"  Balance: ${balance:,.2f}")
    print(f"  Stop Loss: {risk_calc.stop_loss_percent:.1%}")
    print(f"\nPositions:")

    total_value = 0
    total_risk = 0
    for symbol, pos in positions.items():
        value = pos['quantity'] * pos['current_price']
        risk = value * risk_calc.stop_loss_percent
        total_value += value
        total_risk += risk
        print(f"  {symbol:6s}: {pos['quantity']:3.0f} shares @ ${pos['current_price']:6.2f} = ${value:8,.2f} (risk: ${risk:6,.2f})")

    expected_heat = total_risk / balance

    print(f"\nSummary:")
    print(f"  Total Position Value: ${total_value:,.2f}")
    print(f"  Total Risk Exposure: ${total_risk:,.2f}")
    print(f"  Portfolio Heat: {heat:.4f} ({heat:.2%})")
    print(f"  Max Heat Limit: {risk_calc.max_portfolio_heat:.4f} ({risk_calc.max_portfolio_heat:.2%})")

    # Validate
    assert abs(heat - expected_heat) < 0.0001, f"Heat mismatch: {heat} vs {expected_heat}"

    if heat < risk_calc.max_portfolio_heat:
        print(f"\n[PASS] SAFE: Portfolio heat {heat:.2%} < {risk_calc.max_portfolio_heat:.2%} limit")
    else:
        print(f"\n[WARNING] WARNING: Portfolio heat {heat:.2%} ≥ {risk_calc.max_portfolio_heat:.2%} limit")

    print(f"[PASS] TEST PASSED: Realistic portfolio calculated correctly!")

    return True


def run_all_tests():
    """Run all portfolio heat tests"""
    print("\n" + "="*80)
    print("PORTFOLIO HEAT CALCULATION TEST SUITE - MCP-005")
    print("="*80)
    print("\nVerifying portfolio heat calculation uses correct config values:")
    print("  - stop_loss_percent: 3% (from risk_management.yaml)")
    print("  - max_portfolio_heat: 25% (from risk_management.yaml)")

    tests = [
        ("Single Position Heat", test_single_position_heat),
        ("Multiple Positions Heat", test_multiple_positions_heat),
        ("At Heat Limit", test_at_heat_limit),
        ("Overexposure Detection", test_overexposure_detection),
        ("Realistic Portfolio", test_realistic_portfolio_scenario),
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
        print("  [OK] Portfolio heat calculation uses config values correctly")
        print("  [OK] Stop loss percent from config: 3%")
        print("  [OK] Overexposure detection working properly")
        print("  [OK] Risk calculations are accurate")
        return True
    else:
        print("\n[WARNING] SOME TESTS FAILED - Review errors above")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
