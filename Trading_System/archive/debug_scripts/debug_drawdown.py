#!/usr/bin/env python3
"""
Debug drawdown calculation issue
"""
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from risk_management.advanced_risk_calculator import AdvancedRiskCalculator

# Mock broker class for testing
class MockBroker:
    """Mock broker for testing"""
    def __init__(self):
        self.account = {
            'NetLiquidation': 93968.0,
            'AvailableFunds': 93968.0,
            'BuyingPower': 93968.0,
            'TotalCashValue': 93968.0,
            'Currency': 'USD'
        }
    
    def get_account_summary(self):
        return self.account

def debug_drawdown():
    """Debug the drawdown calculation"""
    print("=== DRAWDOWN DEBUG ===")
    
    # Create risk calculator and mock broker
    risk_calc = AdvancedRiskCalculator()
    broker = MockBroker()
    
    # Get account info
    account_info = broker.get_account_summary()
    net_liq = account_info.get('NetLiquidation', 0)
    print(f"Mock broker account value: ${net_liq:,.2f}")
    print(f"Initial peak balance: ${risk_calc.peak_balance:,.2f}")
    print(f"Initial daily start balance: ${risk_calc.daily_start_balance:,.2f}")
    
    # Calculate initial drawdown
    initial_drawdown = (risk_calc.peak_balance - net_liq) / risk_calc.peak_balance if risk_calc.peak_balance > 0 else 0
    print(f"Initial calculated drawdown: {initial_drawdown:.4f} ({initial_drawdown:.2%})")
    
    # Reset peak balance
    print("\n--- RESETTING PEAK BALANCE ---")
    risk_calc.reset_peak_balance(net_liq)
    print(f"After reset peak balance: ${risk_calc.peak_balance:,.2f}")
    print(f"After reset daily start balance: ${risk_calc.daily_start_balance:,.2f}")
    
    # Calculate drawdown after reset
    new_drawdown = (risk_calc.peak_balance - net_liq) / risk_calc.peak_balance if risk_calc.peak_balance > 0 else 0
    print(f"New calculated drawdown: {new_drawdown:.4f} ({new_drawdown:.2%})")
    
    # Test risk calculation
    print("\n--- RISK CALCULATION ---")
    positions = {}  # No positions
    metrics = risk_calc.calculate_risk_metrics(net_liq, positions)
    
    print(f"Is safe to trade: {metrics.get('is_safe_to_trade', False)}")
    print(f"Drawdown OK: {metrics.get('safety_checks', {}).get('drawdown_ok', False)}")
    print(f"Current drawdown: {metrics['current_drawdown']:.4f} ({metrics['current_drawdown']:.2%})")
    print(f"Peak balance used: ${metrics['peak_balance']:,.2f}")
    print(f"Current balance used: ${metrics['current_balance']:,.2f}")

if __name__ == "__main__":
    debug_drawdown()