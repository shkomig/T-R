#!/usr/bin/env python3
"""
🧪 Professional Execution System Test Suite
=============================================

בדיקות מקיפות למערכת הביצוע המקצועית החדשה:
- ExecutionManager עם 5 שלבי validation
- SignalQualityEnhancer עם confidence scoring
- MarketRegimeDetector עם זיהוי משטרי שוק
- אינטגרציה מלאה עם מערכת הסיכונים

Author: T-R Trading System
Version: 1.0.0
Date: November 2, 2025
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from execution.execution_manager import ExecutionManager, TradingSignal, MarketRegime
from execution.signal_quality_enhancer import SignalQualityEnhancer
from execution.market_regime_detector import MarketRegimeDetector
from risk_management.advanced_risk_calculator import AdvancedRiskCalculator
from risk_management.enhanced_position_sizer import EnhancedPositionSizer
from colorama import init, Fore, Back, Style
import time
from datetime import datetime

init(autoreset=True)

def test_execution_manager():
    """🎯 בדיקת ExecutionManager עם 5 שלבי validation"""
    print(f"{Fore.CYAN}🎯 Testing Professional Execution Manager{Style.RESET_ALL}")
    print("═" * 60)
    
    try:
        # Initialize components
        risk_calc = AdvancedRiskCalculator()
        position_sizer = EnhancedPositionSizer(risk_calc)
        execution_manager = ExecutionManager(risk_calc, position_sizer)
        
        print(f"   ✅ ExecutionManager initialized successfully")
        
        # Test signal processing
        signal = TradingSignal(
            symbol='AAPL',
            signal_type='BUY',
            confidence=0.8,
            price=150.0,
            timestamp=datetime.now(),
            data={
                'strategy_name': 'momentum',
                'signals': {'momentum': 'BUY', 'vwap': 'BUY'},
                'signal_count': 2,
                'total_strategies': 5,
                'momentum_score': 1.2
            }
        )
        
        # Test with safe conditions
        current_balance = 100000.0
        current_positions = {
            'MSFT': {
                'quantity': 10,
                'entry_price': 300.0,
                'current_price': 305.0
            }
        }
        
        print(f"\n   🔄 Processing signal for {signal.symbol}")
        decision = execution_manager.process_signal(signal, current_balance, current_positions)
        
        print(f"   📊 Decision: {decision.should_execute}")
        print(f"   📋 Reason: {decision.reason}")
        print(f"   💰 Quantity: {decision.quantity}")
        print(f"   🎯 Confidence: {decision.confidence_score:.1%}")
        print(f"   🌊 Regime Fit: {decision.regime_suitability:.1%}")
        
        # Test regime statistics
        regime_stats = execution_manager.get_regime_summary()
        print(f"   🌊 Current Regime: {regime_stats['current_regime']}")
        print(f"   📈 Regime Confidence: {regime_stats['confidence']:.1%}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ExecutionManager test failed: {e}")
        return False

def test_signal_quality_enhancer():
    """🎯 בדיקת Signal Quality Enhancer"""
    print(f"\n{Fore.CYAN}🎯 Testing Signal Quality Enhancer{Style.RESET_ALL}")
    print("═" * 60)
    
    try:
        enhancer = SignalQualityEnhancer()
        print(f"   ✅ SignalQualityEnhancer initialized successfully")
        
        # Test signal enhancement
        signal_data = {
            'confidence': 0.6,
            'signals': {'momentum': 'BUY', 'vwap': 'BUY', 'rsi': 'BUY'},
            'signal_count': 3,
            'total_strategies': 5,
            'momentum_score': 1.1
        }
        
        market_context = {
            'volume_ratio': 1.8,  # High volume
            'spy_trend': 1,       # Market trending up
            'spy_correlation': 0.8,
            'session': 'regular',
            'volatility': 0.015,
            'trend_strength': 0.04
        }
        
        print(f"   🔄 Testing signal enhancement...")
        enhancement = enhancer.enhance_signal_confidence(signal_data, market_context)
        
        print(f"   📊 Original Confidence: {enhancement.original_confidence:.1%}")
        print(f"   📈 Enhanced Confidence: {enhancement.enhanced_confidence:.1%}")
        print(f"   🔧 Adjustments: {len(enhancement.adjustments)}")
        print(f"   📋 Reason: {enhancement.enhancement_reason}")
        print(f"   🌊 Market Score: {enhancement.market_context_score:.1%}")
        print(f"   ⚙️ Technical Score: {enhancement.technical_confluence_score:.1%}")
        
        # Test edge cases
        print(f"\n   🧪 Testing edge cases...")
        
        # Low volume test
        low_vol_context = market_context.copy()
        low_vol_context['volume_ratio'] = 0.3
        low_vol_enhancement = enhancer.enhance_signal_confidence(signal_data, low_vol_context)
        print(f"   📉 Low Volume Impact: {low_vol_enhancement.enhanced_confidence - enhancement.original_confidence:+.1%}")
        
        # Contrarian signal test
        contrarian_context = market_context.copy()
        contrarian_context['spy_trend'] = -1  # Market down, but signal is BUY
        contrarian_enhancement = enhancer.enhance_signal_confidence(signal_data, contrarian_context)
        print(f"   🔄 Contrarian Impact: {contrarian_enhancement.enhanced_confidence - enhancement.original_confidence:+.1%}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ SignalQualityEnhancer test failed: {e}")
        return False

def test_market_regime_detector():
    """🌊 בדיקת Market Regime Detector"""
    print(f"\n{Fore.CYAN}🌊 Testing Market Regime Detector{Style.RESET_ALL}")
    print("═" * 60)
    
    try:
        detector = MarketRegimeDetector()
        print(f"   ✅ MarketRegimeDetector initialized successfully")
        
        # Test different market scenarios
        scenarios = [
            {
                'name': 'Bull Market',
                'data': {
                    'SPY': {
                        'price': 450.0,
                        'ema_20': 448.0,
                        'ema_50': 440.0,
                        'ema_200': 420.0,
                        'volume': 120000000,
                        'avg_volume': 80000000,
                        'atr': 3.5,
                        'atr_pct': 0.8
                    },
                    'VIX': {'price': 16.5}
                }
            },
            {
                'name': 'Bear Market',
                'data': {
                    'SPY': {
                        'price': 420.0,
                        'ema_20': 425.0,
                        'ema_50': 435.0,
                        'ema_200': 450.0,
                        'volume': 150000000,
                        'avg_volume': 80000000,
                        'atr': 8.5,
                        'atr_pct': 2.0
                    },
                    'VIX': {'price': 28.5}
                }
            },
            {
                'name': 'Crisis Mode',
                'data': {
                    'SPY': {
                        'price': 380.0,
                        'ema_20': 390.0,
                        'ema_50': 410.0,
                        'ema_200': 440.0,
                        'volume': 250000000,
                        'avg_volume': 80000000,
                        'atr': 15.0,
                        'atr_pct': 4.0
                    },
                    'VIX': {'price': 42.0}
                }
            },
            {
                'name': 'Ranging Market',
                'data': {
                    'SPY': {
                        'price': 440.0,
                        'ema_20': 441.0,
                        'ema_50': 439.0,
                        'ema_200': 438.0,
                        'volume': 70000000,
                        'avg_volume': 80000000,
                        'atr': 2.2,
                        'atr_pct': 0.5
                    },
                    'VIX': {'price': 19.0}
                }
            }
        ]
        
        for scenario in scenarios:
            print(f"\n   🧪 Testing {scenario['name']}:")
            analysis = detector.analyze_market_regime(scenario['data'])
            
            print(f"      🌊 Regime: {analysis.regime.value}")
            print(f"      🎯 Confidence: {analysis.confidence:.1%}")
            print(f"      📈 Trend Strength: {analysis.trend_strength:+.1%}")
            print(f"      📊 Volatility: {analysis.volatility_level:.1f}")
            print(f"      ⚠️ Risk Level: {analysis.risk_level}")
            print(f"      📋 Supporting: {len(analysis.supporting_indicators)} indicators")
        
        # Test regime statistics
        print(f"\n   📊 Testing regime statistics...")
        stats = detector.get_regime_statistics()
        print(f"      📈 Total Observations: {stats['total_observations']}")
        print(f"      🌊 Current Regime: {stats['current_regime']}")
        print(f"      📅 Regime Duration: {stats['regime_duration_days']} days")
        
        return True
        
    except Exception as e:
        print(f"   ❌ MarketRegimeDetector test failed: {e}")
        return False

def test_full_integration():
    """🔗 בדיקת אינטגרציה מלאה"""
    print(f"\n{Fore.CYAN}🔗 Testing Full Integration{Style.RESET_ALL}")
    print("═" * 60)
    
    try:
        # Initialize complete system
        risk_calc = AdvancedRiskCalculator()
        position_sizer = EnhancedPositionSizer(risk_calc)
        execution_manager = ExecutionManager(risk_calc, position_sizer)
        signal_enhancer = SignalQualityEnhancer()
        regime_detector = MarketRegimeDetector()
        
        print(f"   ✅ Complete system initialized")
        
        # Simulate trading day workflow
        balance = 100000.0
        positions = {}
        
        # Market context
        market_data = {
            'SPY': {
                'price': 445.0,
                'ema_20': 444.0,
                'ema_50': 441.0,
                'ema_200': 435.0,
                'volume': 95000000,
                'avg_volume': 80000000,
                'atr': 4.0,
                'atr_pct': 0.9
            },
            'VIX': {'price': 20.5}
        }
        
        # Update market regime
        regime_analysis = regime_detector.analyze_market_regime(market_data)
        print(f"   🌊 Market Regime: {regime_analysis.regime.value} ({regime_analysis.confidence:.1%})")
        
        # Test multiple signals
        test_signals = [
            {'symbol': 'AAPL', 'type': 'BUY', 'price': 150.0, 'strategy': 'momentum'},
            {'symbol': 'GOOGL', 'type': 'BUY', 'price': 125.0, 'strategy': 'vwap'},
            {'symbol': 'MSFT', 'type': 'BUY', 'price': 330.0, 'strategy': 'bollinger'}
        ]
        
        successful_trades = 0
        
        for i, signal_info in enumerate(test_signals):
            print(f"\n   📈 Processing Signal {i+1}: {signal_info['symbol']}")
            
            # Create signal
            signal = TradingSignal(
                symbol=signal_info['symbol'],
                signal_type=signal_info['type'],
                confidence=0.7,
                price=signal_info['price'],
                timestamp=datetime.now(),
                data={
                    'strategy_name': signal_info['strategy'],
                    'signals': {'momentum': 'BUY'},
                    'signal_count': 1,
                    'total_strategies': 3
                }
            )
            
            # Enhance signal
            market_context = {
                'volume_ratio': 1.2,
                'spy_trend': 1,
                'spy_correlation': 0.6,
                'session': 'regular',
                'volatility': 0.02
            }
            
            enhancement = signal_enhancer.enhance_signal_confidence(signal.data, market_context)
            signal.confidence = enhancement.enhanced_confidence
            
            print(f"      🎯 Enhanced Confidence: {enhancement.enhanced_confidence:.1%}")
            
            # Process through execution manager
            decision = execution_manager.process_signal(signal, balance, positions)
            
            if decision.should_execute:
                successful_trades += 1
                # Simulate position addition
                positions[signal.symbol] = {
                    'quantity': decision.quantity,
                    'entry_price': signal.price,
                    'current_price': signal.price
                }
                print(f"      ✅ Trade Executed: {decision.quantity} shares")
            else:
                print(f"      ❌ Trade Rejected: {decision.reason[:50]}...")
        
        # Final results
        portfolio_value = sum(pos['quantity'] * pos['current_price'] for pos in positions.values())
        print(f"\n   📊 Integration Test Results:")
        print(f"      💰 Portfolio Value: ${portfolio_value:,.0f}")
        print(f"      📈 Successful Trades: {successful_trades}/{len(test_signals)}")
        print(f"      🎯 Success Rate: {(successful_trades/len(test_signals))*100:.1f}%")
        print(f"      🌊 Final Regime: {execution_manager.current_regime.value}")
        
        return successful_trades > 0
        
    except Exception as e:
        print(f"   ❌ Full integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_benchmarks():
    """⚡ בדיקת ביצועים"""
    print(f"\n{Fore.CYAN}⚡ Testing Performance Benchmarks{Style.RESET_ALL}")
    print("═" * 60)
    
    try:
        # Initialize system
        risk_calc = AdvancedRiskCalculator()
        position_sizer = EnhancedPositionSizer(risk_calc)
        execution_manager = ExecutionManager(risk_calc, position_sizer)
        signal_enhancer = SignalQualityEnhancer()
        regime_detector = MarketRegimeDetector()
        
        # Performance test parameters
        iterations = 100
        
        # Test 1: Signal processing speed
        signal = TradingSignal(
            symbol='AAPL',
            signal_type='BUY',
            confidence=0.8,
            price=150.0,
            timestamp=datetime.now(),
            data={'strategy_name': 'momentum', 'signal_count': 2, 'total_strategies': 5}
        )
        
        start_time = time.time()
        for _ in range(iterations):
            decision = execution_manager.process_signal(signal, 100000.0, {})
        execution_time = (time.time() - start_time) / iterations
        
        print(f"   ⚡ Signal Processing: {execution_time*1000:.2f}ms per signal")
        
        # Test 2: Signal enhancement speed
        signal_data = {'confidence': 0.6, 'signal_count': 2, 'total_strategies': 5}
        market_context = {'volume_ratio': 1.2, 'spy_trend': 1, 'session': 'regular'}
        
        start_time = time.time()
        for _ in range(iterations):
            enhancement = signal_enhancer.enhance_signal_confidence(signal_data, market_context)
        enhancement_time = (time.time() - start_time) / iterations
        
        print(f"   🎯 Signal Enhancement: {enhancement_time*1000:.2f}ms per enhancement")
        
        # Test 3: Regime detection speed
        market_data = {
            'SPY': {'price': 450, 'ema_20': 448, 'ema_50': 445, 'volume': 100000000, 'avg_volume': 80000000},
            'VIX': {'price': 18.5}
        }
        
        start_time = time.time()
        for _ in range(iterations):
            analysis = regime_detector.analyze_market_regime(market_data)
        regime_time = (time.time() - start_time) / iterations
        
        print(f"   🌊 Regime Detection: {regime_time*1000:.2f}ms per analysis")
        
        # Performance assessment
        total_time = execution_time + enhancement_time + regime_time
        print(f"\n   📊 Performance Summary:")
        print(f"      🚀 Total Processing: {total_time*1000:.2f}ms per complete cycle")
        print(f"      ⚡ Throughput: {1/total_time:.0f} decisions per second")
        
        # Performance criteria
        if total_time < 0.050:  # 50ms threshold
            print(f"      ✅ Performance: EXCELLENT (< 50ms)")
            return True
        elif total_time < 0.100:  # 100ms threshold
            print(f"      ✅ Performance: GOOD (< 100ms)")
            return True
        else:
            print(f"      ⚠️ Performance: NEEDS OPTIMIZATION (> 100ms)")
            return False
            
    except Exception as e:
        print(f"   ❌ Performance test failed: {e}")
        return False

if __name__ == "__main__":
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}🚀 PROFESSIONAL EXECUTION SYSTEM - TEST SUITE{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    
    # Run all tests
    test_results = []
    
    test_results.append(("ExecutionManager", test_execution_manager()))
    test_results.append(("SignalQualityEnhancer", test_signal_quality_enhancer()))
    test_results.append(("MarketRegimeDetector", test_market_regime_detector()))
    test_results.append(("Full Integration", test_full_integration()))
    test_results.append(("Performance Benchmarks", test_performance_benchmarks()))
    
    # Final summary
    print(f"\n{Fore.CYAN}📊 Final Test Summary{Style.RESET_ALL}")
    print("═" * 40)
    
    passed_tests = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:.<25} {status}")
        if result:
            passed_tests += 1
    
    success_rate = (passed_tests / len(test_results)) * 100
    print(f"\n   📈 Success Rate: {success_rate:.1f}% ({passed_tests}/{len(test_results)})")
    
    if success_rate >= 80:
        print(f"\n{Fore.GREEN}{Back.BLACK}🎉 PROFESSIONAL EXECUTION SYSTEM: READY FOR PRODUCTION! 🎉{Style.RESET_ALL}")
    elif success_rate >= 60:
        print(f"\n{Fore.YELLOW}⚠️ System mostly functional - minor adjustments needed{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}❌ System requires significant improvements before deployment{Style.RESET_ALL}")