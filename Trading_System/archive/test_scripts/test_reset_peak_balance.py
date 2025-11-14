#!/usr/bin/env python3
"""
Test script for reset_peak_balance functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from risk_management.advanced_risk_calculator import AdvancedRiskCalculator
from risk_management.risk_calculator import RiskCalculator
import yaml

def test_reset_peak_balance():
    """Test the reset_peak_balance function"""
    
    print("🧪 Testing reset_peak_balance functionality...")
    print("=" * 50)
    
    # Test 1: Advanced Risk Calculator
    print("\n1. Testing AdvancedRiskCalculator:")
    try:
        advanced_calc = AdvancedRiskCalculator()
        
        # Initial peak balance
        print(f"   Initial peak balance: ${advanced_calc.peak_balance:,.2f}")
        
        # Reset to new value
        test_balance = 125000.50
        advanced_calc.reset_peak_balance(test_balance)
        
        print(f"   Peak balance after reset: ${advanced_calc.peak_balance:,.2f}")
        print(f"   Daily start balance: ${advanced_calc.daily_start_balance:,.2f}")
        
        if advanced_calc.peak_balance == test_balance:
            print("   ✅ AdvancedRiskCalculator test PASSED")
        else:
            print("   ❌ AdvancedRiskCalculator test FAILED")
            
    except Exception as e:
        print(f"   ❌ AdvancedRiskCalculator error: {e}")
    
    # Test 2: Regular Risk Calculator
    print("\n2. Testing RiskCalculator:")
    try:
        # Load config
        with open('config/risk_management.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        risk_calc = RiskCalculator(config)
        
        # Initial peak balance
        print(f"   Initial peak balance: ${risk_calc.peak_balance:,.2f}")
        
        # Reset to new value
        test_balance = 98750.25
        risk_calc.reset_peak_balance(test_balance)
        
        print(f"   Peak balance after reset: ${risk_calc.peak_balance:,.2f}")
        
        if risk_calc.peak_balance == test_balance:
            print("   ✅ RiskCalculator test PASSED")
        else:
            print("   ❌ RiskCalculator test FAILED")
            
    except Exception as e:
        print(f"   ❌ RiskCalculator error: {e}")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    test_reset_peak_balance()