#!/usr/bin/env python3
"""
Reset daily trade counter
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from risk_management.advanced_risk_calculator import AdvancedRiskCalculator

def reset_trade_counter():
    """Reset daily trade counter to 0"""
    try:
        print("🔄 Resetting daily trade counter...")
        
        # Create risk calculator
        risk_calc = AdvancedRiskCalculator()
        
        # Reset counter
        risk_calc.trade_count_today = 0
        
        print(f"✅ Daily trades reset to: {risk_calc.trade_count_today}")
        print(f"📊 Max daily trades: {risk_calc.max_daily_trades}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    reset_trade_counter()