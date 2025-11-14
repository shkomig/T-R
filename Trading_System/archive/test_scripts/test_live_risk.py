#!/usr/bin/env python3
"""
Test live risk calculation with real account values
"""
import sys
import os
sys.path.append(os.getcwd())

from risk_management.advanced_risk_calculator import AdvancedRiskCalculator

def test_live_risk():
    """Test risk calculation with live account values"""
    print("=== LIVE RISK CALCULATION TEST ===")
    
    # Create risk calculator
    risk_calc = AdvancedRiskCalculator()
    
    # Test with live account value
    current_balance = 1224523.97  # From the latest dashboard output
    positions = {}  # No positions
    
    print(f"Testing with account balance: ${current_balance:,.2f}")
    print(f"Initial peak balance: ${risk_calc.peak_balance:,.2f}")
    print(f"Initial daily start balance: ${risk_calc.daily_start_balance:,.2f}")
    
    # Calculate risk metrics
    metrics = risk_calc.calculate_risk_metrics(current_balance, positions)
    
    print(f"\n--- RESULTS ---")
    print(f"Peak balance after calculation: ${metrics['peak_balance']:,.2f}")
    print(f"Current balance: ${metrics['current_balance']:,.2f}")
    print(f"Calculated drawdown: {metrics['current_drawdown']:.4f} ({metrics['current_drawdown']:.2%})")
    print(f"Is safe to trade: {metrics['is_safe_to_trade']}")
    print(f"Drawdown OK: {metrics['safety_checks']['drawdown_ok']}")
    
    # Expected calculation
    expected_drawdown = (metrics['peak_balance'] - current_balance) / metrics['peak_balance'] if metrics['peak_balance'] > 0 else 0
    print(f"Expected drawdown: {expected_drawdown:.4f} ({expected_drawdown:.2%})")
    
    if expected_drawdown > 0.15:
        print(f"❌ Drawdown exceeds 15% limit!")
    else:
        print(f"✅ Drawdown within 15% limit!")

if __name__ == "__main__":
    test_live_risk()