"""
Risk Calculator
==============
מחשבון סיכונים - ניהול סיכונים ברמת החשבון

מבצע:
- בדיקת הסיכון הכולל של התיק
- ניטור ירידות (drawdown)
- הגבלת הפסדים יומיים
- בדיקת הסיכון למסחר בודד
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, date
import numpy as np


@dataclass
class RiskMetrics:
    """מדדי סיכון"""
    total_risk_amount: float  # סיכון כולל בדולרים
    total_risk_percent: float  # סיכון כולל כאחוז
    daily_loss: float  # הפסד יומי
    daily_loss_percent: float  # הפסד יומי כאחוז
    current_drawdown: float  # ירידה נוכחית
    current_drawdown_percent: float  # ירידה נוכחית כאחוז
    max_drawdown: float  # ירידה מקסימלית
    max_drawdown_percent: float  # ירידה מקסימלית כאחוז
    num_positions: int  # מספר פוזיציות פתוחות
    is_safe_to_trade: bool  # האם בטוח לסחור
    warnings: List[str]  # אזהרות


class RiskCalculator:
    """מחלקה לחישוב וניטור סיכונים"""
    
    def __init__(self, config: Dict):
        """
        אתחול
        
        Args:
            config: קונפיגורציה מקובץ risk_management.yaml
        """
        self.config = config
        
        # Account settings
        account_config = config.get('account', {})
        self.initial_capital = account_config.get('initial_capital', 100000)
        
        # Risk limits
        self.max_risk_per_trade_percent = account_config.get(
            'max_risk_per_trade_percent', 2.0
        )
        self.max_risk_per_trade_amount = account_config.get(
            'max_risk_per_trade_amount', 2000
        )
        self.max_portfolio_risk_percent = account_config.get(
            'max_portfolio_risk_percent', 10.0
        )
        self.max_drawdown_percent = account_config.get(
            'max_drawdown_percent', 5.0
        )
        
        # Daily limits
        self.max_daily_loss_percent = account_config.get(
            'max_daily_loss_percent', 3.0
        )
        self.max_daily_loss_amount = account_config.get(
            'max_daily_loss_amount', 3000
        )
        
        # Position limits
        position_config = config.get('position', {})
        self.max_positions = position_config.get('max_positions', 5)
        
        # Tracking
        self.peak_balance = self.initial_capital
        self.daily_start_balance = self.initial_capital
        self.current_date = date.today()
        
    def calculate_risk_metrics(
        self,
        current_balance: float,
        open_positions: List[Dict],
        today_pnl: float = 0.0
    ) -> RiskMetrics:
        """
        חישוב כל מדדי הסיכון
        
        Args:
            current_balance: יתרת חשבון נוכחית
            open_positions: רשימת פוזיציות פתוחות
            today_pnl: רווח/הפסד היום
            
        Returns:
            מדדי סיכון
        """
        warnings = []
        
        # Update peak if needed
        if current_balance > self.peak_balance:
            self.peak_balance = current_balance
        
        # Calculate total risk from open positions
        total_risk = 0.0
        for pos in open_positions:
            position_risk = self._calculate_position_risk(pos)
            total_risk += position_risk
        
        total_risk_percent = (total_risk / current_balance) * 100
        
        # Calculate drawdown
        current_drawdown = self.peak_balance - current_balance
        current_drawdown_percent = (current_drawdown / self.peak_balance) * 100
        
        # Daily loss
        daily_loss = -today_pnl if today_pnl < 0 else 0.0
        daily_loss_percent = (daily_loss / self.daily_start_balance) * 100
        
        # Check if safe to trade
        is_safe = True
        
        # Check 1: Portfolio risk limit
        if total_risk_percent > self.max_portfolio_risk_percent:
            is_safe = False
            warnings.append(
                f"Portfolio risk ({total_risk_percent:.1f}%) exceeds limit "
                f"({self.max_portfolio_risk_percent:.1f}%)"
            )
        
        # Check 2: Drawdown limit
        if current_drawdown_percent > self.max_drawdown_percent:
            is_safe = False
            warnings.append(
                f"Drawdown ({current_drawdown_percent:.1f}%) exceeds limit "
                f"({self.max_drawdown_percent:.1f}%)"
            )
        
        # Check 3: Daily loss limit
        if daily_loss_percent > self.max_daily_loss_percent:
            is_safe = False
            warnings.append(
                f"Daily loss ({daily_loss_percent:.1f}%) exceeds limit "
                f"({self.max_daily_loss_percent:.1f}%)"
            )
        
        if daily_loss > self.max_daily_loss_amount:
            is_safe = False
            warnings.append(
                f"Daily loss (${daily_loss:.2f}) exceeds limit "
                f"(${self.max_daily_loss_amount:.2f})"
            )
        
        # Check 4: Max positions
        if len(open_positions) >= self.max_positions:
            warnings.append(
                f"Maximum positions ({self.max_positions}) reached"
            )
        
        return RiskMetrics(
            total_risk_amount=total_risk,
            total_risk_percent=total_risk_percent,
            daily_loss=daily_loss,
            daily_loss_percent=daily_loss_percent,
            current_drawdown=current_drawdown,
            current_drawdown_percent=current_drawdown_percent,
            max_drawdown=current_drawdown,  # This session's max
            max_drawdown_percent=current_drawdown_percent,
            num_positions=len(open_positions),
            is_safe_to_trade=is_safe,
            warnings=warnings
        )
    
    def can_open_new_position(
        self,
        current_balance: float,
        open_positions: List[Dict],
        new_position_risk: float
    ) -> Tuple[bool, str]:
        """
        בדיקה האם ניתן לפתוח פוזיציה חדשה
        
        Args:
            current_balance: יתרת חשבון
            open_positions: פוזיציות פתוחות
            new_position_risk: סיכון של הפוזיציה החדשה
            
        Returns:
            (האם מותר, סיבה)
        """
        # Check 1: Max positions
        if len(open_positions) >= self.max_positions:
            return False, f"Maximum {self.max_positions} positions reached"
        
        # Check 2: Single trade risk
        new_risk_percent = (new_position_risk / current_balance) * 100
        if new_risk_percent > self.max_risk_per_trade_percent:
            return False, (
                f"Trade risk ({new_risk_percent:.1f}%) exceeds "
                f"max ({self.max_risk_per_trade_percent:.1f}%)"
            )
        
        if new_position_risk > self.max_risk_per_trade_amount:
            return False, (
                f"Trade risk (${new_position_risk:.2f}) exceeds "
                f"max (${self.max_risk_per_trade_amount:.2f})"
            )
        
        # Check 3: Portfolio risk
        current_total_risk = sum(
            self._calculate_position_risk(pos) for pos in open_positions
        )
        total_risk_with_new = current_total_risk + new_position_risk
        total_risk_percent = (total_risk_with_new / current_balance) * 100
        
        if total_risk_percent > self.max_portfolio_risk_percent:
            return False, (
                f"Total portfolio risk ({total_risk_percent:.1f}%) would exceed "
                f"limit ({self.max_portfolio_risk_percent:.1f}%)"
            )
        
        return True, "Position allowed"
    
    def _calculate_position_risk(self, position: Dict) -> float:
        """
        חישוב סיכון לפוזיציה בודדת
        
        Args:
            position: מידע על הפוזיציה
            
        Returns:
            סיכון בדולרים
        """
        shares = position.get('shares', 0)
        entry_price = position.get('entry_price', 0)
        stop_loss = position.get('stop_loss', entry_price * 0.98)
        
        risk_per_share = abs(entry_price - stop_loss)
        return shares * risk_per_share
    
    def calculate_optimal_portfolio_heat(
        self,
        current_balance: float,
        open_positions: List[Dict]
    ) -> float:
        """
        חישוב "חום" התיק - כמה סיכון נשאר
        
        Returns:
            אחוז סיכון זמין (0-100)
        """
        total_risk = sum(
            self._calculate_position_risk(pos) for pos in open_positions
        )
        total_risk_percent = (total_risk / current_balance) * 100
        
        available_risk = self.max_portfolio_risk_percent - total_risk_percent
        
        return max(0, available_risk)
    
    def should_reduce_risk(
        self,
        current_balance: float,
        open_positions: List[Dict]
    ) -> Tuple[bool, str]:
        """
        בדיקה האם צריך להקטין סיכון
        
        Returns:
            (האם להקטין, סיבה)
        """
        # Calculate drawdown
        drawdown_percent = (
            (self.peak_balance - current_balance) / self.peak_balance
        ) * 100
        
        # Reduce risk if approaching limits
        if drawdown_percent > self.max_drawdown_percent * 0.8:
            return True, "Approaching maximum drawdown"
        
        # Calculate portfolio risk
        total_risk = sum(
            self._calculate_position_risk(pos) for pos in open_positions
        )
        risk_percent = (total_risk / current_balance) * 100
        
        if risk_percent > self.max_portfolio_risk_percent * 0.9:
            return True, "Portfolio risk too high"
        
        return False, "Risk levels acceptable"
    
    def reset_daily_tracking(self, current_balance: float):
        """איפוס מעקב יומי - לקרוא בתחילת יום מסחר"""
        self.current_date = date.today()
        self.daily_start_balance = current_balance
    
    def update_peak_balance(self, current_balance: float):
        """עדכון שיא החשבון"""
        if current_balance > self.peak_balance:
            self.peak_balance = current_balance
    
    def get_risk_summary(self, metrics: RiskMetrics) -> str:
        """
        קבלת סיכום סיכונים בפורמט טקסט
        
        Args:
            metrics: מדדי סיכון
            
        Returns:
            סיכום טקסטואלי
        """
        summary = []
        summary.append("=== Risk Summary ===")
        summary.append(f"Total Portfolio Risk: ${metrics.total_risk_amount:.2f} "
                      f"({metrics.total_risk_percent:.1f}%)")
        summary.append(f"Current Drawdown: ${metrics.current_drawdown:.2f} "
                      f"({metrics.current_drawdown_percent:.1f}%)")
        summary.append(f"Daily Loss: ${metrics.daily_loss:.2f} "
                      f"({metrics.daily_loss_percent:.1f}%)")
        summary.append(f"Open Positions: {metrics.num_positions}/{self.max_positions}")
        summary.append(f"Safe to Trade: {'YES [OK]' if metrics.is_safe_to_trade else 'NO [ERROR]'}")
        
        if metrics.warnings:
            summary.append("\n[WARN] Warnings:")
            for warning in metrics.warnings:
                summary.append(f"  - {warning}")
        
        return "\n".join(summary)
