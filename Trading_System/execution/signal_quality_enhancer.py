"""
🎯 Signal Quality Enhancer - משפר איכות סיגנלים
===================================================

מערכת לשיפור איכות סיגנלים על בסיס הקשר שוק ותנאים טכניים.
מתאים את רמת הביטחון (confidence) בהתבסס על:
- אישור נפח (Volume confirmation)
- קורלציה עם השוק (Market correlation)
- התכנסות טכנית (Technical confluence)
- תמיכה/התנגדות (Support/Resistance)

Author: T-R Trading System
Version: 1.0.0
Date: November 2, 2025
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime
import numpy as np
import pandas as pd


@dataclass
class SignalEnhancement:
    """פרטי שיפור סיגנל"""
    original_confidence: float
    enhanced_confidence: float
    adjustments: List[Tuple[str, float]]
    enhancement_reason: str
    market_context_score: float
    technical_confluence_score: float


class SignalQualityEnhancer:
    """
    🎯 משפר איכות סיגנלים עם ציונים מרוכבים
    
    מתאים את רמת הביטחון בסיגנלים על בסיס:
    1. הקשר שוק (Volume, Correlation, Timing)
    2. התכנסות טכנית (מספר אינדיקטורים מאשרים)
    3. תמיכה/התנגדות
    4. מומנטום שוק
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Enhancement parameters
        self.volume_impact = {
            'high_volume_bonus': 0.15,      # נפח גבוה = ביטחון גבוה יותר
            'low_volume_penalty': -0.10,   # נפח נמוך = פחות ביטחון
            'extreme_volume_threshold': 2.0 # פי 2 מהממוצע
        }
        
        self.market_correlation_impact = {
            'aligned_bonus': 0.12,          # סיגנל מתיישר עם השוק
            'contrarian_penalty': -0.08,   # סיגנל נגד השוק
            'correlation_threshold': 0.7   # סף קורלציה משמעותית
        }
        
        self.technical_confluence_impact = {
            'multiple_indicators_bonus': 0.20,  # כמה אינדיקטורים מאשרים
            'single_indicator_penalty': -0.05,  # אינדיקטור יחיד
            'min_confluence_count': 3           # מינימום אינדיקטורים לבונוס
        }
        
        self.timing_impact = {
            'session_bonus': 0.08,          # בתוך שעות מסחר רגילות
            'opening_bonus': 0.10,          # בפתיחת השוק
            'closing_bonus': 0.06,          # לקראת סגירה
            'afterhours_penalty': -0.15     # מחוץ לשעות מסחר
        }
        
        self.logger.info("🎯 SignalQualityEnhancer initialized")
    
    def enhance_signal_confidence(self, 
                                 signal_data: Dict, 
                                 market_context: Dict) -> SignalEnhancement:
        """
        🎯 שיפור ביטחון סיגנל על בסיס הקשר שוק ותנאים טכניים
        
        Parameters:
        -----------
        signal_data : Dict
            נתוני הסיגנל הבסיסי
        market_context : Dict
            הקשר שוק נוכחי
            
        Returns:
        --------
        SignalEnhancement עם פרטי השיפור
        """
        
        base_confidence = signal_data.get('confidence', 0.5)
        adjustments = []
        
        try:
            # 1. Volume confirmation analysis
            volume_adjustment = self._analyze_volume_confirmation(market_context)
            if volume_adjustment != 0:
                adjustments.append(('Volume', volume_adjustment))
            
            # 2. Market correlation analysis
            correlation_adjustment = self._analyze_market_correlation(
                signal_data, market_context
            )
            if correlation_adjustment != 0:
                adjustments.append(('Market Correlation', correlation_adjustment))
            
            # 3. Technical confluence analysis
            confluence_adjustment = self._analyze_technical_confluence(signal_data)
            if confluence_adjustment != 0:
                adjustments.append(('Technical Confluence', confluence_adjustment))
            
            # 4. Timing analysis
            timing_adjustment = self._analyze_timing_context(market_context)
            if timing_adjustment != 0:
                adjustments.append(('Timing', timing_adjustment))
            
            # 5. Support/Resistance analysis
            sr_adjustment = self._analyze_support_resistance(signal_data, market_context)
            if sr_adjustment != 0:
                adjustments.append(('Support/Resistance', sr_adjustment))
            
            # Calculate final confidence
            final_confidence = base_confidence
            total_adjustment = sum(adj[1] for adj in adjustments)
            final_confidence += total_adjustment
            
            # Clamp to valid range [0.0, 1.0]
            final_confidence = max(0.0, min(1.0, final_confidence))
            
            # Create enhancement summary
            enhancement_reason = self._create_enhancement_reason(adjustments)
            market_score = self._calculate_market_context_score(market_context)
            technical_score = self._calculate_technical_confluence_score(signal_data)
            
            enhancement = SignalEnhancement(
                original_confidence=base_confidence,
                enhanced_confidence=final_confidence,
                adjustments=adjustments,
                enhancement_reason=enhancement_reason,
                market_context_score=market_score,
                technical_confluence_score=technical_score
            )
            
            self.logger.info(
                f"🎯 Signal enhanced: {base_confidence:.1%} → {final_confidence:.1%} "
                f"({total_adjustment:+.1%})"
            )
            
            return enhancement
            
        except Exception as e:
            self.logger.error(f"❌ Error enhancing signal: {e}")
            return SignalEnhancement(
                original_confidence=base_confidence,
                enhanced_confidence=base_confidence,
                adjustments=[],
                enhancement_reason="Enhancement failed",
                market_context_score=0.5,
                technical_confluence_score=0.5
            )
    
    def _analyze_volume_confirmation(self, market_context: Dict) -> float:
        """📊 ניתוח אישור נפח"""
        volume_ratio = market_context.get('volume_ratio', 1.0)
        avg_volume = market_context.get('avg_volume', 0)
        
        if volume_ratio > self.volume_impact['extreme_volume_threshold']:
            return self.volume_impact['high_volume_bonus']
        elif volume_ratio < 0.5:  # נפח נמוך מהממוצע
            return self.volume_impact['low_volume_penalty']
        elif volume_ratio > 1.2:  # נפח גבוה במקצת
            return self.volume_impact['high_volume_bonus'] * 0.5
        
        return 0.0
    
    def _analyze_market_correlation(self, signal_data: Dict, market_context: Dict) -> float:
        """📈 ניתוח קורלציה עם השוק"""
        signal_direction = signal_data.get('signal_type', 'HOLD')
        market_trend = market_context.get('spy_trend', 0)  # 1=up, -1=down, 0=neutral
        market_correlation = market_context.get('spy_correlation', 0.5)
        
        # בדיקה אם הסיגנל מתיישר עם כיוון השוק
        if abs(market_correlation) > self.market_correlation_impact['correlation_threshold']:
            if signal_direction in ['BUY', 'LONG'] and market_trend > 0:
                return self.market_correlation_impact['aligned_bonus']
            elif signal_direction in ['SELL', 'SHORT'] and market_trend < 0:
                return self.market_correlation_impact['aligned_bonus']
            else:
                return self.market_correlation_impact['contrarian_penalty']
        
        return 0.0
    
    def _analyze_technical_confluence(self, signal_data: Dict) -> float:
        """🔧 ניתוח התכנסות טכנית"""
        # ספירת אינדיקטורים מאשרים
        signals = signal_data.get('signals', {})
        signal_count = signal_data.get('signal_count', 0)
        total_strategies = signal_data.get('total_strategies', 1)
        
        # בדיקת התכנסות על בסיס מספר אינדיקטורים
        if signal_count >= self.technical_confluence_impact['min_confluence_count']:
            confluence_ratio = signal_count / total_strategies
            return self.technical_confluence_impact['multiple_indicators_bonus'] * confluence_ratio
        elif signal_count <= 1:
            return self.technical_confluence_impact['single_indicator_penalty']
        
        return 0.0
    
    def _analyze_timing_context(self, market_context: Dict) -> float:
        """⏰ ניתוח הקשר זמן"""
        current_time = datetime.now()
        market_session = market_context.get('session', 'regular')
        
        # ניתוח לפי שעות מסחר
        if market_session == 'pre_market':
            return self.timing_impact['opening_bonus'] * 0.5
        elif market_session == 'regular':
            # בדיקה אם זה בשעות הפתיחה הראשונות
            hour = current_time.hour
            if 9 <= hour <= 10:  # שעת פתיחה
                return self.timing_impact['opening_bonus']
            elif 15 <= hour <= 16:  # שעת סגירה
                return self.timing_impact['closing_bonus']
            else:
                return self.timing_impact['session_bonus']
        elif market_session == 'after_hours':
            return self.timing_impact['afterhours_penalty']
        
        return 0.0
    
    def _analyze_support_resistance(self, signal_data: Dict, market_context: Dict) -> float:
        """📏 ניתוח תמיכה והתנגדות"""
        price = signal_data.get('price', 0)
        support_level = market_context.get('support_level', 0)
        resistance_level = market_context.get('resistance_level', 0)
        signal_type = signal_data.get('signal_type', 'HOLD')
        
        if support_level and resistance_level and price:
            # מרחק מתמיכה/התנגדות כאחוז מהמחיר
            distance_to_support = abs(price - support_level) / price if support_level else 1.0
            distance_to_resistance = abs(price - resistance_level) / price if resistance_level else 1.0
            
            # בונוס לסיגנלי קנייה ליד תמיכה
            if signal_type in ['BUY', 'LONG'] and distance_to_support < 0.02:  # 2% מהתמיכה
                return 0.10
            
            # בונוס לסיגנלי מכירה ליד התנגדות
            if signal_type in ['SELL', 'SHORT'] and distance_to_resistance < 0.02:  # 2% מההתנגדות
                return 0.10
            
            # עונש לסיגנלים רחוק מרמות מפתח
            min_distance = min(distance_to_support, distance_to_resistance)
            if min_distance > 0.05:  # רחוק יותר מ-5%
                return -0.05
        
        return 0.0
    
    def _calculate_market_context_score(self, market_context: Dict) -> float:
        """📊 חישוב ציון הקשר שוק"""
        volume_ratio = market_context.get('volume_ratio', 1.0)
        volatility = market_context.get('volatility', 0.02)
        trend_strength = market_context.get('trend_strength', 0.0)
        
        # ציון מורכב על בסיס תנאי שוק
        volume_score = min(1.0, volume_ratio / 2.0)  # נורמליזציה לפי נפח
        volatility_score = 1.0 - min(1.0, volatility / 0.05)  # תנודתיות נמוכה = טוב יותר
        trend_score = min(1.0, abs(trend_strength) * 2)  # טרנד חזק = טוב יותר
        
        return (volume_score + volatility_score + trend_score) / 3.0
    
    def _calculate_technical_confluence_score(self, signal_data: Dict) -> float:
        """🔧 חישוב ציון התכנסות טכנית"""
        signal_count = signal_data.get('signal_count', 0)
        total_strategies = signal_data.get('total_strategies', 1)
        momentum_score = signal_data.get('momentum_score', 1.0)
        
        # ציון על בסיס כמות ואיכות הסיגנלים
        confluence_ratio = signal_count / total_strategies if total_strategies > 0 else 0
        momentum_normalized = min(1.0, abs(momentum_score) / 2.0)
        
        return (confluence_ratio + momentum_normalized) / 2.0
    
    def _create_enhancement_reason(self, adjustments: List[Tuple[str, float]]) -> str:
        """📝 יצירת הסבר לשיפור הסיגנל"""
        if not adjustments:
            return "No significant enhancements applied"
        
        positive_adjustments = [f"{name}(+{adj:+.1%})" for name, adj in adjustments if adj > 0]
        negative_adjustments = [f"{name}({adj:+.1%})" for name, adj in adjustments if adj < 0]
        
        parts = []
        if positive_adjustments:
            parts.append(f"Boosted by: {', '.join(positive_adjustments)}")
        if negative_adjustments:
            parts.append(f"Reduced by: {', '.join(negative_adjustments)}")
        
        return "; ".join(parts)
    
    def get_enhancement_stats(self) -> Dict:
        """📊 סטטיסטיקות שיפור"""
        return {
            'volume_thresholds': self.volume_impact,
            'correlation_thresholds': self.market_correlation_impact,
            'confluence_thresholds': self.technical_confluence_impact,
            'timing_adjustments': self.timing_impact
        }