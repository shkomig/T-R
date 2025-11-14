#!/usr/bin/env python3
"""
Test script for Enhanced Position Sizer
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from risk_management.advanced_risk_calculator import AdvancedRiskCalculator
from risk_management.enhanced_position_sizer import EnhancedPositionSizer

def test_position_sizer():
    """Test Enhanced Position Sizer initialization"""
    try:
        print("🧪 Testing Enhanced Position Sizer...")
        
        # Create risk calculator
        risk_calc = AdvancedRiskCalculator()
        print("✅ Risk Calculator created")
        
        # Create position sizer
        position_sizer = EnhancedPositionSizer(risk_calc)
        print("✅ Position Sizer created")
        
        print(f"📊 Base Position Size: ${position_sizer.base_position_size}")
        print(f"📊 Max Position Size: ${position_sizer.max_position_size}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_position_sizer()
    print(f"\n🎯 Test Result: {'✅ SUCCESS' if success else '❌ FAILED'}")