"""
🛡️ Advanced Risk Calculator - Multi-Layer Risk Management System
================================================================

מערכת ניהול סיכונים מתקדמת עם בדיקות בטיחות מרובות שכבות:
- בדיקת סף גלובלית לפני כל עסקה
- חישוב "חום" התיק (Portfolio Heat)
- ולידציה כפולה לפוזיציות חדשות
- מעקב אחר שיאי חשבון ו-Drawdown

Author: T-R Trading System
Version: 3.1.0
Date: November 2, 2025
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List, Any
import logging
import yaml
from pathlib import Path


class AdvancedRiskCalculator:
    """
    🎯 מחלקת ניהול סיכונים מתקדמת עם בדיקות בטיחות מרובות שכבות
    
    Features:
    --------
    1. Global Risk Assessment - בדיקת סף גלובלית
    2. Portfolio Heat Calculation - חישוב חום תיק
    3. Peak Balance Tracking - מעקב שיאי חשבון
    4. Multi-Layer Validation - ולידציה מרובת שכבות
    5. Real-time Risk Monitoring - ניטור בזמן אמת
    """
    
    def __init__(self, 
                 max_daily_loss: float = 0.05,        # 5% הפסד מקסימלי יומי
                 max_total_drawdown: float = 0.15,    # 15% drawdown מקסימלי
                 max_portfolio_heat: float = 0.25,    # 25% "חום" תיק מקסימלי
                 max_single_position_risk: float = 0.03,  # 3% סיכון למניה
                 stop_loss_percent: float = 0.25,     # 25% stop loss
                 config_path: Optional[str] = None):
        
        # 🔔 Initialize logging first
        self.logger = logging.getLogger(__name__)
        
        # Load configuration if provided
        if config_path and Path(config_path).exists():
            self._load_config(config_path)
        else:
            self.max_daily_loss = max_daily_loss
            self.max_total_drawdown = max_total_drawdown
            self.max_portfolio_heat = max_portfolio_heat
            self.max_single_position_risk = max_single_position_risk
            self.stop_loss_percent = stop_loss_percent
        
        # 📊 Tracking Variables
        self.peak_balance = 0.0
        self.daily_start_balance = 0.0
        self.last_update_date = None
        self.daily_pnl = 0.0
        
        # 📈 Position Tracking
        self.open_positions = {}
        self.trade_count_today = 0
        self.max_daily_trades = 50
        
        # 🔔 Alerts and Logging - already initialized above
        self.alert_thresholds = {
            'drawdown_warning': 0.10,    # 10% drawdown warning
            'daily_loss_warning': 0.03,  # 3% daily loss warning
            'heat_warning': 0.20         # 20% portfolio heat warning
        }
        
        # 📊 Performance Tracking
        self.risk_metrics_history = []
        self.violation_count = 0
        
        self.logger.info("🛡️ Advanced Risk Calculator initialized")
        self.logger.info(f"   Max Daily Loss: {self.max_daily_loss:.1%}")
        self.logger.info(f"   Max Drawdown: {self.max_total_drawdown:.1%}")
        self.logger.info(f"   Max Portfolio Heat: {self.max_portfolio_heat:.1%}")
        self.logger.info(f"   Max Single Position Risk: {self.max_single_position_risk:.1%}")
    
    def _load_config(self, config_path: str) -> None:
        """Load risk management configuration from YAML file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                risk_config = config.get('risk_management', {})
                
                self.max_daily_loss = risk_config.get('max_daily_loss', 0.05)
                self.max_total_drawdown = risk_config.get('max_total_drawdown', 0.15)
                self.max_portfolio_heat = risk_config.get('max_portfolio_heat', 0.25)
                self.max_single_position_risk = risk_config.get('max_single_position_risk', 0.03)
                self.stop_loss_percent = risk_config.get('stop_loss_percent', 0.25)
                
                self.logger.info(f"✅ Risk config loaded from {config_path}")
        except Exception as e:
            # Set default values if config loading fails
            self.max_daily_loss = 0.05
            self.max_total_drawdown = 0.15
            self.max_portfolio_heat = 0.25
            self.max_single_position_risk = 0.03
            self.stop_loss_percent = 0.25
            
            self.logger.warning(f"⚠️ Failed to load config from {config_path}: {e}")
            self.logger.info("📋 Using default risk parameters")
    
    def calculate_risk_metrics(self, current_balance: float, 
                             current_positions: Dict) -> Dict[str, Any]:
        """
        🎯 חישוב מדדי סיכון כלליים - בדיקת סף גלובלית
        
        This is the MAIN risk assessment function that should be called
        before ANY trading decision.
        
        Parameters:
        -----------
        current_balance : float
            Current account balance
        current_positions : Dict
            Dictionary of current open positions
        
        Returns:
        --------
        Dict containing comprehensive risk metrics and safety status
        """
        
        # 🏆 Update peak balance if needed
        if current_balance > self.peak_balance:
            old_peak = self.peak_balance
            self.peak_balance = current_balance
            if old_peak > 0:  # Don't log on first initialization
                self.logger.info(f"🏆 NEW PEAK BALANCE: ${current_balance:,.2f} (Previous: ${old_peak:,.2f})")
        
        # 📅 Daily tracking update
        today = datetime.now().date()
        if self.last_update_date != today:
            self.daily_start_balance = current_balance
            self.daily_pnl = 0.0
            self.trade_count_today = 0
            self.last_update_date = today
            self.logger.info(f"📅 Daily Reset - Starting Balance: ${current_balance:,.2f}")
        
        # 📉 Calculate current drawdown
        current_drawdown = 0.0
        if self.peak_balance > 0:
            current_drawdown = (self.peak_balance - current_balance) / self.peak_balance
        
        # 📊 Calculate daily loss/gain
        daily_pnl_percent = 0.0
        if self.daily_start_balance > 0:
            daily_pnl_percent = (current_balance - self.daily_start_balance) / self.daily_start_balance
        
        daily_loss = abs(min(0, daily_pnl_percent))  # Only losses, as positive number
        
        # 🔥 Calculate portfolio heat (open risk)
        portfolio_heat = self._calculate_portfolio_heat(current_positions, current_balance)
        
        # 🛡️ Global safety assessment
        safety_checks = {
            'daily_loss_ok': daily_loss <= self.max_daily_loss,
            'drawdown_ok': current_drawdown <= self.max_total_drawdown,
            'portfolio_heat_ok': portfolio_heat <= self.max_portfolio_heat,
            'trade_count_ok': self.trade_count_today < self.max_daily_trades
        }
        
        is_safe_to_trade = all(safety_checks.values())
        
        # 🔔 Warning alerts
        self._check_warning_thresholds(current_drawdown, daily_loss, portfolio_heat)
        
        # 📊 Compile comprehensive metrics
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'current_balance': current_balance,
            'peak_balance': self.peak_balance,
            'daily_start_balance': self.daily_start_balance,
            'current_drawdown': current_drawdown,
            'daily_pnl_percent': daily_pnl_percent,
            'daily_loss': daily_loss,
            'portfolio_heat': portfolio_heat,
            'trade_count_today': self.trade_count_today,
            'is_safe_to_trade': is_safe_to_trade,
            'safety_checks': safety_checks,
            'risk_limits': {
                'max_daily_loss': self.max_daily_loss,
                'max_drawdown': self.max_total_drawdown,
                'max_portfolio_heat': self.max_portfolio_heat,
                'max_daily_trades': self.max_daily_trades
            },
            'violation_count': self.violation_count
        }
        
        # 🚨 Log violations
        if not is_safe_to_trade:
            self.violation_count += 1
            self.logger.warning(f"🚨 TRADING HALTED - Risk limits exceeded! (Violation #{self.violation_count})")
            
            for check, status in safety_checks.items():
                if not status:
                    if check == 'daily_loss_ok':
                        self.logger.warning(f"   ❌ Daily loss: {daily_loss:.2%} > {self.max_daily_loss:.2%}")
                    elif check == 'drawdown_ok':
                        self.logger.warning(f"   ❌ Drawdown: {current_drawdown:.2%} > {self.max_total_drawdown:.2%}")
                    elif check == 'portfolio_heat_ok':
                        self.logger.warning(f"   ❌ Portfolio heat: {portfolio_heat:.2%} > {self.max_portfolio_heat:.2%}")
                    elif check == 'trade_count_ok':
                        self.logger.warning(f"   ❌ Daily trades: {self.trade_count_today} >= {self.max_daily_trades}")
        
        # Store for historical analysis
        self.risk_metrics_history.append(metrics)
        
        # Keep only last 100 records
        if len(self.risk_metrics_history) > 100:
            self.risk_metrics_history = self.risk_metrics_history[-100:]
        
        return metrics
    
    def _calculate_portfolio_heat(self, positions: Dict, current_balance: float) -> float:
        """
        🔥 חישוב "חום" התיק - כמה סיכון פתוח יש בתיק
        
        Portfolio Heat = Total potential loss from all positions if stop losses hit
        """
        if current_balance <= 0:
            return 0.0
        
        total_risk = 0.0
        
        for symbol, position in positions.items():
            try:
                if isinstance(position, dict) and 'quantity' in position:
                    qty = abs(position.get('quantity', 0))
                    if qty == 0:
                        continue
                    
                    entry_price = position.get('entry_price', 0)
                    current_price = position.get('current_price', entry_price)
                    
                    if entry_price <= 0 or current_price <= 0:
                        continue
                    
                    # Calculate position value
                    position_value = qty * current_price
                    
                    # Calculate potential loss if stop loss hits
                    position_risk = position_value * self.stop_loss_percent
                    total_risk += position_risk
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Error calculating heat for {symbol}: {e}")
                continue
        
        # Return percentage of account balance
        heat_percent = total_risk / current_balance
        return min(1.0, heat_percent)  # Cap at 100%
    
    def calculate_optimal_portfolio_heat(self, current_balance: float, 
                                       current_positions: Dict) -> float:
        """
        📊 חישוב כמה "חום" (סיכון) פנוי נשאר בתיק
        
        Returns available portfolio heat capacity for new positions.
        """
        current_heat = self._calculate_portfolio_heat(current_positions, current_balance)
        available_heat = max(0, self.max_portfolio_heat - current_heat)
        
        self.logger.info(f"🔥 Portfolio Heat Analysis:")
        self.logger.info(f"   Current Heat: {current_heat:.2%}")
        self.logger.info(f"   Available Heat: {available_heat:.2%}")
        self.logger.info(f"   Heat Limit: {self.max_portfolio_heat:.2%}")
        
        return available_heat
    
    def can_open_new_position(self, symbol: str, position_size: float, 
                            entry_price: float, current_balance: float, 
                            current_positions: Dict) -> Tuple[bool, str]:
        """
        🎯 ולידציה כפולה - בדיקה סופית לפני פתיחת פוזיציה
        
        This is the FINAL validation before executing any trade.
        """
        
        # 🔍 Validation 1: Single position risk
        if entry_price <= 0:
            return False, "Invalid entry price"
        
        quantity = position_size / entry_price
        single_position_risk = (position_size * self.stop_loss_percent) / current_balance
        
        if single_position_risk > self.max_single_position_risk:
            return False, f"Single position risk {single_position_risk:.2%} > max {self.max_single_position_risk:.2%}"
        
        # 🔍 Validation 2: Portfolio heat after new position
        simulated_positions = current_positions.copy()
        simulated_positions[symbol] = {
            'quantity': quantity,
            'entry_price': entry_price,
            'current_price': entry_price
        }
        
        future_heat = self._calculate_portfolio_heat(simulated_positions, current_balance)
        if future_heat > self.max_portfolio_heat:
            return False, f"Portfolio heat after trade {future_heat:.2%} > max {self.max_portfolio_heat:.2%}"
        
        # 🔍 Validation 3: Global risk metrics
        risk_metrics = self.calculate_risk_metrics(current_balance, current_positions)
        if not risk_metrics['is_safe_to_trade']:
            violations = [check for check, status in risk_metrics['safety_checks'].items() if not status]
            return False, f"Global risk violations: {', '.join(violations)}"
        
        # ✅ All validations passed
        approval_msg = f"Position approved - Risk: {single_position_risk:.2%}, Future Heat: {future_heat:.2%}"
        self.logger.info(f"✅ {symbol}: {approval_msg}")
        
        return True, approval_msg
    
    def update_peak_balance(self, current_balance: float) -> None:
        """
        🏆 עדכון שיא החשבון - להפעלה בסוף כל יום מסחר
        """
        old_peak = self.peak_balance
        
        if current_balance > self.peak_balance:
            self.peak_balance = current_balance
            gain = ((current_balance - old_peak) / old_peak * 100) if old_peak > 0 else 0
            self.logger.info(f"🏆 NEW PEAK BALANCE: ${current_balance:,.2f} (+{gain:.1f}%)")
        
        # Daily summary log
        today = datetime.now().date()
        if self.last_update_date != today:
            daily_pnl = current_balance - self.daily_start_balance if self.daily_start_balance > 0 else 0
            daily_pnl_percent = (daily_pnl / self.daily_start_balance * 100) if self.daily_start_balance > 0 else 0
            
            self.logger.info(f"📅 Daily Update Summary:")
            self.logger.info(f"   Date: {today}")
            self.logger.info(f"   Peak Balance: ${self.peak_balance:,.2f}")
            self.logger.info(f"   Current Balance: ${current_balance:,.2f}")
            self.logger.info(f"   Daily P&L: ${daily_pnl:,.2f} ({daily_pnl_percent:+.2f}%)")
            self.logger.info(f"   Trades Today: {self.trade_count_today}")
            
            self.last_update_date = today
    
    def get_position_size_limit(self, current_balance: float, 
                              available_heat: float) -> float:
        """
        💰 חישוב גודל פוזיציה מקסימלי בהתבסס על החום הפנוי
        """
        # Calculate max size based on available heat
        max_size_by_heat = (available_heat * current_balance) / self.stop_loss_percent
        
        # Calculate max size based on single position risk
        max_size_by_single = (self.max_single_position_risk * current_balance) / self.stop_loss_percent
        
        # Take the smaller of the two
        max_position_size = min(max_size_by_heat, max_size_by_single)
        
        self.logger.debug(f"💰 Position Size Limits:")
        self.logger.debug(f"   By Heat: ${max_size_by_heat:,.2f}")
        self.logger.debug(f"   By Single Risk: ${max_size_by_single:,.2f}")
        self.logger.debug(f"   Final Limit: ${max_position_size:,.2f}")
        
        return max_position_size
    
    def _check_warning_thresholds(self, drawdown: float, daily_loss: float, heat: float) -> None:
        """🔔 Check and issue warnings for approaching risk limits"""
        
        if drawdown >= self.alert_thresholds['drawdown_warning']:
            self.logger.warning(f"⚠️ DRAWDOWN WARNING: {drawdown:.2%} (Limit: {self.max_total_drawdown:.2%})")
        
        if daily_loss >= self.alert_thresholds['daily_loss_warning']:
            self.logger.warning(f"⚠️ DAILY LOSS WARNING: {daily_loss:.2%} (Limit: {self.max_daily_loss:.2%})")
        
        if heat >= self.alert_thresholds['heat_warning']:
            self.logger.warning(f"⚠️ PORTFOLIO HEAT WARNING: {heat:.2%} (Limit: {self.max_portfolio_heat:.2%})")
    
    def increment_trade_count(self) -> None:
        """📊 Increment daily trade counter"""
        self.trade_count_today += 1
        self.logger.debug(f"📊 Trade count updated: {self.trade_count_today}/{self.max_daily_trades}")
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """📋 Get comprehensive risk management summary"""
        return {
            'peak_balance': self.peak_balance,
            'daily_start_balance': self.daily_start_balance,
            'trade_count_today': self.trade_count_today,
            'violation_count': self.violation_count,
            'last_update': self.last_update_date.isoformat() if self.last_update_date else None,
            'limits': {
                'max_daily_loss': self.max_daily_loss,
                'max_total_drawdown': self.max_total_drawdown,
                'max_portfolio_heat': self.max_portfolio_heat,
                'max_single_position_risk': self.max_single_position_risk,
                'stop_loss_percent': self.stop_loss_percent
            }
        }


