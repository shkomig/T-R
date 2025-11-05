"""
💰 Enhanced Position Sizer - Advanced Position Sizing with Risk Integration
========================================================================

מחלקת חישוב גודל פוזיציה משופרת עם אינטגרציה מלאה לניהול סיכונים:
- אינטגרציה מלאה עם Advanced Risk Calculator
- חישוב עוצמת אותות (Signal Strength)
- ולידציה מרובת שכבות לפני כל עסקה
- התאמה דינמית לתנאי שוק

Author: T-R Trading System
Version: 3.1.0
Date: November 2, 2025
"""

from typing import Dict, Tuple, Optional, Any
import logging
import numpy as np
from datetime import datetime
import math

from .advanced_risk_calculator import AdvancedRiskCalculator


class EnhancedPositionSizer:
    """
    🎯 מחלקת חישוב גודל פוזיציה משופרת עם אינטגרציה מלאה לניהול סיכונים
    
    Features:
    --------
    1. Risk Calculator Integration - אינטגרציה מלאה לניהול סיכונים
    2. Signal Strength Analysis - ניתוח עוצמת אותות
    3. Multi-Layer Validation - ולידציה מרובת שכבות
    4. Dynamic Sizing - התאמה דינמית לתנאי שוק
    5. Kelly Criterion Support - תמיכה בקריטריון קלי
    """
    
    def __init__(self, risk_calculator: AdvancedRiskCalculator,
                 sizing_method: str = "dynamic",
                 kelly_fraction: float = 0.25,
                 volatility_adjustment: bool = True,
                 signal_confidence_threshold: float = 0.6):
        """
        Initialize Enhanced Position Sizer
        
        Parameters:
        -----------
        risk_calculator : AdvancedRiskCalculator
            The risk calculator instance for integration
        sizing_method : str
            Method for position sizing: 'fixed', 'dynamic', 'kelly', 'volatility'
        kelly_fraction : float
            Fraction of Kelly bet size to use (0.25 = 25% of Kelly)
        volatility_adjustment : bool
            Whether to adjust position size based on volatility
        signal_confidence_threshold : float
            Minimum signal confidence required for trading
        """
        
        self.risk_calculator = risk_calculator
        self.sizing_method = sizing_method
        self.kelly_fraction = kelly_fraction
        self.volatility_adjustment = volatility_adjustment
        self.signal_confidence_threshold = signal_confidence_threshold
        
        # 📊 Sizing Parameters
        self.base_position_size = 15000  # Default base size
        self.min_position_size = 1000    # Minimum position size
        self.max_position_size = 50000   # Maximum position size
        
        # 📈 Performance Tracking
        self.sizing_history = []
        self.performance_tracker = {
            'total_positions': 0,
            'successful_positions': 0,
            'avg_position_size': 0.0,
            'sizing_accuracy': 0.0
        }
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("💰 Enhanced Position Sizer initialized")
        self.logger.info(f"   Sizing Method: {self.sizing_method}")
        self.logger.info(f"   Kelly Fraction: {self.kelly_fraction}")
        self.logger.info(f"   Volatility Adjustment: {self.volatility_adjustment}")
        self.logger.info(f"   Signal Threshold: {self.signal_confidence_threshold}")
    
    def calculate_position_size(self, symbol: str, signal_data: Dict[str, Any],
                              current_balance: float, current_positions: Dict,
                              entry_price: float,
                              base_position_size: Optional[float] = None) -> Tuple[float, bool, str]:
        """
        🎯 חישוב גודל פוזיציה עם כל בדיקות הבטיחות המומלצות
        
        This is the MAIN position sizing function that integrates all risk checks.
        
        Parameters:
        -----------
        symbol : str
            Trading symbol
        signal_data : Dict
            Signal information including strength, confidence, direction
        current_balance : float
            Current account balance
        current_positions : Dict
            Current open positions
        entry_price : float
            Expected entry price
        base_position_size : float, optional
            Base position size override
        
        Returns:
        --------
        Tuple[float, bool, str] : (position_size, approved, message)
        """
        
        start_time = datetime.now()
        base_size = base_position_size or self.base_position_size
        
        try:
            self.logger.info(f"💰 Calculating position size for {symbol}")
            
            # 🔍 STEP 1: Global Risk Assessment
            self.logger.info(f"   🔍 Step 1: Global risk assessment")
            risk_metrics = self.risk_calculator.calculate_risk_metrics(current_balance, current_positions)
            
            if not risk_metrics['is_safe_to_trade']:
                return 0.0, False, "❌ Global risk limits exceeded - trading halted"
            
            # 🔍 STEP 2: Signal Analysis
            self.logger.info(f"   🔍 Step 2: Signal analysis")
            signal_strength, signal_confidence = self._analyze_signal_strength(signal_data)
            
            if signal_confidence < self.signal_confidence_threshold:
                return 0.0, False, f"❌ Signal confidence {signal_confidence:.2f} < threshold {self.signal_confidence_threshold}"
            
            # 🔍 STEP 3: Portfolio Heat Calculation
            self.logger.info(f"   🔍 Step 3: Portfolio heat calculation")
            available_heat = self.risk_calculator.calculate_optimal_portfolio_heat(
                current_balance, current_positions
            )
            
            if available_heat <= 0:
                return 0.0, False, "❌ No available portfolio heat for new positions"
            
            # 🔍 STEP 4: Position Size Calculation
            self.logger.info(f"   🔍 Step 4: Position size calculation")
            calculated_size = self._calculate_optimal_size(
                symbol=symbol,
                signal_strength=signal_strength,
                signal_confidence=signal_confidence,
                current_balance=current_balance,
                available_heat=available_heat,
                entry_price=entry_price,
                base_size=base_size
            )
            
            # 🔍 STEP 5: Size Validation and Adjustment
            self.logger.info(f"   🔍 Step 5: Size validation and adjustment")
            final_size = self._validate_and_adjust_size(
                calculated_size, current_balance, available_heat
            )
            
            # 🔍 STEP 6: Final Risk Validation
            self.logger.info(f"   🔍 Step 6: Final risk validation")
            can_open, validation_msg = self.risk_calculator.can_open_new_position(
                symbol, final_size, entry_price, current_balance, current_positions
            )
            
            if not can_open:
                return 0.0, False, f"❌ Final validation failed: {validation_msg}"
            
            # 📊 Record sizing decision
            self._record_sizing_decision(symbol, signal_data, final_size, current_balance)
            
            # ✅ Success!
            execution_time = (datetime.now() - start_time).total_seconds()
            success_msg = (f"✅ Position approved for {symbol}: "
                         f"${final_size:,.2f} (Signal: {signal_strength:.2f}, "
                         f"Confidence: {signal_confidence:.2f}) - {execution_time:.3f}s")
            
            self.logger.info(success_msg)
            return final_size, True, success_msg
            
        except Exception as e:
            error_msg = f"❌ Error calculating position size for {symbol}: {e}"
            self.logger.error(error_msg)
            return 0.0, False, error_msg
    
    def _analyze_signal_strength(self, signal_data: Dict[str, Any]) -> Tuple[float, float]:
        """
        📊 ניתוח עוצמת אות וביטחון
        
        Returns:
        --------
        Tuple[float, float] : (signal_strength, signal_confidence)
        """
        
        # Extract signal information
        signals = signal_data.get('signals', {})
        signal_count = signal_data.get('signal_count', 0)
        total_strategies = signal_data.get('total_strategies', 7)
        
        if not signals or signal_count == 0:
            return 0.0, 0.0
        
        # Calculate basic strength (percentage of strategies agreeing)
        basic_strength = signal_count / total_strategies
        
        # Analyze signal quality - support both old and new format
        strong_signals = 0
        weak_signals = 0
        
        for signal in signals.values():
            if signal in ['STRONG_BUY', 'STRONG_SELL', 'BUY', 'SELL']:
                strong_signals += 1
            elif signal in ['WEAK_BUY', 'WEAK_SELL', 'H', 'L']:  # H=High, L=Low confidence
                weak_signals += 1
        
        # Calculate weighted strength
        total_valid_signals = strong_signals + weak_signals
        if total_valid_signals > 0:
            weighted_strength = (strong_signals * 1.0 + weak_signals * 0.5) / total_strategies
        else:
            weighted_strength = basic_strength  # Fallback
        
        # Calculate confidence based on signal consistency
        if signal_count >= 4:  # Strong consensus
            confidence = min(1.0, basic_strength * 1.2)
        elif signal_count >= 2:  # Moderate consensus
            confidence = basic_strength
        else:  # Weak consensus
            confidence = basic_strength * 0.8
        
        # Additional confidence factors
        momentum_factor = min(2.0, abs(signal_data.get('momentum_score', 1.0)))
        volume_factor = min(2.0, signal_data.get('volume_confirmation', 1.0))
        
        # Adjust confidence based on additional factors
        confidence *= min(1.5, momentum_factor) * min(1.2, volume_factor)
        confidence = min(1.0, confidence)
        
        # Final strength calculation
        final_strength = min(1.0, (weighted_strength + basic_strength) / 2)
        
        self.logger.debug(f"📊 Signal Analysis:")
        self.logger.debug(f"   Basic Strength: {basic_strength:.2f}")
        self.logger.debug(f"   Weighted Strength: {weighted_strength:.2f}")
        self.logger.debug(f"   Final Strength: {final_strength:.2f}")
        self.logger.debug(f"   Confidence: {confidence:.2f}")
        self.logger.debug(f"   Signals: {signals}")
        
        return final_strength, confidence
        
        # Adjust confidence based on additional factors
        confidence *= momentum_factor * volume_factor
        confidence = min(1.0, confidence)
        
        # Final strength calculation
        final_strength = min(1.0, (weighted_strength + basic_strength) / 2)
        
        self.logger.debug(f"📊 Signal Analysis:")
        self.logger.debug(f"   Basic Strength: {basic_strength:.2f}")
        self.logger.debug(f"   Weighted Strength: {weighted_strength:.2f}")
        self.logger.debug(f"   Final Strength: {final_strength:.2f}")
        self.logger.debug(f"   Confidence: {confidence:.2f}")
        
        return final_strength, confidence
    
    def _calculate_optimal_size(self, symbol: str, signal_strength: float,
                              signal_confidence: float, current_balance: float,
                              available_heat: float, entry_price: float,
                              base_size: float) -> float:
        """
        💡 חישוב גודל פוזיציה אופטימלי בהתבסס על השיטה שנבחרה
        """
        
        if self.sizing_method == "fixed":
            return self._calculate_fixed_size(base_size, signal_strength)
            
        elif self.sizing_method == "dynamic":
            return self._calculate_dynamic_size(
                signal_strength, signal_confidence, current_balance, available_heat, base_size
            )
            
        elif self.sizing_method == "kelly":
            return self._calculate_kelly_size(
                symbol, signal_strength, signal_confidence, current_balance, entry_price
            )
            
        elif self.sizing_method == "volatility":
            return self._calculate_volatility_adjusted_size(
                symbol, signal_strength, current_balance, entry_price, base_size
            )
        
        else:
            # Default to dynamic sizing
            return self._calculate_dynamic_size(
                signal_strength, signal_confidence, current_balance, available_heat, base_size
            )
    
    def _calculate_fixed_size(self, base_size: float, signal_strength: float) -> float:
        """Fixed position sizing with signal strength adjustment"""
        return base_size * signal_strength
    
    def _calculate_dynamic_size(self, signal_strength: float, signal_confidence: float,
                              current_balance: float, available_heat: float,
                              base_size: float) -> float:
        """Dynamic position sizing based on multiple factors"""
        
        # Start with base size
        size = base_size
        
        # Adjust for signal strength
        size *= signal_strength
        
        # Adjust for signal confidence
        confidence_multiplier = 0.5 + (signal_confidence * 0.5)  # 0.5 to 1.0
        size *= confidence_multiplier
        
        # Limit by available heat
        max_size_by_heat = self.risk_calculator.get_position_size_limit(
            current_balance, available_heat
        )
        size = min(size, max_size_by_heat)
        
        # Account balance adjustment
        balance_factor = min(1.0, current_balance / 100000)  # Scale for 100k baseline
        size *= (0.5 + balance_factor * 0.5)  # Between 50% and 100% of calculated size
        
        return size
    
    def _calculate_kelly_size(self, symbol: str, signal_strength: float,
                            signal_confidence: float, current_balance: float,
                            entry_price: float) -> float:
        """Kelly Criterion position sizing"""
        
        # Estimate win probability based on signal confidence and strength
        win_probability = (signal_confidence + signal_strength) / 2
        
        # Estimate win/loss ratio (conservative estimate)
        avg_win_loss_ratio = 1.5  # 1.5:1 average win/loss
        
        # Kelly fraction calculation: f = (bp - q) / b
        # where b = odds, p = win probability, q = lose probability
        b = avg_win_loss_ratio
        p = win_probability
        q = 1 - p
        
        kelly_fraction_calc = (b * p - q) / b
        kelly_fraction_calc = max(0, kelly_fraction_calc)  # No negative Kelly
        
        # Apply Kelly fraction safety factor
        safe_kelly_fraction = kelly_fraction_calc * self.kelly_fraction
        
        # Calculate position size
        kelly_size = current_balance * safe_kelly_fraction
        
        self.logger.debug(f"📊 Kelly Calculation for {symbol}:")
        self.logger.debug(f"   Win Probability: {p:.2f}")
        self.logger.debug(f"   Win/Loss Ratio: {b:.2f}")
        self.logger.debug(f"   Kelly Fraction: {kelly_fraction_calc:.3f}")
        self.logger.debug(f"   Safe Kelly: {safe_kelly_fraction:.3f}")
        
        return kelly_size
    
    def _calculate_volatility_adjusted_size(self, symbol: str, signal_strength: float,
                                          current_balance: float, entry_price: float,
                                          base_size: float) -> float:
        """Volatility-adjusted position sizing"""
        
        # Simple volatility estimation (in real implementation, use ATR or realized volatility)
        estimated_volatility = 0.02  # 2% daily volatility baseline
        
        # Adjust size inversely to volatility
        volatility_adjustment = min(2.0, 0.02 / estimated_volatility)
        
        # Apply signal strength
        adjusted_size = base_size * signal_strength * volatility_adjustment
        
        return adjusted_size
    
    def _validate_and_adjust_size(self, calculated_size: float, current_balance: float,
                                available_heat: float) -> float:
        """
        🔍 אימות וההתאמה סופית של גודל הפוזיציה
        """
        
        # Apply minimum size
        final_size = max(self.min_position_size, calculated_size)
        
        # Apply maximum size
        final_size = min(self.max_position_size, final_size)
        
        # Ensure we don't exceed available heat
        max_size_by_heat = self.risk_calculator.get_position_size_limit(
            current_balance, available_heat
        )
        final_size = min(final_size, max_size_by_heat)
        
        # Ensure we don't exceed percentage of account
        max_size_by_account = current_balance * 0.10  # Max 10% of account per position
        final_size = min(final_size, max_size_by_account)
        
        # Round to nearest $100
        final_size = round(final_size / 100) * 100
        
        self.logger.debug(f"🔍 Size Validation:")
        self.logger.debug(f"   Calculated: ${calculated_size:,.2f}")
        self.logger.debug(f"   After Min/Max: ${min(self.max_position_size, max(self.min_position_size, calculated_size)):,.2f}")
        self.logger.debug(f"   After Heat Limit: ${min(final_size, max_size_by_heat):,.2f}")
        self.logger.debug(f"   Final Size: ${final_size:,.2f}")
        
        return final_size
    
    def _record_sizing_decision(self, symbol: str, signal_data: Dict[str, Any],
                              position_size: float, current_balance: float) -> None:
        """📊 Record sizing decision for analysis"""
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'position_size': position_size,
            'position_size_percent': position_size / current_balance,
            'signal_data': signal_data,
            'sizing_method': self.sizing_method,
            'current_balance': current_balance
        }
        
        self.sizing_history.append(record)
        
        # Keep only last 1000 records
        if len(self.sizing_history) > 1000:
            self.sizing_history = self.sizing_history[-1000:]
        
        # Update performance tracking
        self.performance_tracker['total_positions'] += 1
        
        # Calculate running average position size
        total_size = sum(r['position_size'] for r in self.sizing_history[-100:])  # Last 100
        count = min(100, len(self.sizing_history))
        self.performance_tracker['avg_position_size'] = total_size / count if count > 0 else 0
    
    def get_sizing_performance(self) -> Dict[str, Any]:
        """📈 Get position sizing performance metrics"""
        
        if not self.sizing_history:
            return {'message': 'No sizing history available'}
        
        recent_positions = self.sizing_history[-50:]  # Last 50 positions
        
        avg_size = np.mean([p['position_size'] for p in recent_positions])
        std_size = np.std([p['position_size'] for p in recent_positions])
        min_size = min(p['position_size'] for p in recent_positions)
        max_size = max(p['position_size'] for p in recent_positions)
        
        avg_size_percent = np.mean([p['position_size_percent'] for p in recent_positions])
        
        return {
            'total_positions': len(self.sizing_history),
            'recent_positions': len(recent_positions),
            'avg_position_size': avg_size,
            'std_position_size': std_size,
            'min_position_size': min_size,
            'max_position_size': max_size,
            'avg_size_percent': avg_size_percent,
            'sizing_method': self.sizing_method,
            'performance_tracker': self.performance_tracker
        }
    
    def update_sizing_parameters(self, **kwargs) -> None:
        """🔧 Update sizing parameters"""
        
        for param, value in kwargs.items():
            if hasattr(self, param):
                old_value = getattr(self, param)
                setattr(self, param, value)
                self.logger.info(f"🔧 Updated {param}: {old_value} → {value}")
            else:
                self.logger.warning(f"⚠️ Unknown parameter: {param}")


