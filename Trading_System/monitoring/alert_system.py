"""
Alert System Module

Sends notifications via email, Telegram, and logging for trading events,
signals, risks, and system errors.

Author: Trading System
Date: October 29, 2025
"""

import logging
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import yaml


class AlertLevel(Enum):
    """Alert severity level."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AlertType(Enum):
    """Type of alert."""
    SIGNAL = "SIGNAL"              # Trading signal generated
    ORDER = "ORDER"                # Order submitted/filled/cancelled
    POSITION = "POSITION"          # Position opened/closed
    RISK = "RISK"                  # Risk limit breached
    SYSTEM = "SYSTEM"              # System event
    ERROR = "ERROR"                # Error occurred
    PERFORMANCE = "PERFORMANCE"    # Performance milestone


class AlertSystem:
    """
    Manages alerts and notifications for the trading system.
    
    Features:
    - Email notifications
    - Telegram bot messages
    - Alert history and filtering
    - Configurable alert levels
    """
    
    def __init__(self, config_path: str = "config/trading_config.yaml"):
        """
        Initialize Alert System.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Alert configuration
        self.alerts_config = self.config.get('alerts', {})
        self.email_enabled = self.alerts_config.get('email_enabled', False)
        self.telegram_enabled = self.alerts_config.get('telegram_enabled', False)
        self.min_alert_level = AlertLevel[self.alerts_config.get('min_level', 'INFO')]
        
        # Email configuration
        self.email_config = self.alerts_config.get('email', {})
        self.smtp_server = self.email_config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = self.email_config.get('smtp_port', 587)
        self.sender_email = self.email_config.get('sender_email', '')
        self.sender_password = self.email_config.get('sender_password', '')
        self.recipient_emails = self.email_config.get('recipients', [])
        
        # Telegram configuration
        self.telegram_config = self.alerts_config.get('telegram', {})
        self.telegram_token = self.telegram_config.get('bot_token', '')
        self.telegram_chat_ids = self.telegram_config.get('chat_ids', [])
        
        # Alert history
        self.alert_history: List[Dict] = []
        self.max_history = 1000
        
        # Alert counts
        self.alert_counts = {
            AlertLevel.INFO: 0,
            AlertLevel.WARNING: 0,
            AlertLevel.ERROR: 0,
            AlertLevel.CRITICAL: 0
        }
        
        self.logger.info("AlertSystem initialized")
        self.logger.info(f"Email alerts: {self.email_enabled}, Telegram alerts: {self.telegram_enabled}")
    
    def send_alert(self, 
                   message: str,
                   alert_type: AlertType = AlertType.SYSTEM,
                   alert_level: AlertLevel = AlertLevel.INFO,
                   data: Optional[Dict] = None) -> bool:
        """
        Send an alert through configured channels.
        
        Args:
            message: Alert message
            alert_type: Type of alert
            alert_level: Severity level
            data: Additional data (optional)
            
        Returns:
            True if alert was sent successfully
        """
        # Check if alert level is high enough
        if self._should_skip_alert(alert_level):
            return False
        
        # Create alert record
        alert = {
            'timestamp': datetime.now(),
            'message': message,
            'type': alert_type.value,
            'level': alert_level.value,
            'data': data or {}
        }
        
        # Add to history
        self.alert_history.append(alert)
        if len(self.alert_history) > self.max_history:
            self.alert_history.pop(0)
        
        # Update counts
        self.alert_counts[alert_level] += 1
        
        # Format message
        formatted_message = self._format_alert(alert)
        
        # Log alert
        self._log_alert(alert_level, message)
        
        # Send through channels
        success = True
        
        if self.email_enabled:
            if not self._send_email(formatted_message, alert_level):
                success = False
        
        if self.telegram_enabled:
            if not self._send_telegram(formatted_message, alert_level):
                success = False
        
        return success
    
    def signal_alert(self, symbol: str, signal_type: str, strength: str, 
                    price: float, strategy: str):
        """
        Send trading signal alert.
        
        Args:
            symbol: Symbol
            signal_type: BUY/SELL
            strength: Signal strength
            price: Current price
            strategy: Strategy name
        """
        message = (
            f"🎯 TRADING SIGNAL\n"
            f"Symbol: {symbol}\n"
            f"Signal: {signal_type}\n"
            f"Strength: {strength}\n"
            f"Price: ${price:.2f}\n"
            f"Strategy: {strategy}"
        )
        
        data = {
            'symbol': symbol,
            'signal_type': signal_type,
            'strength': strength,
            'price': price,
            'strategy': strategy
        }
        
        self.send_alert(message, AlertType.SIGNAL, AlertLevel.INFO, data)
    
    def order_alert(self, order_id: int, symbol: str, action: str, 
                   quantity: int, order_type: str, status: str):
        """
        Send order alert.
        
        Args:
            order_id: Order ID
            symbol: Symbol
            action: BUY/SELL
            quantity: Quantity
            order_type: MARKET/LIMIT/STOP
            status: Order status
        """
        message = (
            f"📋 ORDER {status.upper()}\n"
            f"Order ID: {order_id}\n"
            f"Symbol: {symbol}\n"
            f"Action: {action}\n"
            f"Quantity: {quantity}\n"
            f"Type: {order_type}"
        )
        
        data = {
            'order_id': order_id,
            'symbol': symbol,
            'action': action,
            'quantity': quantity,
            'order_type': order_type,
            'status': status
        }
        
        level = AlertLevel.INFO if status in ['SUBMITTED', 'FILLED'] else AlertLevel.WARNING
        self.send_alert(message, AlertType.ORDER, level, data)
    
    def position_alert(self, symbol: str, action: str, quantity: int, 
                      price: float, pnl: Optional[float] = None):
        """
        Send position alert.
        
        Args:
            symbol: Symbol
            action: OPENED/CLOSED
            quantity: Quantity
            price: Entry/Exit price
            pnl: P&L (for closed positions)
        """
        message = f"💼 POSITION {action.upper()}\n"
        message += f"Symbol: {symbol}\n"
        message += f"Quantity: {quantity}\n"
        message += f"Price: ${price:.2f}\n"
        
        if pnl is not None:
            pnl_emoji = "✅" if pnl >= 0 else "❌"
            message += f"{pnl_emoji} P&L: ${pnl:,.2f}"
        
        data = {
            'symbol': symbol,
            'action': action,
            'quantity': quantity,
            'price': price,
            'pnl': pnl
        }
        
        self.send_alert(message, AlertType.POSITION, AlertLevel.INFO, data)
    
    def risk_alert(self, risk_type: str, current_value: float, 
                  limit_value: float, message_detail: str = ""):
        """
        Send risk alert.
        
        Args:
            risk_type: Type of risk (drawdown, position_size, etc.)
            current_value: Current value
            limit_value: Limit value
            message_detail: Additional details
        """
        message = (
            f"⚠️ RISK ALERT\n"
            f"Type: {risk_type}\n"
            f"Current: {current_value:.2f}\n"
            f"Limit: {limit_value:.2f}\n"
        )
        
        if message_detail:
            message += f"Details: {message_detail}"
        
        data = {
            'risk_type': risk_type,
            'current_value': current_value,
            'limit_value': limit_value,
            'message_detail': message_detail
        }
        
        self.send_alert(message, AlertType.RISK, AlertLevel.WARNING, data)
    
    def error_alert(self, error_type: str, error_message: str, 
                   component: str = "", stack_trace: str = ""):
        """
        Send error alert.
        
        Args:
            error_type: Type of error
            error_message: Error message
            component: Component where error occurred
            stack_trace: Stack trace (optional)
        """
        message = f"🚨 ERROR\n"
        
        if component:
            message += f"Component: {component}\n"
        
        message += f"Type: {error_type}\n"
        message += f"Message: {error_message}\n"
        
        if stack_trace:
            message += f"\nStack Trace:\n{stack_trace[:500]}"  # Limit length
        
        data = {
            'error_type': error_type,
            'error_message': error_message,
            'component': component
        }
        
        self.send_alert(message, AlertType.ERROR, AlertLevel.ERROR, data)
    
    def performance_alert(self, metric: str, value: float, 
                         period: str = "", is_milestone: bool = False):
        """
        Send performance alert.
        
        Args:
            metric: Performance metric
            value: Metric value
            period: Time period
            is_milestone: Is this a milestone achievement
        """
        emoji = "🎉" if is_milestone else "📊"
        message = f"{emoji} PERFORMANCE UPDATE\n"
        message += f"Metric: {metric}\n"
        message += f"Value: {value:.2f}\n"
        
        if period:
            message += f"Period: {period}"
        
        data = {
            'metric': metric,
            'value': value,
            'period': period,
            'is_milestone': is_milestone
        }
        
        level = AlertLevel.INFO if is_milestone else AlertLevel.INFO
        self.send_alert(message, AlertType.PERFORMANCE, level, data)
    
    def daily_summary(self, stats: Dict):
        """
        Send daily trading summary.
        
        Args:
            stats: Dictionary of daily statistics
        """
        message = "📈 DAILY SUMMARY\n"
        message += f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        message += f"Trades: {stats.get('trades', 0)}\n"
        message += f"Winners: {stats.get('winners', 0)}\n"
        message += f"Losers: {stats.get('losers', 0)}\n"
        message += f"Win Rate: {stats.get('win_rate', 0):.1f}%\n"
        message += f"P&L: ${stats.get('pnl', 0):,.2f}\n"
        message += f"Commission: ${stats.get('commission', 0):,.2f}"
        
        self.send_alert(message, AlertType.PERFORMANCE, AlertLevel.INFO, stats)
    
    def _should_skip_alert(self, alert_level: AlertLevel) -> bool:
        """
        Check if alert should be skipped based on min level.
        
        Args:
            alert_level: Alert level
            
        Returns:
            True if alert should be skipped
        """
        level_priority = {
            AlertLevel.INFO: 0,
            AlertLevel.WARNING: 1,
            AlertLevel.ERROR: 2,
            AlertLevel.CRITICAL: 3
        }
        
        return level_priority[alert_level] < level_priority[self.min_alert_level]
    
    def _format_alert(self, alert: Dict) -> str:
        """
        Format alert message.
        
        Args:
            alert: Alert dictionary
            
        Returns:
            Formatted message
        """
        timestamp = alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        level = alert['level']
        alert_type = alert['type']
        message = alert['message']
        
        formatted = f"[{timestamp}] [{level}] [{alert_type}]\n"
        formatted += message
        
        return formatted
    
    def _log_alert(self, level: AlertLevel, message: str):
        """
        Log alert to logger.
        
        Args:
            level: Alert level
            message: Message
        """
        if level == AlertLevel.INFO:
            self.logger.info(message)
        elif level == AlertLevel.WARNING:
            self.logger.warning(message)
        elif level == AlertLevel.ERROR:
            self.logger.error(message)
        elif level == AlertLevel.CRITICAL:
            self.logger.critical(message)
    
    def _send_email(self, message: str, level: AlertLevel) -> bool:
        """
        Send email alert.
        
        Args:
            message: Message to send
            level: Alert level
            
        Returns:
            True if sent successfully
        """
        if not self.sender_email or not self.sender_password:
            self.logger.warning("Email credentials not configured")
            return False
        
        if not self.recipient_emails:
            self.logger.warning("No recipient emails configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.recipient_emails)
            msg['Subject'] = f"Trading Alert - {level.value}"
            
            # Add body
            body = MIMEText(message, 'plain')
            msg.attach(body)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    def _send_telegram(self, message: str, level: AlertLevel) -> bool:
        """
        Send Telegram alert.
        
        Args:
            message: Message to send
            level: Alert level
            
        Returns:
            True if sent successfully
        """
        if not self.telegram_token:
            self.logger.warning("Telegram bot token not configured")
            return False
        
        if not self.telegram_chat_ids:
            self.logger.warning("No Telegram chat IDs configured")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            
            # Send to each chat ID
            for chat_id in self.telegram_chat_ids:
                data = {
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'HTML'
                }
                
                response = requests.post(url, data=data, timeout=10)
                
                if response.status_code != 200:
                    self.logger.error(f"Telegram API error: {response.text}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def get_alert_history(self, 
                         alert_type: Optional[AlertType] = None,
                         alert_level: Optional[AlertLevel] = None,
                         limit: int = 100) -> List[Dict]:
        """
        Get alert history with optional filtering.
        
        Args:
            alert_type: Filter by alert type
            alert_level: Filter by alert level
            limit: Maximum number of alerts
            
        Returns:
            List of alerts
        """
        alerts = self.alert_history
        
        # Filter by type
        if alert_type:
            alerts = [a for a in alerts if a['type'] == alert_type.value]
        
        # Filter by level
        if alert_level:
            alerts = [a for a in alerts if a['level'] == alert_level.value]
        
        # Return most recent
        return alerts[-limit:]
    
    def get_statistics(self) -> Dict:
        """
        Get alert statistics.
        
        Returns:
            Dictionary of statistics
        """
        return {
            'total_alerts': len(self.alert_history),
            'info_count': self.alert_counts[AlertLevel.INFO],
            'warning_count': self.alert_counts[AlertLevel.WARNING],
            'error_count': self.alert_counts[AlertLevel.ERROR],
            'critical_count': self.alert_counts[AlertLevel.CRITICAL],
            'email_enabled': self.email_enabled,
            'telegram_enabled': self.telegram_enabled
        }
    
    def print_statistics(self):
        """Print alert statistics."""
        stats = self.get_statistics()
        
        print("\n=== ALERT SYSTEM STATISTICS ===")
        print(f"Total Alerts: {stats['total_alerts']}")
        print(f"Info: {stats['info_count']}")
        print(f"Warnings: {stats['warning_count']}")
        print(f"Errors: {stats['error_count']}")
        print(f"Critical: {stats['critical_count']}")
        print(f"\nEmail Enabled: {stats['email_enabled']}")
        print(f"Telegram Enabled: {stats['telegram_enabled']}")
        print("=" * 30)
