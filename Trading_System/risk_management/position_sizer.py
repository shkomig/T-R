"""
Position Sizer
=============
מחשבון גודל פוזיציות על בסיס ניהול סיכונים

מממש מספר שיטות לחישוב גודל פוזיציה:
1. Risk-Based: על בסיס אחוז סיכון מהחשבון
2. Fixed: מספר קבוע של מניות
3. Kelly Criterion: נוסחת קלי (מבוסס סבירות)
4. Volatility Adjusted: התאמה לתנודתיות
"""

from typing import Dict, Optional
from enum import Enum
import numpy as np


class SizingMethod(Enum):
    """שיטות חישוב גודל פוזיציה"""
    RISK_BASED = "risk_based"
    FIXED = "fixed"
    KELLY = "kelly"
    VOLATILITY_ADJUSTED = "volatility_adjusted"


class PositionSizer:
    """מחלקה לחישוב גודל פוזיציה"""
    
    def __init__(self, config: Dict):
        """
        אתחול
        
        Args:
            config: קונפיגורציה מקובץ risk_management.yaml
        """
        self.config = config
        
        # Default sizing method
        self.method = SizingMethod(
            config.get('method', 'risk_based')
        )
        
        # Risk-based parameters
        self.risk_per_trade_percent = config.get('risk_based', {}).get(
            'risk_per_trade', 2.0
        )
        
        # Fixed sizing
        self.fixed_shares = config.get('fixed', {}).get(
            'shares_per_trade', 100
        )
        
        # Kelly parameters
        self.kelly_fraction = config.get('kelly', {}).get(
            'fraction', 0.25
        )
        
        # Volatility parameters
        self.target_volatility = config.get('volatility_adjusted', {}).get(
            'target_volatility', 0.15
        )
        self.lookback_period = config.get('volatility_adjusted', {}).get(
            'lookback_period', 20
        )
        
    def calculate_position_size(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss: float,
        method: Optional[SizingMethod] = None,
        **kwargs
    ) -> int:
        """
        חישוב גודל פוזיציה
        
        Args:
            account_balance: יתרת חשבון
            entry_price: מחיר כניסה
            stop_loss: מחיר Stop Loss
            method: שיטת חישוב (אופציונלי, ישתמש בברירת מחדל)
            **kwargs: פרמטרים נוספים לפי השיטה
            
        Returns:
            מספר מניות
        """
        if method is None:
            method = self.method
        
        if method == SizingMethod.RISK_BASED:
            return self._risk_based_sizing(
                account_balance, entry_price, stop_loss
            )
        elif method == SizingMethod.FIXED:
            return self._fixed_sizing()
        elif method == SizingMethod.KELLY:
            return self._kelly_sizing(
                account_balance, entry_price, stop_loss, **kwargs
            )
        elif method == SizingMethod.VOLATILITY_ADJUSTED:
            return self._volatility_adjusted_sizing(
                account_balance, entry_price, **kwargs
            )
        else:
            raise ValueError(f"Unknown sizing method: {method}")
    
    def _risk_based_sizing(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss: float
    ) -> int:
        """
        חישוב גודל על בסיס סיכון קבוע
        
        מחשב כמה מניות לקנות כך שהסיכון יהיה X% מהחשבון
        
        Args:
            account_balance: יתרת חשבון
            entry_price: מחיר כניסה
            stop_loss: מחיר Stop Loss
            
        Returns:
            מספר מניות
        """
        # סיכון מקסימלי בדולרים
        max_risk_amount = account_balance * (self.risk_per_trade_percent / 100)
        
        # סיכון למניה
        risk_per_share = abs(entry_price - stop_loss)
        
        if risk_per_share == 0:
            return 0
        
        # מספר מניות
        shares = int(max_risk_amount / risk_per_share)
        
        return max(0, shares)
    
    def _fixed_sizing(self) -> int:
        """
        גודל קבוע - פשוט
        
        Returns:
            מספר מניות קבוע
        """
        return self.fixed_shares
    
    def _kelly_sizing(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss: float,
        win_rate: float = 0.5,
        avg_win: float = 1.0,
        avg_loss: float = 1.0
    ) -> int:
        """
        נוסחת קלי (Kelly Criterion)
        
        מחשב גודל פוזיציה אופטימלי על בסיס הסתברות הצלחה ויחס רווח/הפסד
        
        Kelly% = W - [(1-W) / R]
        כאשר:
        W = win rate (הסתברות רווח)
        R = avg_win / avg_loss (יחס רווח ממוצע להפסד ממוצע)
        
        Args:
            account_balance: יתרת חשבון
            entry_price: מחיר כניסה
            stop_loss: מחיר Stop Loss
            win_rate: שיעור הצלחה (0-1)
            avg_win: רווח ממוצע (ביחס לסיכון)
            avg_loss: הפסד ממוצע (ביחס לסיכון)
            
        Returns:
            מספר מניות
        """
        if avg_loss == 0:
            return 0
        
        # חישוב אחוז קלי
        win_loss_ratio = avg_win / avg_loss
        kelly_percent = win_rate - ((1 - win_rate) / win_loss_ratio)
        
        # שימוש בשבר מקלי (fractional Kelly) - שמרני יותר
        kelly_percent = kelly_percent * self.kelly_fraction
        
        # אם קלי שלילי, לא לסחור
        if kelly_percent <= 0:
            return 0
        
        # כמות ההשקעה על בסיס קלי
        position_value = account_balance * kelly_percent
        
        # מספר מניות
        shares = int(position_value / entry_price)
        
        return max(0, shares)
    
    def _volatility_adjusted_sizing(
        self,
        account_balance: float,
        entry_price: float,
        volatility: Optional[float] = None,
        atr: Optional[float] = None
    ) -> int:
        """
        התאמה לתנודתיות
        
        מניות עם תנודתיות גבוהה = פוזיציה קטנה יותר
        מניות עם תנודתיות נמוכה = פוזיציה גדולה יותר
        
        Args:
            account_balance: יתרת חשבון
            entry_price: מחיר כניסה
            volatility: תנודתיות (סטיית תקן שנתית)
            atr: Average True Range
            
        Returns:
            מספר מניות
        """
        if volatility is None and atr is None:
            # אם אין נתוני תנודתיות, השתמש ב-risk based
            return self._risk_based_sizing(
                account_balance, entry_price, entry_price * 0.98
            )
        
        # אם יש ATR, חשב תנודתיות מתוכו
        if volatility is None and atr is not None:
            volatility = (atr / entry_price) * np.sqrt(252)  # Annualize
        
        # התאמת גודל פוזיציה לתנודתיות
        # יעד: תנודתיות קבועה של הפוזיציה
        volatility_scalar = self.target_volatility / volatility
        
        # מקסימום ערך פוזיציה מותאם
        max_position_value = account_balance * volatility_scalar
        
        # הגבלה - לא יותר מ-20% מהחשבון
        max_position_value = min(max_position_value, account_balance * 0.2)
        
        # מספר מניות
        shares = int(max_position_value / entry_price)
        
        return max(0, shares)
    
    def validate_position_size(
        self,
        shares: int,
        entry_price: float,
        account_balance: float,
        max_position_percent: float = 20.0
    ) -> int:
        """
        וידוא שגודל הפוזיציה לא חורג מהמגבלות
        
        Args:
            shares: מספר מניות מחושב
            entry_price: מחיר כניסה
            account_balance: יתרת חשבון
            max_position_percent: אחוז מקסימלי מהחשבון לפוזיציה
            
        Returns:
            מספר מניות מתוקן
        """
        # ערך הפוזיציה
        position_value = shares * entry_price
        
        # ערך מקסימלי
        max_position_value = account_balance * (max_position_percent / 100)
        
        # אם חורג, תקן
        if position_value > max_position_value:
            shares = int(max_position_value / entry_price)
        
        # לפחות מניה אחת
        return max(1, shares)
    
    def calculate_position_value(self, shares: int, price: float) -> float:
        """חישוב ערך פוזיציה"""
        return shares * price
    
    def calculate_risk_amount(
        self,
        shares: int,
        entry_price: float,
        stop_loss: float
    ) -> float:
        """
        חישוב הסיכון בדולרים
        
        Args:
            shares: מספר מניות
            entry_price: מחיר כניסה
            stop_loss: מחיר Stop Loss
            
        Returns:
            סיכון בדולרים
        """
        risk_per_share = abs(entry_price - stop_loss)
        return shares * risk_per_share
    
    def calculate_risk_percent(
        self,
        shares: int,
        entry_price: float,
        stop_loss: float,
        account_balance: float
    ) -> float:
        """
        חישוב הסיכון כאחוז מהחשבון
        
        Returns:
            אחוז סיכון
        """
        risk_amount = self.calculate_risk_amount(shares, entry_price, stop_loss)
        return (risk_amount / account_balance) * 100