if __name__ == "__main__":
    # 🧪 Test the Advanced Risk Calculator
    print("🛡️ Testing Advanced Risk Calculator...")
    
    # Initialize with test parameters
    risk_calc = AdvancedRiskCalculator(
        max_daily_loss=0.05,
        max_total_drawdown=0.15,
        max_portfolio_heat=0.25,
        max_single_position_risk=0.03
    )
    
    # Test with sample data
    test_balance = 100000.0
    test_positions = {
        'AAPL': {'quantity': 100, 'entry_price': 150.0, 'current_price': 152.0},
        'GOOGL': {'quantity': 50, 'entry_price': 2800.0, 'current_price': 2850.0}
    }
    
    # Calculate risk metrics
    metrics = risk_calc.calculate_risk_metrics(test_balance, test_positions)
    
    print(f"\n📊 Risk Metrics Test Results:")
    print(f"   Balance: ${metrics['current_balance']:,.2f}")
    print(f"   Portfolio Heat: {metrics['portfolio_heat']:.2%}")
    print(f"   Safe to Trade: {'✅ YES' if metrics['is_safe_to_trade'] else '❌ NO'}")
    
    # Test position validation
    can_open, message = risk_calc.can_open_new_position('MSFT', 15000, 300.0, test_balance, test_positions)
    print(f"\n🎯 Position Validation Test:")
    print(f"   Can Open MSFT Position: {'✅ YES' if can_open else '❌ NO'}")
    print(f"   Message: {message}")
    
    print("\n✅ Advanced Risk Calculator test completed!")