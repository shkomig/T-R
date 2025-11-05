"""
🎯 Execution Manager - מנהל ביצועים מרכזי
================================================

מחלקה מרכזית שמיישמת את השלבים 0-5 המומלצים לביצוע עסקאות:
0. קבלת סיגנל
1. בדיקת סיכון גלובלית  
2. זיהוי משטר שוק
3. חישוב גודל פוזיציה
4. ולידציה כפולה
5. ביצוע

Author: T-R Trading System
Version: 1.0.0
Date: November 2, 2025
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime
import numpy as np

try:
    from ..risk_management.advanced_risk_calculator import AdvancedRiskCalculator
    from ..risk_management.enhanced_position_sizer import EnhancedPositionSizer
    from ..strategies.base_strategy import SignalType
except ImportError:
    from risk_management.advanced_risk_calculator import AdvancedRiskCalculator
    from risk_management.enhanced_position_sizer import EnhancedPositionSizer
    from strategies.base_strategy import SignalType


@dataclass
class ExecutionDecision:
    """החלטת ביצוע מפורטת עם כל הפרטים הנדרשים"""
    should_execute: bool
    symbol: str
    action: str  # 'BUY', 'SELL', 'HOLD'
    quantity: int
    price: float
    reason: str
    risk_metrics: Dict
    position_size_details: Dict
    confidence_score: float
    regime_suitability: float


class MarketRegime(Enum):
    """זיהוי משטרי שוק שונים לאופטימיזציה של אסטרטגיות"""
    STRONG_TREND_UP = "strong_trend_up"
    WEAK_TREND_UP = "weak_trend_up" 
    RANGING = "ranging"
    WEAK_TREND_DOWN = "weak_trend_down"
    STRONG_TREND_DOWN = "strong_trend_down"
    HIGH_VOLATILITY = "high_volatility"
    CRISIS = "crisis"


@dataclass
class TradingSignal:
    """סיגנל מסחר פשוט - להתאמה עם המערכת הקיימת"""
    symbol: str
    signal_type: str  # 'BUY', 'SELL', 'LONG', 'SHORT'
    confidence: float
    price: float
    timestamp: datetime
    data: Dict


class ExecutionManager:
    """
    🎯 מנהל ביצועים מרכזי - מתווך בין אסטרטגיות לביצוע
    
    המחלקה מיישמת את השלבים 0-5 המומלצים:
    0. קבלת סיגנל
    1. בדיקת סיכון גלובלית  
    2. זיהוי משטר שוק
    3. חישוב גודל פוזיציה
    4. ולידציה כפולה
    5. ביצוע
    """
    
    def __init__(self, 
                 risk_calculator: AdvancedRiskCalculator,
                 position_sizer: EnhancedPositionSizer,
                 broker=None):
        
        self.risk_calculator = risk_calculator
        self.position_sizer = position_sizer
        self.broker = broker
        self.logger = logging.getLogger(__name__)
        
        # Market Regime Detection
        self.current_regime = MarketRegime.RANGING
        self.regime_confidence = 0.5
        self.last_regime_update = None
        
        # Strategy weights per regime - אסטרטגיות מותאמות למשטר שוק
        self.strategy_weights = {
            MarketRegime.STRONG_TREND_UP: {
                'momentum': 1.0,           # מעולה לטרנד חזק
                'volume_breakout': 1.0,    # פריצות בטרנד חזק
                'rsi_divergence': 0.8,     # עדיין רלוונטי
                'vwap': 0.9,               # טוב לטרנד
                'mean_reversion': 0.2,     # לא מתאים
                'bollinger': 0.3,          # פחות רלוונטי
                'pairs_trading': 0.6       # hedge חלקי
            },
            MarketRegime.RANGING: {
                'momentum': 0.3,           # פחות יעיל
                'volume_breakout': 0.4,    # פריצות שווא
                'rsi_divergence': 1.0,     # מעולה לריינג'
                'vwap': 0.7,               # בסדר
                'mean_reversion': 1.0,     # מעולה לריינג'
                'bollinger': 1.0,          # מעולה לריינג'
                'pairs_trading': 1.0       # מעולה - ניטרלי
            },
            MarketRegime.HIGH_VOLATILITY: {
                'momentum': 0.2,           # מסוכן
                'volume_breakout': 0.1,    # מסוכן מאוד
                'rsi_divergence': 0.5,     # זהירות
                'vwap': 0.4,               # פחות יעיל
                'mean_reversion': 0.8,     # טוב לתנודתיות
                'bollinger': 0.6,          # בסדר
                'pairs_trading': 1.0       # הכי בטוח
            },
            MarketRegime.CRISIS: {
                'momentum': 0.1,           # מסוכן מאוד
                'volume_breakout': 0.0,    # לא לגעת!
                'rsi_divergence': 0.3,     # זהירות רבה
                'vwap': 0.2,               # לא יעיל
                'mean_reversion': 0.4,     # זהירות
                'bollinger': 0.3,          # זהירות
                'pairs_trading': 1.0       # היחיד הבטוח
            }
        }
        
        # Signal quality thresholds
        self.min_confidence_threshold = 0.6    # 60% ביטחון מינימלי
        self.min_regime_suitability = 0.5      # 50% התאמה למשטר
        
        self.logger.info("🎯 ExecutionManager initialized with professional risk management")
    
    def process_signal(self, signal: TradingSignal, 
                      current_balance: float, 
                      current_positions: Dict) -> ExecutionDecision:
        """
        🎯 השלבים 0-5 של עיבוד סיגנל לביצוע
        מיישם את המתודולוגיה המומלצת במלואה
        """
        symbol = signal.symbol
        
        # שלב 0: קבלת הסיגנל ולוגינג מפורט
        self.logger.info(f"📥 STEP 0: Processing signal for {symbol}")
        self.logger.info(f"    Signal: {signal.signal_type}")
        self.logger.info(f"    Confidence: {signal.confidence:.1%}")
        self.logger.info(f"    Price: ${signal.price:.2f}")
        
        # שלב 1: בדיקת סיכון גלובלית
        self.logger.info(f"🛡️ STEP 1: Global risk assessment")
        risk_metrics = self.risk_calculator.calculate_risk_metrics(
            current_balance, current_positions
        )
        
        if not risk_metrics['is_safe_to_trade']:
            violation_reasons = self._get_violation_reasons(risk_metrics)
            return ExecutionDecision(
                should_execute=False,
                symbol=symbol,
                action='HOLD',
                quantity=0,
                price=signal.price,
                reason=f"🚨 Global risk limits exceeded: {violation_reasons}",
                risk_metrics=risk_metrics,
                position_size_details={},
                confidence_score=0.0,
                regime_suitability=0.0
            )
        
        # שלב 2: בדיקת רלוונטיות לפי משטר שוק
        self.logger.info(f"🌊 STEP 2: Market regime analysis")
        regime_weight = self._get_strategy_weight_for_regime(signal.data.get('strategy_name', 'unknown'))
        
        if regime_weight < self.min_regime_suitability:
            return ExecutionDecision(
                should_execute=False,
                symbol=symbol,
                action='HOLD',
                quantity=0,
                price=signal.price,
                reason=f"🌊 Strategy unsuitable for {self.current_regime.value} (weight: {regime_weight:.1f})",
                risk_metrics=risk_metrics,
                position_size_details={'regime_weight': regime_weight},
                confidence_score=signal.confidence,
                regime_suitability=regime_weight
            )
        
        # שלב 3: חישוב גודל פוזיציה מתקדם
        self.logger.info(f"💰 STEP 3: Advanced position sizing")
        
        # Enhanced signal data with confidence weighting
        enhanced_signal_data = {
            'signal_type': signal.signal_type,
            'confidence': signal.confidence,
            'regime_adjusted_confidence': signal.confidence * regime_weight,
            'price': signal.price,
            'stop_loss': signal.data.get('stop_loss'),
            'strategy_name': signal.data.get('strategy_name', 'unknown'),
            'market_regime': self.current_regime.value,
            'regime_weight': regime_weight,
            'signals': signal.data.get('signals', {}),
            'signal_count': signal.data.get('signal_count', 1),
            'total_strategies': signal.data.get('total_strategies', 1),
            'momentum_score': signal.data.get('momentum_score', 1.0),
            'volume_confirmation': signal.data.get('volume_confirmation', 1.0)
        }
        
        position_result = self.position_sizer.calculate_position_size(
            symbol=symbol,
            signal_data=enhanced_signal_data,
            current_balance=current_balance,
            current_positions=current_positions,
            entry_price=signal.price
        )
        
        position_size, approved, sizing_message = position_result
        
        if not approved:
            return ExecutionDecision(
                should_execute=False,
                symbol=symbol,
                action='HOLD',
                quantity=0,
                price=signal.price,
                reason=f"💰 Position sizing rejected: {sizing_message}",
                risk_metrics=risk_metrics,
                position_size_details={'error': sizing_message, 'regime_weight': regime_weight},
                confidence_score=signal.confidence,
                regime_suitability=regime_weight
            )
        
        # שלב 4: ולידציה כפולה (סיכון סופי)
        self.logger.info(f"🔍 STEP 4: Final risk validation")
        quantity = max(1, int(position_size / signal.price))
        can_open, validation_message = self.risk_calculator.can_open_new_position(
            symbol=symbol,
            position_size=position_size,
            entry_price=signal.price,
            current_balance=current_balance,
            current_positions=current_positions
        )
        
        if not can_open:
            return ExecutionDecision(
                should_execute=False,
                symbol=symbol,
                action='HOLD',
                quantity=0,
                price=signal.price,
                reason=f"🛡️ Final validation failed: {validation_message}",
                risk_metrics=risk_metrics,
                position_size_details={
                    'position_size': position_size, 
                    'quantity': quantity,
                    'regime_weight': regime_weight
                },
                confidence_score=signal.confidence,
                regime_suitability=regime_weight
            )
        
        # שלב 5: אישור לביצוע
        self.logger.info(f"✅ STEP 5: Execution approved")
        action = 'BUY' if signal.signal_type in ['BUY', 'LONG', 'long'] else 'SELL'
        
        # Calculate final confidence score
        final_confidence = signal.confidence * regime_weight
        
        return ExecutionDecision(
            should_execute=True,
            symbol=symbol,
            action=action,
            quantity=quantity,
            price=signal.price,
            reason=f"✅ All checks passed. Confidence: {final_confidence:.1%}, Regime: {self.current_regime.value}",
            risk_metrics=risk_metrics,
            position_size_details={
                'position_size': position_size,
                'quantity': quantity,
                'regime_weight': regime_weight,
                'confidence_adjusted': final_confidence,
                'risk_percentage': (position_size * 0.25) / current_balance  # 25% stop loss
            },
            confidence_score=signal.confidence,
            regime_suitability=regime_weight
        )
    
    def _get_violation_reasons(self, risk_metrics: Dict) -> str:
        """🚨 קבלת סיבות הפרת גבולות סיכון"""
        reasons = []
        safety_checks = risk_metrics.get('safety_checks', {})
        
        if not safety_checks.get('daily_loss_ok', True):
            reasons.append(f"Daily loss {risk_metrics.get('daily_loss', 0):.2%}")
        if not safety_checks.get('drawdown_ok', True):
            reasons.append(f"Drawdown {risk_metrics.get('current_drawdown', 0):.2%}")
        if not safety_checks.get('portfolio_heat_ok', True):
            reasons.append(f"Portfolio heat {risk_metrics.get('portfolio_heat', 0):.2%}")
        if not safety_checks.get('trade_count_ok', True):
            reasons.append(f"Trade count {risk_metrics.get('trade_count_today', 0)}")
            
        return ', '.join(reasons) if reasons else "Unknown violation"
    
    def _get_strategy_weight_for_regime(self, strategy_name: str) -> float:
        """🌊 קבלת משקל אסטרטגיה בהתאם למשטר שוק נוכחי"""
        strategy_weights = self.strategy_weights.get(self.current_regime, {})
        normalized_name = strategy_name.lower().replace('_', '').replace('-', '')
        
        # Match strategy names flexibly
        for key in strategy_weights.keys():
            if key.replace('_', '') in normalized_name or normalized_name in key.replace('_', ''):
                return strategy_weights[key]
        
        return 0.5  # Default weight for unknown strategies
    
    def update_market_regime(self, market_data: Dict):
        """🌊 עדכון משטר שוק על בסיס נתוני מאקרו ומיקרו"""
        try:
            # נתוני שוק נדרשים
            spy_data = market_data.get('SPY', {})
            vix_data = market_data.get('VIX', {})
            qqq_data = market_data.get('QQQ', {})
            
            # אם אין נתוני SPY, ננסה QQQ
            main_index_data = spy_data or qqq_data
            
            if not main_index_data:
                self.logger.warning("📊 No market index data available for regime detection")
                return
            
            # חישוב טרנד (EMA 20 vs EMA 50)
            index_price = main_index_data.get('price', main_index_data.get('close', 0))
            index_ema_20 = main_index_data.get('ema_20', index_price)
            index_ema_50 = main_index_data.get('ema_50', index_price)
            
            # חישוב תנודתיות
            vix_level = vix_data.get('price', vix_data.get('close', 20))  # Default VIX = 20
            atr_normalized = main_index_data.get('atr_pct', 1.0)  # ATR as % of price
            
            # Volume analysis
            volume_ratio = main_index_data.get('volume_ratio', 1.0)  # Current vs average
            
            # זיהוי משטר
            trend_strength = (index_ema_20 - index_ema_50) / index_ema_50 if index_ema_50 > 0 else 0
            
            # Crisis detection (highest priority)
            if vix_level > 35 or atr_normalized > 4.0:
                new_regime = MarketRegime.CRISIS
                confidence = 0.9
            elif vix_level > 25 or atr_normalized > 2.5:
                new_regime = MarketRegime.HIGH_VOLATILITY
                confidence = 0.8
            elif trend_strength > 0.05:  # 5% strong trend up
                new_regime = MarketRegime.STRONG_TREND_UP
                confidence = min(0.9, trend_strength * 10)
            elif trend_strength > 0.02:  # 2% weak trend up
                new_regime = MarketRegime.WEAK_TREND_UP
                confidence = min(0.8, trend_strength * 15)
            elif trend_strength < -0.05:  # 5% strong trend down
                new_regime = MarketRegime.STRONG_TREND_DOWN
                confidence = min(0.9, abs(trend_strength) * 10)
            elif trend_strength < -0.02:  # 2% weak trend down
                new_regime = MarketRegime.WEAK_TREND_DOWN
                confidence = min(0.8, abs(trend_strength) * 15)
            else:
                new_regime = MarketRegime.RANGING
                confidence = 0.7
            
            # עדכון אם יש שינוי משמעותי
            if (new_regime != self.current_regime or 
                abs(confidence - self.regime_confidence) > 0.2):
                
                old_regime = self.current_regime
                self.current_regime = new_regime
                self.regime_confidence = confidence
                self.last_regime_update = datetime.now()
                
                self.logger.info(f"🌊 REGIME CHANGE: {old_regime.value} → {new_regime.value}")
                self.logger.info(f"   Confidence: {confidence:.1%}")
                self.logger.info(f"   Trend Strength: {trend_strength:+.2%}")
                self.logger.info(f"   VIX Level: {vix_level:.1f}")
                self.logger.info(f"   ATR: {atr_normalized:.1%}")
                
                # הדפסת השפעה על אסטרטגיות
                self._log_strategy_impact_change()
        
        except Exception as e:
            self.logger.error(f"❌ Error updating market regime: {e}")
    
    def _log_strategy_impact_change(self):
        """📊 הדפסת השפעת שינוי משטר על אסטרטגיות"""
        current_weights = self.strategy_weights.get(self.current_regime, {})
        
        self.logger.info(f"📊 Strategy weights for {self.current_regime.value}:")
        for strategy, weight in current_weights.items():
            if weight >= 0.8:
                status = "🟢 ACTIVE"
            elif weight >= 0.5:
                status = "🟡 REDUCED"
            elif weight >= 0.3:
                status = "🟠 LIMITED"
            else:
                status = "🔴 MINIMAL"
                
            self.logger.info(f"   {strategy:>15}: {weight:.1f} {status}")
    
    def get_regime_summary(self) -> Dict:
        """📊 קבלת סיכום מצב משטר שוק"""
        return {
            'current_regime': self.current_regime.value,
            'confidence': self.regime_confidence,
            'last_update': self.last_regime_update,
            'strategy_weights': self.strategy_weights.get(self.current_regime, {}),
            'recommended_strategies': [
                strategy for strategy, weight in self.strategy_weights.get(self.current_regime, {}).items()
                if weight >= 0.7
            ]
        }
    
    def get_execution_stats(self) -> Dict:
        """📊 סטטיסטיקות ביצוע"""
        return {
            'current_regime': self.current_regime.value,
            'regime_confidence': self.regime_confidence,
            'min_confidence_threshold': self.min_confidence_threshold,
            'min_regime_suitability': self.min_regime_suitability,
            'last_regime_update': self.last_regime_update.isoformat() if self.last_regime_update else None
        }