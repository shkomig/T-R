#!/usr/bin/env python3
"""
Manual Peak Balance Reset Script
================================
Script to manually reset the peak balance in AdvancedRiskCalculator to prevent drawdown alerts
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from risk_management.advanced_risk_calculator import AdvancedRiskCalculator

def reset_peak_balance_manual():
    """Reset peak balance manually to current account value"""
    
    print("🔄 Manual Peak Balance Reset")
    print("=" * 40)
    
    # Mock account value (same as used in simulation)
    current_net_liquidation = 1158340.55
    
    print(f"Current Net Liquidation: ${current_net_liquidation:,.2f}")
    
    # Create risk calculator instance
    risk_calc = AdvancedRiskCalculator()
    
    print(f"Old Peak Balance: ${risk_calc.peak_balance:,.2f}")
    
    # Reset peak balance
    risk_calc.reset_peak_balance(current_net_liquidation)
    
    print(f"New Peak Balance: ${risk_calc.peak_balance:,.2f}")
    print(f"Daily Start Balance: ${risk_calc.daily_start_balance:,.2f}")
    
    # Calculate new drawdown (should be 0%)
    drawdown = ((risk_calc.peak_balance - current_net_liquidation) / risk_calc.peak_balance) * 100
    print(f"New Drawdown: {drawdown:.2f}%")
    
    print("✅ Peak balance reset completed!")
    print("\nNow the system should allow trading without drawdown restrictions.")

if __name__ == "__main__":
    reset_peak_balance_manual()