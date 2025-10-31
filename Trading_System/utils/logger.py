"""
Advanced Logger Module

Detailed logging system with severity levels, file rotation, and archival.

Author: Trading System
Date: October 29, 2025
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import yaml


class TradingLogger:
    """
    Advanced logging system for the trading platform.
    
    Features:
    - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - File rotation by size and time
    - Separate logs for different components
    - Console and file output
    - Structured log formatting
    - Log archival
    """
    
    def __init__(self, 
                 name: str = "TradingSystem",
                 log_dir: str = "logs",
                 config_path: str = "config/trading_config.yaml"):
        """
        Initialize logger.
        
        Args:
            name: Logger name
            log_dir: Directory for log files
            config_path: Path to configuration file
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Load configuration
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            self.log_level = self.config.get('system', {}).get('log_level', 'INFO')
        except:
            self.log_level = 'INFO'
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, self.log_level))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set up handlers
        self._setup_console_handler()
        self._setup_file_handlers()
        
        self.logger.info(f"Logger initialized - Level: {self.log_level}")
    
    def _setup_console_handler(self):
        """Set up console handler with formatting."""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Console formatter (simpler, colored if possible)
        console_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        
        self.logger.addHandler(console_handler)
    
    def _setup_file_handlers(self):
        """Set up file handlers with rotation."""
        # Main log file (all messages)
        main_log = self.log_dir / f"{self.name}_main.log"
        main_handler = logging.handlers.RotatingFileHandler(
            main_log,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        main_handler.setLevel(logging.DEBUG)
        
        # Error log file (errors and critical only)
        error_log = self.log_dir / f"{self.name}_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        # Daily log file (rotates daily)
        daily_log = self.log_dir / f"{self.name}_daily.log"
        daily_handler = logging.handlers.TimedRotatingFileHandler(
            daily_log,
            when='midnight',
            interval=1,
            backupCount=30,  # Keep 30 days
            encoding='utf-8'
        )
        daily_handler.setLevel(logging.INFO)
        
        # Detailed formatter for files
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        main_handler.setFormatter(file_format)
        error_handler.setFormatter(file_format)
        daily_handler.setFormatter(file_format)
        
        self.logger.addHandler(main_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(daily_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, exc_info: bool = False, **kwargs):
        """
        Log error message.
        
        Args:
            message: Error message
            exc_info: Include exception info
            **kwargs: Additional context
        """
        self.logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def critical(self, message: str, exc_info: bool = True, **kwargs):
        """
        Log critical message.
        
        Args:
            message: Critical message
            exc_info: Include exception info
            **kwargs: Additional context
        """
        self.logger.critical(message, exc_info=exc_info, extra=kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback."""
        self.logger.exception(message, extra=kwargs)
    
    def get_logger(self) -> logging.Logger:
        """
        Get underlying logger instance.
        
        Returns:
            Logger instance
        """
        return self.logger


class ComponentLogger:
    """
    Component-specific logger.
    
    Creates a logger for a specific component with its own file.
    """
    
    def __init__(self, 
                 component_name: str,
                 log_dir: str = "logs",
                 parent_logger: Optional[logging.Logger] = None):
        """
        Initialize component logger.
        
        Args:
            component_name: Name of the component
            log_dir: Directory for log files
            parent_logger: Parent logger (optional)
        """
        self.component_name = component_name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        if parent_logger:
            self.logger = parent_logger.getChild(component_name)
        else:
            self.logger = logging.getLogger(component_name)
        
        # Component-specific file handler
        component_log = self.log_dir / f"{component_name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            component_log,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        """Log error message."""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = True):
        """Log critical message."""
        self.logger.critical(message, exc_info=exc_info)
    
    def exception(self, message: str):
        """Log exception with traceback."""
        self.logger.exception(message)


class TradeLogger:
    """
    Specialized logger for trade execution.
    
    Logs all trade-related activities with structured formatting.
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize trade logger.
        
        Args:
            log_dir: Directory for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger("TradeLogger")
        self.logger.setLevel(logging.INFO)
        
        # Trade log file
        trade_log = self.log_dir / "trades.log"
        file_handler = logging.handlers.RotatingFileHandler(
            trade_log,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        
        # CSV-style format for easy parsing
        trade_format = logging.Formatter(
            '%(asctime)s,%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(trade_format)
        
        self.logger.addHandler(file_handler)
    
    def log_signal(self, symbol: str, signal_type: str, strength: str, 
                   price: float, strategy: str):
        """Log trading signal."""
        message = f"SIGNAL,{symbol},{signal_type},{strength},{price:.2f},{strategy}"
        self.logger.info(message)
    
    def log_order(self, order_id: int, symbol: str, action: str, 
                 quantity: int, order_type: str, price: Optional[float] = None):
        """Log order submission."""
        price_str = f"{price:.2f}" if price else "MARKET"
        message = f"ORDER,{order_id},{symbol},{action},{quantity},{order_type},{price_str}"
        self.logger.info(message)
    
    def log_fill(self, order_id: int, symbol: str, quantity: int, 
                price: float, commission: float):
        """Log order fill."""
        message = f"FILL,{order_id},{symbol},{quantity},{price:.2f},{commission:.2f}"
        self.logger.info(message)
    
    def log_position_open(self, symbol: str, side: str, quantity: int, 
                         entry_price: float, strategy: str):
        """Log position opening."""
        message = f"POSITION_OPEN,{symbol},{side},{quantity},{entry_price:.2f},{strategy}"
        self.logger.info(message)
    
    def log_position_close(self, symbol: str, side: str, quantity: int, 
                          entry_price: float, exit_price: float, pnl: float):
        """Log position closing."""
        message = (f"POSITION_CLOSE,{symbol},{side},{quantity},"
                  f"{entry_price:.2f},{exit_price:.2f},{pnl:.2f}")
        self.logger.info(message)
    
    def log_error(self, component: str, error_type: str, error_message: str):
        """Log trading error."""
        message = f"ERROR,{component},{error_type},{error_message}"
        self.logger.error(message)


def setup_logging(log_dir: str = "logs", 
                 log_level: str = "INFO",
                 config_path: str = "config/trading_config.yaml") -> TradingLogger:
    """
    Set up logging for the entire trading system.
    
    Args:
        log_dir: Directory for log files
        log_level: Logging level
        config_path: Configuration file path
        
    Returns:
        TradingLogger instance
    """
    # Create log directory
    Path(log_dir).mkdir(exist_ok=True)
    
    # Create main logger
    main_logger = TradingLogger(
        name="TradingSystem",
        log_dir=log_dir,
        config_path=config_path
    )
    
    return main_logger


def get_component_logger(component_name: str, 
                        log_dir: str = "logs") -> ComponentLogger:
    """
    Get a logger for a specific component.
    
    Args:
        component_name: Name of the component
        log_dir: Directory for log files
        
    Returns:
        ComponentLogger instance
    """
    return ComponentLogger(component_name, log_dir)


def get_trade_logger(log_dir: str = "logs") -> TradeLogger:
    """
    Get the trade logger.
    
    Args:
        log_dir: Directory for log files
        
    Returns:
        TradeLogger instance
    """
    return TradeLogger(log_dir)


# Example usage
if __name__ == "__main__":
    # Set up main logger
    logger = setup_logging()
    
    # Log some messages
    logger.info("Trading system starting...")
    logger.debug("This is a debug message")
    logger.warning("This is a warning")
    
    # Get component logger
    strategy_logger = get_component_logger("Strategy")
    strategy_logger.info("Strategy initialized")
    
    # Get trade logger
    trade_logger = get_trade_logger()
    trade_logger.log_signal("AAPL", "BUY", "STRONG", 150.25, "EMA_Cross")
    trade_logger.log_order(12345, "AAPL", "BUY", 100, "MARKET")
    
    print("Logging test complete. Check logs/ directory.")
