#!/usr/bin/env python3
"""
🎯 Professional Trading System - Full Simulation Mode
====================================================

מצב סימולציה מלא למערכת המסחר המקצועית:
- עובד ללא TWS/חיבור לשוק
- נתונים מדומים אמיתיים
- בדיקה מלאה של המערכת המקצועית
- מושלם לסוף השבוע/בדיקות

Author: T-R Trading System  
Version: 2.0.0
Date: November 2, 2025
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import time
import random
import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from colorama import Fore, Back, Style, init
from dataclasses import dataclass

sys.path.append(str(Path(__file__).parent))

# Import professional execution components
from execution.execution_manager import ExecutionManager, ExecutionDecision, TradingSignal
from execution.signal_quality_enhancer import SignalQualityEnhancer
from execution.market_regime_detector import MarketRegimeDetector, RegimeAnalysis
from risk_management.advanced_risk_calculator import AdvancedRiskCalculator
from risk_management.enhanced_position_sizer import EnhancedPositionSizer

# Initialize colorama
init(autoreset=True)

@dataclass
class SimulatedPosition:
    """פוזיציה מדומה"""
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    entry_time: datetime
    
    @property
    def pnl(self) -> float:
        return (self.current_price - self.entry_price) * self.quantity
    
    @property
    def pnl_pct(self) -> float:
        return (self.current_price - self.entry_price) / self.entry_price * 100

class ProfessionalSimulationDashboard:
    """מערכת סימולציה מלאה למערכת המקצועית"""
    
    def __init__(self):
        self.is_running = False
        self.simulation_speed = 1.0  # 1.0 = זמן אמת, 2.0 = פי 2 יותר מהר
        self.current_balance = 100000.0
        self.positions: Dict[str, SimulatedPosition] = {}
        self.trade_history = []
        self.cycle_count = 0
        
        # סמלים לסימולציה
        self.symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'NFLX',
            'QCOM', 'AMD', 'INTC', 'CRM', 'ORCL', 'ADBE', 'NOW', 'PYPL'
        ]
        
        # מחירים בסיסיים (מדומים)
        self.base_prices = {
            'AAPL': 175.0, 'MSFT': 350.0, 'GOOGL': 140.0, 'AMZN': 145.0,
            'NVDA': 450.0, 'META': 320.0, 'TSLA': 220.0, 'NFLX': 450.0,
            'QCOM': 160.0, 'AMD': 140.0, 'INTC': 50.0, 'CRM': 250.0,
            'ORCL': 110.0, 'ADBE': 580.0, 'NOW': 750.0, 'PYPL': 65.0
        }
        
        # אתחול המערכות המקצועיות
        self._initialize_professional_systems()
        
        print(f"{Fore.GREEN}🎯 Professional Simulation Dashboard Initialized{Style.RESET_ALL}")
        print(f"   💰 Starting Balance: ${self.current_balance:,.0f}")
        print(f"   📊 Symbols: {len(self.symbols)}")
        print(f"   🚀 Professional Execution: ENABLED")
    
    def _initialize_professional_systems(self):
        """אתחול המערכות המקצועיות"""
        try:
            # Advanced Risk Management
            self.risk_calculator = AdvancedRiskCalculator()
            self.position_sizer = EnhancedPositionSizer(self.risk_calculator)
            
            # Professional Execution System
            self.execution_manager = ExecutionManager(self.risk_calculator, self.position_sizer)
            self.signal_enhancer = SignalQualityEnhancer()
            self.regime_detector = MarketRegimeDetector()
            
            print(f"   ✅ Advanced Risk Calculator initialized")
            print(f"   ✅ Enhanced Position Sizer initialized") 
            print(f"   ✅ Professional Execution Manager initialized")
            print(f"   ✅ Signal Quality Enhancer initialized")
            print(f"   ✅ Market Regime Detector initialized")
            
        except Exception as e:
            print(f"   ❌ Error initializing professional systems: {e}")
            # Fallback
            self.risk_calculator = None
            self.position_sizer = None
            self.execution_manager = None
            self.signal_enhancer = None
            self.regime_detector = None
    
    def _generate_realistic_price(self, symbol: str) -> float:
        """יצירת מחיר אמיתי עם תנועות אמיתיות"""
        base_price = self.base_prices[symbol]
        
        # תנועה יומית בסיסית (-3% עד +3%)
        daily_change = random.uniform(-0.03, 0.03)
        
        # תנועה קצרת טווח (-1% עד +1%)
        short_term_noise = random.uniform(-0.01, 0.01)
        
        # חלק מהמניות יותר תנודתיות
        volatility_multiplier = 1.0
        if symbol in ['TSLA', 'NVDA', 'AMD']:
            volatility_multiplier = 1.5
        elif symbol in ['AAPL', 'MSFT', 'GOOGL']:
            volatility_multiplier = 0.8
            
        total_change = (daily_change + short_term_noise) * volatility_multiplier
        current_price = base_price * (1 + total_change)
        
        return round(current_price, 2)
    
    def _generate_market_signals(self, symbol: str, price: float) -> Dict:
        """יצירת סיגנלים אמיתיים לאסטרטגיות"""
        signals = {}
        signal_count = 0
        
        # VWAP Strategy (נפח מול מחיר)
        vwap_signal = random.choice(['H', 'L', 'H', 'L', 'H'])  # גם H = High confidence
        signals['vwap'] = vwap_signal
        if vwap_signal == 'H':
            signal_count += 1
        
        # Momentum Strategy  
        momentum_bias = random.uniform(-1, 1)
        if momentum_bias > 0.3:
            signals['momentum'] = 'BUY'
            signal_count += 1
        elif momentum_bias < -0.3:
            signals['momentum'] = 'SELL'
            signal_count += 1
        else:
            signals['momentum'] = 'HOLD'
        
        # Bollinger Bands
        bb_signal = random.choice(['BUY', 'SELL', 'HOLD', 'BUY', 'HOLD'])
        signals['bollinger'] = bb_signal
        if bb_signal in ['BUY', 'SELL']:
            signal_count += 1
            
        # Mean Reversion
        mr_signal = random.choice(['BUY', 'SELL', 'HOLD', 'HOLD', 'HOLD'])
        signals['mean_reversion'] = mr_signal
        if mr_signal in ['BUY', 'SELL']:
            signal_count += 1
            
        # RSI Divergence  
        rsi_signal = random.choice(['H', 'L', 'H', 'L', 'L'])
        signals['rsi'] = rsi_signal
        if rsi_signal == 'H':
            signal_count += 1
        
        # Volume Breakout
        vol_signal = random.choice(['H', 'L', 'H', 'H', 'L'])
        signals['volume'] = vol_signal
        if vol_signal == 'H':
            signal_count += 1
        
        # Pairs Trading
        pairs_signal = random.choice(['H', 'L', 'H', 'L', 'H'])
        signals['pairs'] = pairs_signal
        if pairs_signal == 'H':
            signal_count += 1
        
        return {
            'signals': signals,
            'signal_count': signal_count,
            'total_strategies': 7,
            'momentum_score': abs(momentum_bias),
            'volume_confirmation': random.uniform(0.8, 1.5),
            'volatility': random.uniform(0.01, 0.04)
        }
    
    def _get_trading_signal(self, symbol: str, signals: Dict) -> Optional[str]:
        """קביעת סיגנל מסחר על בסיס האסטרטגיות"""
        buy_signals = sum(1 for s in signals['signals'].values() if s in ['BUY', 'H'])
        sell_signals = sum(1 for s in signals['signals'].values() if s in ['SELL', 'L'])
        
        # דרישה לקונצנזוס של לפחות 3 אסטרטגיות
        if buy_signals >= 3 and buy_signals > sell_signals:
            return 'BUY'
        elif sell_signals >= 3 and sell_signals > buy_signals:
            return 'SELL'
        else:
            return None
    
    def _execute_professional_trade(self, symbol: str, signal: str, price: float, signal_data: Dict):
        """ביצוע מסחר מקצועי עם המערכת החדשה"""
        try:
            print(f"    🚀 PROFESSIONAL EXECUTION for {symbol}")
            
            # יצירת TradingSignal
            trading_signal = TradingSignal(
                symbol=symbol,
                signal_type=signal,
                confidence=0.65,  # ביטחון בסיסי
                price=price,
                timestamp=datetime.now(),
                data=signal_data
            )
            
            print(f"    🔍 DEBUG: TradingSignal confidence: {trading_signal.confidence:.2f}")
            print(f"    🔍 DEBUG: Signal data: signal_count={signal_data.get('signal_count', 0)}")
            
            # יצירת נתוני הקשר שוק
            market_context = {
                'SPY': {
                    'price': 440.0 + random.uniform(-5, 5),
                    'ema_20': 438.0,
                    'ema_50': 435.0,
                    'ema_200': 430.0,
                    'volume': random.randint(80000000, 120000000),
                    'avg_volume': 80000000,
                    'atr': random.uniform(3.0, 5.0),
                    'atr_pct': random.uniform(0.7, 1.2)
                },
                'VIX': {'price': random.uniform(15.0, 25.0)},
                'volume_ratio': signal_data.get('volume_confirmation', 1.0),
                'spy_trend': random.choice([-1, 1]),
                'spy_correlation': random.uniform(0.3, 0.8),
                'session': 'regular',
                'volatility': signal_data.get('volatility', 0.02)
            }
            
            # עדכון detector
            if self.regime_detector:
                regime_analysis = self.regime_detector.analyze_market_regime(market_context)
                print(f"    🌊 Market Regime: {regime_analysis.regime.value} ({regime_analysis.confidence:.1%})")
            
            # שיפור סיגנל
            if self.signal_enhancer:
                enhancement = self.signal_enhancer.enhance_signal_confidence(
                    signal_data, market_context
                )
                trading_signal.confidence = enhancement.enhanced_confidence
                print(f"    🎯 Signal enhanced: {enhancement.original_confidence:.1%} → {enhancement.enhanced_confidence:.1%}")
            
            # פורמט פוזיציות עבור ExecutionManager
            formatted_positions = {}
            for sym, pos in self.positions.items():
                formatted_positions[sym] = {
                    'quantity': pos.quantity,
                    'entry_price': pos.entry_price,
                    'current_price': pos.current_price
                }
            
            # עיבוד דרך ExecutionManager
            if self.execution_manager:
                decision = self.execution_manager.process_signal(
                    trading_signal, self.current_balance, formatted_positions
                )
                
                print(f"    🎯 DECISION: {decision.reason}")
                
                if decision.should_execute and decision.quantity > 0:
                    # ביצוע העסקה
                    self._execute_simulated_trade(symbol, signal, price, decision.quantity)
                    return True
                else:
                    print(f"    ⏸️ Trade rejected by professional system")
                    return False
            else:
                print(f"    ⚠️ ExecutionManager not available - using fallback")
                return False
                
        except Exception as e:
            print(f"    ❌ Professional execution error: {e}")
            return False
    
    def _execute_simulated_trade(self, symbol: str, signal: str, price: float, quantity: float):
        """ביצוע עסקה מדומה"""
        try:
            if signal == 'BUY':
                # רכישה
                cost = price * quantity
                if cost <= self.current_balance:
                    self.current_balance -= cost
                    self.positions[symbol] = SimulatedPosition(
                        symbol=symbol,
                        quantity=quantity,
                        entry_price=price,
                        current_price=price,
                        entry_time=datetime.now()
                    )
                    self.trade_history.append({
                        'time': datetime.now(),
                        'symbol': symbol,
                        'action': signal,
                        'quantity': quantity,
                        'price': price,
                        'cost': cost
                    })
                    print(f"       ✅ BUY executed: {quantity} shares at ${price:.2f}")
                    return True
            
            elif signal == 'SELL' and symbol in self.positions:
                # מכירה
                pos = self.positions[symbol]
                revenue = price * pos.quantity
                self.current_balance += revenue
                
                self.trade_history.append({
                    'time': datetime.now(),
                    'symbol': symbol,
                    'action': signal,
                    'quantity': pos.quantity,
                    'price': price,
                    'revenue': revenue,
                    'pnl': pos.pnl
                })
                
                print(f"       ✅ SELL executed: {pos.quantity} shares at ${price:.2f}")
                print(f"       💰 P&L: ${pos.pnl:+.2f} ({pos.pnl_pct:+.1f}%)")
                
                del self.positions[symbol]
                return True
                
        except Exception as e:
            print(f"       ❌ Trade execution failed: {e}")
            return False
        
        return False
    
    def _update_position_prices(self):
        """עדכון מחירי פוזיציות"""
        for symbol, position in self.positions.items():
            position.current_price = self._generate_realistic_price(symbol)
    
    def _display_status(self):
        """הצגת סטטוס המערכת"""
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🎯 PROFESSIONAL SIMULATION DASHBOARD - CYCLE #{self.cycle_count}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        
        # סטטוס כללי
        total_portfolio_value = self.current_balance
        total_pnl = 0.0
        
        if self.positions:
            for pos in self.positions.values():
                total_portfolio_value += pos.current_price * pos.quantity
                total_pnl += pos.pnl
        
        print(f"💰 Cash Balance:      ${self.current_balance:>12,.2f}")
        print(f"📊 Portfolio Value:   ${total_portfolio_value:>12,.2f}")
        print(f"📈 Total P&L:         ${total_pnl:>12,.2f}")
        print(f"📍 Active Positions:  {len(self.positions):>12}")
        print(f"🔄 Completed Trades:  {len(self.trade_history):>12}")
        
        # פוזיציות פעילות
        if self.positions:
            print(f"\n📋 ACTIVE POSITIONS:")
            print("─" * 80)
            for symbol, pos in self.positions.items():
                pnl_color = Fore.GREEN if pos.pnl >= 0 else Fore.RED
                print(f"   {symbol:<6} | Qty: {pos.quantity:>6.0f} | Entry: ${pos.entry_price:>6.2f} | "
                      f"Current: ${pos.current_price:>6.2f} | "
                      f"{pnl_color}P&L: ${pos.pnl:>8.2f} ({pos.pnl_pct:>+5.1f}%){Style.RESET_ALL}")
        
        # סטטיסטיקות מקצועיות
        if self.execution_manager:
            try:
                regime_stats = self.execution_manager.get_regime_summary()
                print(f"\n🌊 PROFESSIONAL SYSTEM STATUS:")
                print("─" * 50)
                print(f"   Current Regime: {regime_stats['current_regime']}")
                print(f"   Regime Confidence: {regime_stats['confidence']:.1%}")
            except:
                pass
    
    def run_simulation_cycle(self):
        """הרצת מחזור סימולציה אחד"""
        self.cycle_count += 1
        self._update_position_prices()
        
        print(f"\n{Fore.YELLOW}🔄 MARKET SCAN CYCLE #{self.cycle_count}{Style.RESET_ALL}")
        print("─" * 60)
        
        signals_processed = 0
        trades_executed = 0
        
        # בדיקת כל הסמלים
        for symbol in self.symbols:
            current_price = self._generate_realistic_price(symbol)
            signal_data = self._generate_market_signals(symbol, current_price)
            trading_signal = self._get_trading_signal(symbol, signal_data)
            
            if trading_signal:
                signals_processed += 1
                signal_display = "🔺 BUY" if trading_signal == 'BUY' else "🔻 SELL"
                confidence = signal_data['signal_count'] / signal_data['total_strategies']
                
                print(f"   {symbol:<6} | ${current_price:>7.2f} | {signal_display} | "
                      f"Confidence: {confidence:.1%} | Signals: {signal_data['signal_count']}/7")
                
                # ביצוע מקצועי
                if self._execute_professional_trade(symbol, trading_signal, current_price, signal_data):
                    trades_executed += 1
        
        print(f"\n📊 Cycle Summary: {signals_processed} signals, {trades_executed} trades executed")
        
        return signals_processed, trades_executed
    
    def run_simulation(self, cycles: int = 10, delay: float = 3.0):
        """הרצת סימולציה מלאה"""
        print(f"\n{Fore.GREEN}🚀 Starting Professional Trading Simulation{Style.RESET_ALL}")
        print(f"   📊 Cycles: {cycles}")
        print(f"   ⏱️ Delay: {delay}s between cycles")
        print(f"   🎯 Professional Execution: ENABLED")
        print(f"\n   Press Ctrl+C to stop early...\n")
        
        self.is_running = True
        total_signals = 0
        total_trades = 0
        
        try:
            for cycle in range(cycles):
                if not self.is_running:
                    break
                
                signals, trades = self.run_simulation_cycle()
                total_signals += signals
                total_trades += trades
                
                self._display_status()
                
                if cycle < cycles - 1:  # לא להמתין אחרי המחזור האחרון
                    print(f"\n⏳ Next cycle in {delay}s...")
                    time.sleep(delay / self.simulation_speed)
        
        except KeyboardInterrupt:
            print(f"\n\n⚠️ Simulation stopped by user")
        
        finally:
            self.is_running = False
            print(f"\n{Fore.GREEN}✅ SIMULATION COMPLETED{Style.RESET_ALL}")
            print(f"   📊 Total Signals: {total_signals}")
            print(f"   🎯 Total Trades: {total_trades}")
            if total_signals > 0:
                print(f"   📈 Execution Rate: {(total_trades/total_signals)*100:.1f}%")

def main():
    """פונקציה ראשית"""
    print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}🎯 PROFESSIONAL TRADING SYSTEM - FULL SIMULATION{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
    
    # יצירת מערכת הסימולציה
    dashboard = ProfessionalSimulationDashboard()
    
    # הרצת הסימולציה
    dashboard.run_simulation(cycles=20, delay=2.0)

if __name__ == "__main__":
    main()