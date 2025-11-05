"""
Fresh Data Broker Interface - IBKR API עם פתרון Stale Data
==========================================================
מעטפת מתקדמת לברוקר IBKR עם ניהול רעננות נתונים

תכונות מתקדמות:
- Auto-detection of stale data
- Real-time price validation 
- Connection health monitoring
- Smart refresh mechanisms
"""

import time
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
from dataclasses import dataclass

from .broker_interface import IBBroker
from .data_freshness_manager import data_freshness_manager, DataPoint

logger = logging.getLogger(__name__)

@dataclass
class PriceValidationResult:
    """תוצאת אימות מחיר"""
    symbol: str
    price: float
    is_valid: bool
    confidence: float
    reason: str
    timestamp: datetime

class FreshDataBroker(IBBroker):
    """
    🔄 ברוקר עם ניהול רעננות נתונים מתקדם
    
    פותר בעיות Stale Data נפוצות ב-IBKR API:
    1. נתונים מיושנים מ-TWS
    2. חיבורים איטיים
    3. עדכונים לא סינכרוניים
    4. אימות מחירים
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Fresh data management
        self.freshness_manager = data_freshness_manager
        self.price_validation_enabled = True
        self.min_price_change_threshold = 0.001  # 0.1% שינוי מינימלי
        self.max_price_jump_threshold = 0.20     # 20% קפיצה מקסימלית
        
        # Monitoring
        self.last_successful_request = datetime.now()
        self.connection_issues_count = 0
        self.stale_data_warnings = 0
        
        # Statistics
        self.fresh_data_stats = {
            'total_price_requests': 0,
            'stale_prices_detected': 0,
            'validation_failures': 0,
            'auto_refreshes_triggered': 0,
            'connection_recoveries': 0
        }
        
        # Start monitoring
        self.freshness_manager.start_monitoring()
        
        # Register callbacks for broker reconnection
        self.freshness_manager.set_broker_callback(self._handle_stale_data_reconnect)
        self.freshness_manager.set_connection_check_callback(self._check_connection_health)
        
        logger.info("🔄 Fresh Data Broker initialized with reconnection callbacks")
    
    def get_current_price(self, symbol: str, force_refresh: bool = False) -> Optional[float]:
        """
        קבלת מחיר נוכחי עם אימות רעננות
        
        Args:
            symbol: סימבול המניה
            force_refresh: האם לכפות רענון
            
        Returns:
            מחיר עדכני או None אם לא זמין
        """
        cache_key = f"price_{symbol}"
        self.fresh_data_stats['total_price_requests'] += 1
        
        # בדיקת cache אם לא נדרש רענון כפוי
        if not force_refresh:
            cached_price, is_fresh = self.freshness_manager.get_data(cache_key, max_age_override=15)
            if cached_price is not None and is_fresh:
                logger.debug(f"✅ Using fresh cached price for {symbol}: ${cached_price:.2f}")
                return cached_price
        
        try:
            # קבלת מחיר חדש מ-API
            new_price = self._fetch_fresh_price(symbol)
            
            if new_price is not None:
                # אימות המחיר
                validation = self._validate_price(symbol, new_price)
                
                if validation.is_valid:
                    # שמירה במטמון
                    self.freshness_manager.update_data(
                        cache_key, 
                        new_price, 
                        source=f"IBKR_API_{datetime.now().strftime('%H:%M:%S')}"
                    )
                    
                    self.last_successful_request = datetime.now()
                    logger.debug(f"✅ Fresh price for {symbol}: ${new_price:.2f}")
                    return new_price
                else:
                    logger.warning(f"🚨 Price validation failed for {symbol}: {validation.reason}")
                    self.fresh_data_stats['validation_failures'] += 1
                    
                    # חזרה למחיר cached אם קיים
                    cached_price, _ = self.freshness_manager.get_data(cache_key)
                    return cached_price
            
        except Exception as e:
            logger.error(f"❌ Error fetching fresh price for {symbol}: {e}")
            self.connection_issues_count += 1
            
            # ניסיון להחזיר מחיר cached
            cached_price, _ = self.freshness_manager.get_data(cache_key)
            if cached_price is not None:
                logger.info(f"⚠️ Using cached price for {symbol} due to error: ${cached_price:.2f}")
                return cached_price
        
        return None
    
    def _fetch_fresh_price(self, symbol: str) -> Optional[float]:
        """קבלת מחיר רענן מ-API"""
        try:
            # קריאה ל-API הבסיסי
            price_data = super().get_current_price(symbol)
            
            if price_data and price_data > 0:
                return float(price_data)
                
        except Exception as e:
            logger.error(f"❌ API error for {symbol}: {e}")
            
        return None
    
    def _validate_price(self, symbol: str, new_price: float) -> PriceValidationResult:
        """
        אימות מחיר חדש מול מחירים קודמים
        
        Args:
            symbol: סימבול המניה
            new_price: המחיר החדש
            
        Returns:
            תוצאת אימות המחיר
        """
        cache_key = f"price_{symbol}"
        
        # קבלת מחיר קודם
        cached_price, _ = self.freshness_manager.get_data(cache_key)
        
        if cached_price is None:
            # אין מחיר קודם - מקבלים את המחיר החדש
            return PriceValidationResult(
                symbol=symbol,
                price=new_price,
                is_valid=True,
                confidence=0.8,
                reason="No previous price for comparison",
                timestamp=datetime.now()
            )
        
        # חישוב שינוי באחוזים
        price_change_pct = abs(new_price - cached_price) / cached_price
        
        # בדיקות אימות
        if new_price <= 0:
            return PriceValidationResult(
                symbol=symbol,
                price=new_price,
                is_valid=False,
                confidence=0.0,
                reason="Price is zero or negative",
                timestamp=datetime.now()
            )
        
        if price_change_pct > self.max_price_jump_threshold:
            return PriceValidationResult(
                symbol=symbol,
                price=new_price,
                is_valid=False,
                confidence=0.2,
                reason=f"Price jump too large: {price_change_pct:.1%} (threshold: {self.max_price_jump_threshold:.1%})",
                timestamp=datetime.now()
            )
        
        # חישוב confidence בהתבסס על השינוי
        if price_change_pct < self.min_price_change_threshold:
            confidence = 0.9  # שינוי קטן - ביטחון גבוה
        elif price_change_pct < 0.05:  # 5%
            confidence = 0.95  # שינוי סביר - ביטחון גבוה מאוד
        elif price_change_pct < 0.10:  # 10%
            confidence = 0.8   # שינוי בינוני - ביטחון טוב
        else:
            confidence = 0.6   # שינוי גדול - ביטחון נמוך יותר
        
        return PriceValidationResult(
            symbol=symbol,
            price=new_price,
            is_valid=True,
            confidence=confidence,
            reason=f"Price change: {price_change_pct:.2%}",
            timestamp=datetime.now()
        )
    
    def get_account_summary(self, force_refresh: bool = False) -> Dict:
        """קבלת סיכום חשבון עם רעננות"""
        cache_key = "account_summary"
        
        if not force_refresh:
            cached_data, is_fresh = self.freshness_manager.get_data(cache_key, max_age_override=30)
            if cached_data is not None and is_fresh:
                return cached_data
        
        try:
            account_data = super().get_account_summary()
            if account_data:
                self.freshness_manager.update_data(
                    cache_key, 
                    account_data, 
                    source="IBKR_Account_API"
                )
                return account_data
        except Exception as e:
            logger.error(f"❌ Error getting account summary: {e}")
            
            # חזרה לנתונים cached
            cached_data, _ = self.freshness_manager.get_data(cache_key)
            if cached_data:
                logger.info("⚠️ Using cached account data due to error")
                return cached_data
        
        return {}
    
    def get_positions(self, force_refresh: bool = False) -> List:
        """קבלת פוזיציות עם רעננות"""
        cache_key = "positions"
        
        if not force_refresh:
            cached_data, is_fresh = self.freshness_manager.get_data(cache_key, max_age_override=20)
            if cached_data is not None and is_fresh:
                return cached_data
        
        try:
            positions_data = super().get_positions()
            if positions_data is not None:
                self.freshness_manager.update_data(
                    cache_key, 
                    positions_data, 
                    source="IBKR_Positions_API"
                )
                return positions_data
        except Exception as e:
            logger.error(f"❌ Error getting positions: {e}")
            
            # חזרה לנתונים cached
            cached_data, _ = self.freshness_manager.get_data(cache_key)
            if cached_data:
                logger.info("⚠️ Using cached positions data due to error")
                return cached_data
        
        return []
    
    def get_historical_data(self, symbol: str, duration: str = "1 D", 
                          bar_size: str = "30 mins", what_to_show: str = "TRADES", 
                          force_refresh: bool = False, **kwargs) -> Optional[Any]:
        """קבלת נתונים היסטוריים עם רעננות - תומך בפרמטרים פוזיציוניים וקוואורדיים"""
        cache_key = f"historical_{symbol}_{duration}_{bar_size}_{what_to_show}"
        
        if not force_refresh:
            cached_data, is_fresh = self.freshness_manager.get_data(cache_key, max_age_override=300)  # 5 דקות
            if cached_data is not None and is_fresh:
                return cached_data
        
        try:
            # Call the parent method with compatible parameters
            historical_data = super().get_historical_data(
                symbol=symbol, 
                duration=duration, 
                bar_size=bar_size,
                what_to_show=what_to_show
            )
            if historical_data is not None:
                self.freshness_manager.update_data(
                    cache_key, 
                    historical_data, 
                    source="IBKR_Historical_API"
                )
                return historical_data
        except Exception as e:
            # השגיאה כבר מודחקת ב-broker_interface
            # logger.error(f"❌ Error getting historical data for {symbol}: {e}")
            
            cached_data, _ = self.freshness_manager.get_data(cache_key)
            return cached_data
        
        return None
    
    def get_freshness_status(self) -> Dict:
        """מצב רעננות הנתונים"""
        cache_info = self.freshness_manager.get_cache_info()
        stale_keys = self.freshness_manager.get_stale_keys()
        
        return {
            'cache_info': cache_info,
            'stale_data_count': len(stale_keys),
            'stale_keys': stale_keys,
            'connection_health': {
                'last_successful_request': self.last_successful_request,
                'connection_issues_count': self.connection_issues_count,
                'time_since_last_success': (datetime.now() - self.last_successful_request).total_seconds()
            },
            'fresh_data_stats': self.fresh_data_stats.copy()
        }
    
    def force_refresh_all(self):
        """כפיית רענון כל הנתונים"""
        logger.info("🔄 Forcing refresh of all cached data")
        
        # רענון נתונים קריטיים
        try:
            self.get_account_summary(force_refresh=True)
            self.get_positions(force_refresh=True)
            
            self.fresh_data_stats['auto_refreshes_triggered'] += 1
            logger.info("✅ All data refreshed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error during force refresh: {e}")
    
    def cleanup_and_refresh(self):
        """ניקוי נתונים מיושנים ורענון"""
        logger.info("🧹 Cleaning up stale data and refreshing")
        
        # ניקוי הנתונים המיושנים
        self.freshness_manager.cleanup_stale_data()
        
        # רענון נתונים חשובים
        self.force_refresh_all()
    
    def disconnect(self):
        """ניתוק עם ניקוי"""
        logger.info("🔌 Disconnecting Fresh Data Broker")
        
        # עצירת ניטור רעננות
        self.freshness_manager.stop_monitoring()
        
        # ניתוק מהברוקר הבסיסי
        super().disconnect()
    
    def get_stale_historical_keys(self, long_stale_seconds: int = 150) -> list[str]:
        """קבלת רשימת מפתחות נתונים היסטוריים מיושנים"""
        return self.freshness_manager.get_stale_historical_keys(long_stale_seconds)
    
    def _handle_stale_data_reconnect(self, stale_keys: list):
        """טיפול בהתחברות מחדש בגלל נתונים מיושנים"""
        logger.warning(f"🔄 Handling stale data reconnect for {len(stale_keys)} keys")
        
        try:
            # ניסיון התחברות מחדש למערכת Market Data
            if self.is_connected():
                logger.info("🔌 Refreshing market data connections...")
                
                # רענון חיבורי Market Data
                self._refresh_market_data_subscriptions()
                
                # כפיית רענון הנתונים המיושנים
                for key in stale_keys:
                    self.freshness_manager.force_refresh(key)
                
                self.fresh_data_stats['connection_recoveries'] += 1
                logger.info("✅ Market data connections refreshed")
            else:
                logger.warning("❌ Cannot refresh - broker not connected")
                
        except Exception as e:
            logger.error(f"❌ Error handling stale data reconnect: {e}")
    
    def _check_connection_health(self):
        """בדיקת תקינות החיבור"""
        try:
            if not self.is_connected():
                logger.warning("⚠️ Broker connection lost")
                self.connection_issues_count += 1
                return False
            
            # בדיקה אם יש תגובה מהברוקר
            test_summary = super().get_account_summary()
            if test_summary:
                self.last_successful_request = datetime.now()
                logger.debug("✅ Broker connection healthy")
                return True
            else:
                logger.warning("⚠️ Broker not responding to requests")
                self.connection_issues_count += 1
                return False
                
        except Exception as e:
            logger.error(f"❌ Error checking connection health: {e}")
            self.connection_issues_count += 1
            return False
    
    # ----------------------------------------------------
    # 🛡️ Error 201 Prevention - Order Management
    # ----------------------------------------------------
    
    def has_working_orders(self, symbol: str) -> bool:
        """
        Check if there are working orders for a specific symbol.
        Uses parent IBBroker method with Fresh Data tracking.
        
        Args:
            symbol: Stock symbol to check
            
        Returns:
            True if there are working orders for the symbol
        """
        try:
            result = super().has_working_orders(symbol)
            logger.debug(f"🔍 Working orders check for {symbol}: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ Error checking working orders for {symbol}: {e}")
            return False
    
    def cancel_open_orders_for_symbol(self, symbol: str) -> int:
        """
        Cancel all open orders for a specific symbol.
        Uses parent IBBroker method with Fresh Data tracking.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Number of orders cancelled
        """
        try:
            cancelled_count = super().cancel_open_orders_for_symbol(symbol)
            if cancelled_count > 0:
                self.fresh_data_stats['auto_refreshes_triggered'] += 1
                logger.warning(f"🧹 FreshDataBroker: Cancelled {cancelled_count} orders for {symbol}")
            return cancelled_count
        except Exception as e:
            logger.error(f"❌ Error cancelling orders for {symbol}: {e}")
            return 0
    
    def cancel_all_open_orders(self) -> int:
        """
        Emergency cancellation of ALL open orders.
        Uses parent IBBroker method with Fresh Data tracking.
        
        Returns:
            Number of orders cancelled
        """
        try:
            cancelled_count = super().cancel_all_open_orders()
            if cancelled_count > 0:
                self.fresh_data_stats['auto_refreshes_triggered'] += 1
                logger.warning(f"🚨 FreshDataBroker: Emergency cancelled ALL {cancelled_count} orders")
            return cancelled_count
        except Exception as e:
            logger.error(f"❌ Error in emergency cancel all orders: {e}")
            return 0
        
        logger.info("✅ Fresh Data Broker disconnected")