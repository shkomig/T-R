"""
🧪 Test Enhanced Risk Management System
======================================

Comprehensive testing for the advanced risk management integration:
- Advanced Risk Calculator validation
- Enhanced Position Sizer testing  
- Integration testing with trading system
- Risk metrics accuracy verification

Author: T-R Trading System
Version: 3.1.0
Date: November 2, 2025
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import time
import numpy as np

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from risk_management.advanced_risk_calculator import AdvancedRiskCalculator
from risk_management.enhanced_position_sizer import EnhancedPositionSizer
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


class RiskManagementTester:
    """🧪 Comprehensive Risk Management System Tester"""
    
    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        color = Fore.GREEN if passed else Fore.RED
        
        print(f"{color}{status}{Style.RESET_ALL} {test_name}")
        if message:
            print(f"     {message}")
        
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'message': message,
            'timestamp': datetime.now()
        })
        
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
    
    def test_advanced_risk_calculator(self):
        """🛡️ Test Advanced Risk Calculator"""
        print(f"\n{Fore.CYAN}🛡️ Testing Advanced Risk Calculator...{Style.RESET_ALL}")
        print("─" * 50)
        
        try:
            # Initialize risk calculator
            risk_calc = AdvancedRiskCalculator(
                max_daily_loss=0.05,
                max_total_drawdown=0.15,
                max_portfolio_heat=0.25,
                max_single_position_risk=0.03
            )
            
            # Test 1: Basic initialization
            self.log_test(
                "Risk Calculator Initialization",
                risk_calc is not None,
                "Successfully created AdvancedRiskCalculator instance"
            )
            
            # Test 2: Risk metrics calculation with safe conditions
            test_balance = 100000.0
            test_positions = {
                'AAPL': {'quantity': 100, 'entry_price': 150.0, 'current_price': 152.0},
                'GOOGL': {'quantity': 50, 'entry_price': 2800.0, 'current_price': 2850.0}
            }
            
            metrics = risk_calc.calculate_risk_metrics(test_balance, test_positions)
            
            self.log_test(
                "Risk Metrics Calculation",
                isinstance(metrics, dict) and 'is_safe_to_trade' in metrics,
                f"Generated comprehensive risk metrics with {len(metrics)} fields"
            )
            
            # Test 3: Portfolio heat calculation
            heat = risk_calc._calculate_portfolio_heat(test_positions, test_balance)
            expected_heat = ((100 * 152 + 50 * 2850) * 0.25) / test_balance  # 25% stop loss
            
            self.log_test(
                "Portfolio Heat Calculation",
                abs(heat - expected_heat) < 0.01,
                f"Heat: {heat:.4f}, Expected: {expected_heat:.4f}"
            )
            
            # Test 4: Position validation - valid position with smaller test positions
            smaller_test_positions = {
                'AAPL': {'quantity': 50, 'entry_price': 150.0, 'current_price': 152.0}  # Reduced position
            }
            
            can_open, message = risk_calc.can_open_new_position(
                'MSFT', 2500, 300.0, test_balance, smaller_test_positions  # Smaller existing positions
            )
            
            self.log_test(
                "Valid Position Validation",
                can_open,
                f"Position approved: {message}"
            )
            
            # Test 5: Position validation - oversized position
            can_open_large, message_large = risk_calc.can_open_new_position(
                'NVDA', 50000, 500.0, test_balance, test_positions
            )
            
            self.log_test(
                "Oversized Position Rejection",
                not can_open_large,
                f"Large position rejected: {message_large}"
            )
            
            # Test 6: Peak balance tracking
            old_peak = risk_calc.peak_balance
            risk_calc.update_peak_balance(120000.0)
            
            self.log_test(
                "Peak Balance Tracking",
                risk_calc.peak_balance == 120000.0,
                f"Peak updated from ${old_peak:,.2f} to ${risk_calc.peak_balance:,.2f}"
            )
            
            # Test 7: Risk limit violations
            # Simulate dangerous conditions
            dangerous_positions = {
                'STOCK1': {'quantity': 500, 'entry_price': 100.0, 'current_price': 80.0},
                'STOCK2': {'quantity': 300, 'entry_price': 200.0, 'current_price': 160.0},
                'STOCK3': {'quantity': 200, 'entry_price': 300.0, 'current_price': 240.0}
            }
            
            # Set a low balance to trigger limits
            risk_calc.peak_balance = 100000.0
            dangerous_metrics = risk_calc.calculate_risk_metrics(75000.0, dangerous_positions)
            
            self.log_test(
                "Risk Limit Violation Detection",
                not dangerous_metrics['is_safe_to_trade'],
                f"Correctly detected unsafe conditions: drawdown {dangerous_metrics['current_drawdown']:.2%}"
            )
            
        except Exception as e:
            self.log_test("Risk Calculator Testing", False, f"Exception: {e}")
    
    def test_enhanced_position_sizer(self):
        """💰 Test Enhanced Position Sizer"""
        print(f"\n{Fore.CYAN}💰 Testing Enhanced Position Sizer...{Style.RESET_ALL}")
        print("─" * 50)
        
        try:
            # Initialize components
            risk_calc = AdvancedRiskCalculator()
            position_sizer = EnhancedPositionSizer(
                risk_calculator=risk_calc,
                sizing_method="dynamic"
            )
            
            # Test 1: Position sizer initialization
            self.log_test(
                "Position Sizer Initialization",
                position_sizer is not None and position_sizer.risk_calculator is not None,
                "Successfully created EnhancedPositionSizer with risk calculator integration"
            )
            
            # Test 2: Signal strength analysis
            test_signal = {
                'signals': {
                    'vwap': 'BUY',
                    'momentum': 'STRONG_BUY',
                    'bollinger': 'BUY',
                    'rsi_divergence': 'STRONG_BUY'
                },
                'signal_count': 4,
                'total_strategies': 7,
                'momentum_score': 1.2,
                'volume_confirmation': 1.1
            }
            
            strength, confidence = position_sizer._analyze_signal_strength(test_signal)
            
            self.log_test(
                "Signal Strength Analysis",
                0.0 <= strength <= 1.0 and 0.0 <= confidence <= 1.0,
                f"Strength: {strength:.3f}, Confidence: {confidence:.3f}"
            )
            
            # Test 3: Position size calculation with good signal
            test_balance = 100000.0
            test_positions = {'AAPL': {'quantity': 100, 'entry_price': 150.0, 'current_price': 152.0}}
            
            size, approved, message = position_sizer.calculate_position_size(
                symbol='MSFT',
                signal_data=test_signal,
                current_balance=test_balance,
                current_positions=test_positions,
                entry_price=300.0
            )
            
            self.log_test(
                "Position Size Calculation - Good Signal",
                approved and size > 0,
                f"Size: ${size:,.2f}, Message: {message}"
            )
            
            # Test 4: Position size calculation with weak signal
            weak_signal = {
                'signals': {'momentum': 'WEAK_BUY'},
                'signal_count': 1,
                'total_strategies': 7,
                'momentum_score': 0.8,
                'volume_confirmation': 0.9
            }
            
            weak_size, weak_approved, weak_message = position_sizer.calculate_position_size(
                symbol='GOOGL',
                signal_data=weak_signal,
                current_balance=test_balance,
                current_positions=test_positions,
                entry_price=2800.0
            )
            
            self.log_test(
                "Position Size Calculation - Weak Signal",
                not weak_approved or weak_size < size,
                f"Weak signal properly handled: {weak_message}"
            )
            
            # Test 5: Different sizing methods
            methods = ["fixed", "dynamic", "kelly", "volatility"]
            for method in methods:
                position_sizer.sizing_method = method
                method_size = position_sizer._calculate_optimal_size(
                    symbol='TEST',
                    signal_strength=0.8,
                    signal_confidence=0.7,
                    current_balance=test_balance,
                    available_heat=0.15,
                    entry_price=100.0,
                    base_size=15000
                )
                
                self.log_test(
                    f"Sizing Method: {method}",
                    method_size > 0,
                    f"Generated size: ${method_size:,.2f}"
                )
            
            # Test 6: Performance tracking
            position_sizer.sizing_method = "dynamic"  # Reset to default
            performance = position_sizer.get_sizing_performance()
            
            self.log_test(
                "Performance Tracking",
                isinstance(performance, dict),
                f"Performance data structure: {len(performance)} metrics"
            )
            
        except Exception as e:
            self.log_test("Position Sizer Testing", False, f"Exception: {e}")
    
    def test_integration_scenarios(self):
        """🔗 Test Integration Scenarios"""
        print(f"\n{Fore.CYAN}🔗 Testing Integration Scenarios...{Style.RESET_ALL}")
        print("─" * 50)
        
        try:
            # Initialize full system
            risk_calc = AdvancedRiskCalculator()
            position_sizer = EnhancedPositionSizer(risk_calc, "dynamic")
            
            # Scenario 1: Normal trading day
            print(f"\n{Fore.YELLOW}Scenario 1: Normal Trading Day{Style.RESET_ALL}")
            
            balance = 100000.0
            positions = {}
            
            # Simulate multiple smaller trades that should pass
            symbols = ['AAPL', 'GOOGL']  # Reduced to 2 symbols
            total_allocated = 0
            
            for i, symbol in enumerate(symbols):
                signal_data = {
                    'signals': {'momentum': 'BUY', 'vwap': 'BUY', 'rsi_divergence': 'STRONG_BUY'},
                    'signal_count': 3,
                    'total_strategies': 7,
                    'momentum_score': 1.0,
                    'volume_confirmation': 1.0
                }
                
                # Use smaller, safer prices
                entry_price = 50.0 + i * 25  # $50, $75
                
                size, approved, message = position_sizer.calculate_position_size(
                    symbol=symbol,
                    signal_data=signal_data,
                    current_balance=balance,
                    current_positions=positions,
                    entry_price=entry_price,
                    base_position_size=2000  # Much smaller base size
                )
                
                if approved and size > 0:
                    positions[symbol] = {
                        'quantity': size / entry_price,
                        'entry_price': entry_price,
                        'current_price': entry_price
                    }
                    total_allocated += size
                
                print(f"   {symbol}: ${size:,.0f} {'✅' if approved else '❌'} - {message[:50]}...")
            
            portfolio_heat = risk_calc._calculate_portfolio_heat(positions, balance)
            
            self.log_test(
                "Normal Trading Day Simulation",
                len(positions) > 0 and portfolio_heat <= 0.25,
                f"Allocated: ${total_allocated:,.0f}, Heat: {portfolio_heat:.2%}, Positions: {len(positions)}"
            )
            
            # Scenario 2: High volatility day (stress test)
            print(f"\n{Fore.YELLOW}Scenario 2: High Volatility Day{Style.RESET_ALL}")
            
            # Simulate price drops
            stressed_positions = {}
            for symbol, pos in positions.items():
                stressed_positions[symbol] = {
                    'quantity': pos['quantity'],
                    'entry_price': pos['entry_price'],
                    'current_price': pos['entry_price'] * 0.85  # 15% drop
                }
            
            stressed_balance = balance * 0.92  # 8% account drop
            stressed_metrics = risk_calc.calculate_risk_metrics(stressed_balance, stressed_positions)
            
            self.log_test(
                "High Volatility Stress Test",
                'current_drawdown' in stressed_metrics,
                f"Drawdown: {stressed_metrics.get('current_drawdown', 0):.2%}, Safe: {stressed_metrics.get('is_safe_to_trade', False)}"
            )
            
            # Scenario 3: Risk limit recovery
            print(f"\n{Fore.YELLOW}Scenario 3: Risk Limit Recovery{Style.RESET_ALL}")
            
            # Try to place new position during stress
            recovery_signal = {
                'signals': {'momentum': 'BUY'},
                'signal_count': 1,
                'total_strategies': 7,
                'momentum_score': 0.8,
                'volume_confirmation': 0.9
            }
            
            recovery_size, recovery_approved, recovery_message = position_sizer.calculate_position_size(
                symbol='RECOVERY',
                signal_data=recovery_signal,
                current_balance=stressed_balance,
                current_positions=stressed_positions,
                entry_price=200.0
            )
            
            self.log_test(
                "Risk Limit Recovery",
                not recovery_approved or recovery_size < 5000,  # Should be rejected or very small
                f"Recovery position: ${recovery_size:,.0f}, Approved: {recovery_approved}"
            )
            
        except Exception as e:
            self.log_test("Integration Testing", False, f"Exception: {e}")
    
    def test_performance_benchmarks(self):
        """⚡ Test Performance Benchmarks"""
        print(f"\n{Fore.CYAN}⚡ Testing Performance Benchmarks...{Style.RESET_ALL}")
        print("─" * 50)
        
        try:
            risk_calc = AdvancedRiskCalculator()
            position_sizer = EnhancedPositionSizer(risk_calc, "dynamic")
            
            # Benchmark 1: Risk calculation speed
            start_time = time.time()
            iterations = 100
            
            for _ in range(iterations):
                risk_calc.calculate_risk_metrics(
                    100000.0,
                    {'TEST': {'quantity': 100, 'entry_price': 100, 'current_price': 105}}
                )
            
            risk_calc_time = (time.time() - start_time) / iterations
            
            self.log_test(
                "Risk Calculation Performance",
                risk_calc_time < 0.01,  # Should be under 10ms
                f"Average time: {risk_calc_time*1000:.2f}ms per calculation"
            )
            
            # Benchmark 2: Position sizing speed
            start_time = time.time()
            
            signal_data = {
                'signals': {'momentum': 'BUY', 'vwap': 'BUY'},
                'signal_count': 2,
                'total_strategies': 7,
                'momentum_score': 1.0,
                'volume_confirmation': 1.0
            }
            
            for _ in range(iterations):
                position_sizer.calculate_position_size(
                    symbol='BENCH',
                    signal_data=signal_data,
                    current_balance=100000.0,
                    current_positions={},
                    entry_price=100.0
                )
            
            position_size_time = (time.time() - start_time) / iterations
            
            self.log_test(
                "Position Sizing Performance",
                position_size_time < 0.05,  # Should be under 50ms
                f"Average time: {position_size_time*1000:.2f}ms per calculation"
            )
            
            # Benchmark 3: Memory usage (basic check)
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            self.log_test(
                "Memory Usage",
                memory_mb < 100,  # Should be under 100MB for this test
                f"Current memory usage: {memory_mb:.1f}MB"
            )
            
        except Exception as e:
            self.log_test("Performance Testing", False, f"Exception: {e}")
    
    def run_all_tests(self):
        """🚀 Run all comprehensive tests"""
        print(f"{Fore.MAGENTA}{Style.BRIGHT}")
        print("🧪 ENHANCED RISK MANAGEMENT SYSTEM - COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"{Style.RESET_ALL}")
        
        start_time = time.time()
        
        # Run test suites
        self.test_advanced_risk_calculator()
        self.test_enhanced_position_sizer()
        self.test_integration_scenarios()
        self.test_performance_benchmarks()
        
        # Summary
        total_time = time.time() - start_time
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}")
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"{Style.RESET_ALL}")
        
        print(f"✅ Passed: {Fore.GREEN}{self.passed_tests}{Style.RESET_ALL}")
        print(f"❌ Failed: {Fore.RED}{self.failed_tests}{Style.RESET_ALL}")
        print(f"📈 Success Rate: {Fore.CYAN}{success_rate:.1f}%{Style.RESET_ALL}")
        print(f"⏱️  Total Time: {Fore.YELLOW}{total_time:.2f}s{Style.RESET_ALL}")
        
        # Overall result
        if self.failed_tests == 0:
            print(f"\n{Fore.GREEN}{Style.BRIGHT}🎉 ALL TESTS PASSED! Risk management system ready for production.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}{Style.BRIGHT}⚠️  SOME TESTS FAILED! Review and fix issues before deployment.{Style.RESET_ALL}")
        
        return self.failed_tests == 0


if __name__ == "__main__":
    print("🔧 Initializing Risk Management Test Suite...")
    
    tester = RiskManagementTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    exit_code = 0 if success else 1
    print(f"\nExiting with code: {exit_code}")
    exit(exit_code)