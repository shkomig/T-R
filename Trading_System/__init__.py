"""
Trading System Package
======================

AI-powered automated trading system for Interactive Brokers.
Focuses on 30-minute candles with low-risk strategies.

Author: Trading System
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Trading System"

# Package-level imports
from .config import load_config
from .utils import setup_logging

__all__ = [
    "load_config",
    "setup_logging",
]