if __name__ == "__main__":
    # 🧪 Test the Enhanced Position Sizer
    print("💰 Testing Enhanced Position Sizer...")
    
    # Initialize components
    from .advanced_risk_calculator import AdvancedRiskCalculator
    
    risk_calc = AdvancedRiskCalculator()
    position_sizer = EnhancedPositionSizer(
        risk_calculator=risk_calc,
        sizing_method="dynamic"
    )
    
    # Test data
    test_balance = 100000.0
    test_positions = {
        'AAPL': {'quantity': 100, 'entry_price': 150.0, 'current_price': 152.0}
    }
    
    test_signal = {
        'signals': {
            'vwap': 'BUY',
            'momentum': 'STRONG_BUY',
            'bollinger': 'BUY',
            'mean_reversion': 'HOLD'
        },
        'signal_count': 3,
        'total_strategies': 7,
        'momentum_score': 1.2,
        'volume_confirmation': 1.1
    }
    
    # Test position sizing
    size, approved, message = position_sizer.calculate_position_size(
        symbol='MSFT',
        signal_data=test_signal,
        current_balance=test_balance,
        current_positions=test_positions,
        entry_price=300.0
    )
    
    print(f"\n💰 Position Sizing Test Results:")
    print(f"   Symbol: MSFT")
    print(f"   Position Size: ${size:,.2f}")
    print(f"   Approved: {'✅ YES' if approved else '❌ NO'}")
    print(f"   Message: {message}")
    
    # Performance metrics
    performance = position_sizer.get_sizing_performance()
    print(f"\n📈 Performance Metrics:")
    print(f"   Total Positions: {performance.get('total_positions', 0)}")
    print(f"   Sizing Method: {performance.get('sizing_method', 'N/A')}")
    
    print("\n✅ Enhanced Position Sizer test completed!")