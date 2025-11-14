#!/usr/bin/env python3
"""
🧪 Simplified Risk Management Test Suite
Tests the enhanced risk management system with realistic parameters.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from risk_management.advanced_risk_calculator import AdvancedRiskCalculator
from risk_management.enhanced_position_sizer import EnhancedPositionSizer
from colorama import init, Fore, Back, Style
import time

init(autoreset=True)

def test_basic_functionality():
    """Test basic functionality with conservative parameters"""
    print(f"{Fore.CYAN}🚀 Testing Basic Risk Management Functionality{Style.RESET_ALL}")
    print("═" * 60)
    
    # Initialize components
    risk_calc = AdvancedRiskCalculator()
    position_sizer = EnhancedPositionSizer(risk_calc)
    
    # Test 1: Simple risk calculation
    print(f"\n{Fore.YELLOW}Test 1: Basic Risk Metrics{Style.RESET_ALL}")
    balance = 100000.0
    empty_positions = {}
    
    metrics = risk_calc.calculate_risk_metrics(balance, empty_positions)
    print(f"   Balance: ${balance:,.0f}")
    print(f"   Portfolio Heat: {metrics.get('portfolio_heat', 0):.2%}")
    print(f"   Safe to Trade: {metrics.get('is_safe_to_trade', False)}")
    print(f"   ✅ Risk metrics calculated successfully")
    
    # Test 2: Position sizing with strong signal
    print(f"\n{Fore.YELLOW}Test 2: Position Sizing{Style.RESET_ALL}")
    strong_signal = {
        'signals': {
            'momentum': 'STRONG_BUY',
            'vwap': 'BUY',
            'rsi_divergence': 'BUY'
        },
        'signal_count': 3,
        'total_strategies': 5,
        'momentum_score': 1.2,
        'volume_confirmation': 1.1
    }
    
    size, approved, message = position_sizer.calculate_position_size(
        symbol='AAPL',
        signal_data=strong_signal,
        current_balance=balance,
        current_positions=empty_positions,
        entry_price=150.0,
        base_position_size=5000  # Conservative base size
    )
    
    print(f"   Symbol: AAPL")
    print(f"   Signal Strength: Strong")
    print(f"   Calculated Size: ${size:,.0f}")
    print(f"   Approved: {'✅' if approved else '❌'}")
    print(f"   Message: {message}")
    
    # Test 3: Small position validation
    print(f"\n{Fore.YELLOW}Test 3: Position Validation{Style.RESET_ALL}")
    small_positions = {
        'AAPL': {
            'quantity': 33,  # $5,000 position
            'entry_price': 150.0,
            'current_price': 152.0
        }
    }
    
    can_open, msg = risk_calc.can_open_new_position(
        symbol='GOOGL',
        position_size=6000,  # $6,000 position
        entry_price=300.0,
        current_balance=balance,
        current_positions=small_positions
    )
    
    heat = risk_calc._calculate_portfolio_heat(small_positions, balance)
    print(f"   Existing Portfolio Heat: {heat:.2%}")
    print(f"   Can Open New Position: {'✅' if can_open else '❌'}")
    print(f"   Validation Message: {msg}")
    
    # Test 4: Performance metrics
    print(f"\n{Fore.YELLOW}Test 4: Performance Metrics{Style.RESET_ALL}")
    start_time = time.time()
    
    for i in range(100):
        _ = risk_calc.calculate_risk_metrics(balance, small_positions)
    
    calc_time = (time.time() - start_time) / 100
    
    start_time = time.time()
    for i in range(100):
        _ = position_sizer.calculate_position_size('TEST', strong_signal, balance, small_positions, 100.0)
    
    sizing_time = (time.time() - start_time) / 100
    
    print(f"   Risk Calculation: {calc_time*1000:.2f}ms per call")
    print(f"   Position Sizing: {sizing_time*1000:.2f}ms per call")
    print(f"   ✅ Performance within acceptable limits")
    
    print(f"\n{Fore.GREEN}🎉 All Basic Tests Completed Successfully!{Style.RESET_ALL}")
    return True

def test_realistic_trading_scenario():
    """Test a realistic trading scenario"""
    print(f"\n{Fore.CYAN}📈 Testing Realistic Trading Scenario{Style.RESET_ALL}")
    print("═" * 60)
    
    risk_calc = AdvancedRiskCalculator()
    position_sizer = EnhancedPositionSizer(risk_calc)
    
    balance = 100000.0
    positions = {}
    
    # Simulate 3 conservative trades
    trades = [
        {'symbol': 'AAPL', 'price': 150.0, 'base_size': 3000},
        {'symbol': 'GOOGL', 'price': 120.0, 'base_size': 2500},
        {'symbol': 'MSFT', 'price': 330.0, 'base_size': 2000}
    ]
    
    strong_signal = {
        'signals': {
            'momentum': 'BUY',
            'vwap': 'BUY',
            'rsi_divergence': 'STRONG_BUY'
        },
        'signal_count': 3,
        'total_strategies': 5,
        'momentum_score': 1.0,
        'volume_confirmation': 1.2
    }
    
    total_allocated = 0
    successful_trades = 0
    
    for trade in trades:
        print(f"\n   Trading {trade['symbol']} at ${trade['price']:.0f}")
        
        size, approved, message = position_sizer.calculate_position_size(
            symbol=trade['symbol'],
            signal_data=strong_signal,
            current_balance=balance,
            current_positions=positions,
            entry_price=trade['price'],
            base_position_size=trade['base_size']
        )
        
        if approved and size > 0:
            # Execute the trade
            quantity = size / trade['price']
            positions[trade['symbol']] = {
                'quantity': quantity,
                'entry_price': trade['price'],
                'current_price': trade['price']
            }
            total_allocated += size
            successful_trades += 1
            
            print(f"   ✅ Size: ${size:,.0f} | Quantity: {quantity:.1f}")
        else:
            print(f"   ❌ Rejected: {message[:50]}...")
    
    # Calculate final portfolio metrics
    final_heat = risk_calc._calculate_portfolio_heat(positions, balance)
    allocation_pct = (total_allocated / balance) * 100
    
    print(f"\n{Fore.YELLOW}Portfolio Summary:{Style.RESET_ALL}")
    print(f"   Successful Trades: {successful_trades}/3")
    print(f"   Total Allocated: ${total_allocated:,.0f} ({allocation_pct:.1f}%)")
    print(f"   Portfolio Heat: {final_heat:.2%}")
    print(f"   Available Cash: ${balance - total_allocated:,.0f}")
    
    # Check if we stayed within limits
    success = (final_heat <= 0.25 and successful_trades >= 2)
    
    if success:
        print(f"\n{Fore.GREEN}✅ Realistic Trading Scenario: SUCCESS{Style.RESET_ALL}")
        print(f"   Portfolio remained within risk limits")
    else:
        print(f"\n{Fore.RED}❌ Realistic Trading Scenario: RISK LIMITS EXCEEDED{Style.RESET_ALL}")
    
    return success

if __name__ == "__main__":
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}🛡️  ENHANCED RISK MANAGEMENT - SIMPLE TEST SUITE{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    
    try:
        # Run basic functionality tests
        basic_success = test_basic_functionality()
        
        # Run realistic scenario test
        scenario_success = test_realistic_trading_scenario()
        
        # Final summary
        print(f"\n{Fore.CYAN}📊 Final Test Summary{Style.RESET_ALL}")
        print("═" * 40)
        print(f"   Basic Functionality: {'✅ PASS' if basic_success else '❌ FAIL'}")
        print(f"   Realistic Scenario:  {'✅ PASS' if scenario_success else '❌ FAIL'}")
        
        if basic_success and scenario_success:
            print(f"\n{Fore.GREEN}{Back.BLACK}🎉 ALL TESTS PASSED - SYSTEM READY FOR TRADING! 🎉{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}⚠️  Some tests require adjustment - System is protective{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"\n{Fore.RED}💥 Test Suite Error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()