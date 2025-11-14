"""
Data Freshness Manager for IBKR API
====================================
מנהל רעננות נתונים לפתרון בעיית ה-Stale Data ב-IBKR API

פתרון מקצועי לבעיות נפוצות:
1. נתונים מיושנים (Stale Data)
2. חיבורים מושהים 
3. עדכונים לא סינכרוניים
4. Cache validation
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class DataPoint:
    """נקודת נתונים עם metadata על רעננות"""
    value: Any
    timestamp: datetime
    source: str
    is_stale: bool = False
    update_count: int = 0

class DataFreshnessManager:
    """
    [REFRESH] מנהל רעננות נתונים - פתרון מקצועי לבעיית Stale Data
    
    Features:
    - Real-time staleness detection
    - Auto-refresh mechanisms
    - Multi-source data validation
    - Connection health monitoring
    """
    
    def __init__(self, 
                 max_age_seconds: int = 30,
                 stale_threshold_seconds: int = 60,
                 auto_refresh: bool = True):
        """
        Args:
            max_age_seconds: זמן מקסימלי לנתונים בשניות
            stale_threshold_seconds: סף זמן להגדרת נתונים כמיושנים
            auto_refresh: האם לרענן אוטומטית נתונים מיושנים
        """
        self.max_age = timedelta(seconds=max_age_seconds)
        self.stale_threshold = timedelta(seconds=stale_threshold_seconds)
        self.auto_refresh = auto_refresh
        
        # Data storage
        self.data_cache: Dict[str, DataPoint] = {}
        self.last_update_times: Dict[str, datetime] = {}
        self.connection_health: Dict[str, bool] = {}
        
        # Threading
        self.lock = threading.RLock()
        self.refresh_thread = None
        self.running = False
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'stale_data_detected': 0,
            'auto_refreshes': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        logger.info("[REFRESH] Data Freshness Manager initialized")
        
    def start_monitoring(self):
        """התחלת ניטור רעננות נתונים"""
        if not self.running:
            self.running = True
            self.refresh_thread = threading.Thread(
                target=self._refresh_loop, 
                daemon=True,
                name="DataFreshnessMonitor"
            )
            self.refresh_thread.start()
            logger.info("[REFRESH] Data freshness monitoring started")
    
    def stop_monitoring(self):
        """עצירת ניטור רעננות נתונים"""
        self.running = False
        if self.refresh_thread:
            self.refresh_thread.join(timeout=5)
        logger.info("[REFRESH] Data freshness monitoring stopped")
    
    def update_data(self, key: str, value: Any, source: str = "unknown") -> bool:
        """
        עדכון נתונים עם בדיקת רעננות
        
        Args:
            key: מפתח הנתונים
            value: הערך החדש
            source: מקור הנתונים
            
        Returns:
            True אם הנתונים עודכנו בהצלחה
        """
        with self.lock:
            now = datetime.now()
            
            # בדיקה אם הנתונים באמת חדשים
            if key in self.data_cache:
                old_data = self.data_cache[key]
                
                # אם הערך זהה והזמן קרוב, ייתכן שזה Stale Data
                if (old_data.value == value and 
                    now - old_data.timestamp < timedelta(seconds=5)):
                    logger.warning(f"🚨 Potential stale data detected for {key}")
                    self.stats['stale_data_detected'] += 1
                    return False
            
            # עדכון הנתונים
            self.data_cache[key] = DataPoint(
                value=value,
                timestamp=now,
                source=source,
                is_stale=False,
                update_count=self.data_cache.get(key, DataPoint(None, now, source)).update_count + 1
            )
            
            self.last_update_times[key] = now
            self.stats['total_requests'] += 1
            
            logger.debug(f"[OK] Data updated for {key}: {value} from {source}")
            return True
    
    def get_data(self, key: str, max_age_override: Optional[int] = None) -> Tuple[Any, bool]:
        """
        קבלת נתונים עם בדיקת רעננות
        
        Args:
            key: מפתח הנתונים
            max_age_override: גיל מקסימלי חלופי בשניות
            
        Returns:
            (value, is_fresh) - הערך והאם הוא רענן
        """
        with self.lock:
            if key not in self.data_cache:
                self.stats['cache_misses'] += 1
                return None, False
            
            data_point = self.data_cache[key]
            now = datetime.now()
            
            # קביעת גיל מקסימלי
            max_age = (timedelta(seconds=max_age_override) if max_age_override 
                      else self.max_age)
            
            # בדיקת רעננות
            age = now - data_point.timestamp
            is_fresh = age <= max_age
            
            # עדכון flag של stale data
            if age > self.stale_threshold:
                data_point.is_stale = True
                logger.warning(f"🚨 Stale data detected for {key}: age={age.total_seconds():.1f}s")
            
            self.stats['cache_hits'] += 1
            return data_point.value, is_fresh
    
    def is_data_fresh(self, key: str, max_age_seconds: Optional[int] = None) -> bool:
        """בדיקה האם נתונים רעננים"""
        _, is_fresh = self.get_data(key, max_age_seconds)
        return is_fresh
    
    def mark_stale(self, key: str, reason: str = "manual"):
        """סימון נתונים כמיושנים"""
        with self.lock:
            if key in self.data_cache:
                self.data_cache[key].is_stale = True
                logger.info(f"🚨 Data marked as stale for {key}: {reason}")
    
    def force_refresh(self, key: str) -> bool:
        """כפית רענון נתונים"""
        with self.lock:
            if key in self.data_cache:
                # מחיקת הנתונים הישנים כדי לכפות רענון
                del self.data_cache[key]
                self.stats['auto_refreshes'] += 1
                logger.info(f"[REFRESH] Forced refresh for {key}")
                return True
            return False
    
    def get_stale_keys(self) -> list:
        """קבלת רשימת מפתחות עם נתונים מיושנים"""
        with self.lock:
            stale_keys = []
            now = datetime.now()
            
            for key, data_point in self.data_cache.items():
                age = now - data_point.timestamp
                if age > self.stale_threshold or data_point.is_stale:
                    stale_keys.append(key)
            
            return stale_keys
    
    def get_stale_historical_keys(self, long_stale_seconds: int = 150) -> list[str]:
        """קבלת רשימת מפתחות נתונים היסטוריים מיושנים מאוד"""
        with self.lock:
            stale_historical_keys = []
            now = datetime.now()
            long_stale_threshold = timedelta(seconds=long_stale_seconds)
            
            for key, data_point in self.data_cache.items():
                # בדיקה אם המפתח מתחיל ב-historical_
                if key.startswith('historical_'):
                    age = now - data_point.timestamp
                    if age > long_stale_threshold:
                        stale_historical_keys.append(key)
                        logger.debug(f"🚨 Historical data is very stale for {key}: age={age.total_seconds():.1f}s")
            
            return stale_historical_keys
    
    def cleanup_stale_data(self):
        """ניקוי נתונים מיושנים מהמטמון"""
        with self.lock:
            stale_keys = self.get_stale_keys()
            for key in stale_keys:
                if key in self.data_cache:
                    del self.data_cache[key]
                    logger.debug(f"🗑️ Cleaned up stale data for {key}")
            
            if stale_keys:
                logger.info(f"🧹 Cleaned up {len(stale_keys)} stale data entries")
    
    def get_cache_info(self) -> Dict:
        """מידע על מצב המטמון"""
        with self.lock:
            now = datetime.now()
            fresh_count = 0
            stale_count = 0
            
            for data_point in self.data_cache.values():
                age = now - data_point.timestamp
                if age <= self.max_age:
                    fresh_count += 1
                else:
                    stale_count += 1
            
            return {
                'total_entries': len(self.data_cache),
                'fresh_entries': fresh_count,
                'stale_entries': stale_count,
                'cache_hit_rate': (self.stats['cache_hits'] / 
                                 max(1, self.stats['cache_hits'] + self.stats['cache_misses']) * 100),
                'stats': self.stats.copy()
            }
    
    def _refresh_loop(self):
        """לולאת רענון נתונים (רצה ב-thread נפרד)"""
        last_broker_check = time.time()
        broker_check_interval = 60  # בדיקת ברוקר כל דקה
        
        while self.running:
            try:
                current_time = time.time()
                
                if self.auto_refresh:
                    self.cleanup_stale_data()
                
                # בדיקה מיוחדת: אם יש נתונים מיושנים מעבר ל-35 שניות
                stale_keys = self.get_stale_keys()
                if stale_keys:
                    very_stale_keys = []
                    now = datetime.now()
                    
                    with self.lock:
                        for key in stale_keys:
                            if key in self.data_cache:
                                age = now - self.data_cache[key].timestamp
                                if age.total_seconds() > 35:  # נתונים מיושנים מאוד
                                    very_stale_keys.append(key)
                    
                    if very_stale_keys:
                        logger.warning(f"🚨 Very stale data detected for {len(very_stale_keys)} keys")
                        self._trigger_broker_reconnect(very_stale_keys)
                
                # בדיקת חיבור ברוקר תקופתית
                if current_time - last_broker_check > broker_check_interval:
                    self._check_broker_connection()
                    last_broker_check = current_time
                
                # הקפה כל 30 שניות
                for _ in range(30):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"[ERROR] Error in refresh loop: {e}")
                time.sleep(5)
    
    def _trigger_broker_reconnect(self, stale_keys: list):
        """הפעלת התחברות מחדש לברוקר בגלל נתונים מיושנים"""
        logger.warning(f"[REFRESH] Triggering broker reconnect due to {len(stale_keys)} very stale keys")
        
        # הוספת callback לברוקר אם קיים
        if hasattr(self, '_broker_callback') and self._broker_callback:
            try:
                self._broker_callback(stale_keys)
            except Exception as e:
                logger.error(f"[ERROR] Error calling broker callback: {e}")
    
    def _check_broker_connection(self):
        """בדיקה תקופתית של חיבור הברוקר"""
        if hasattr(self, '_connection_check_callback') and self._connection_check_callback:
            try:
                self._connection_check_callback()
            except Exception as e:
                logger.error(f"[ERROR] Error checking broker connection: {e}")
    
    def set_broker_callback(self, callback):
        """הגדרת callback לטיפול בבעיות ברוקר"""
        self._broker_callback = callback
        logger.info("[OK] Broker callback registered")
    
    def set_connection_check_callback(self, callback):
        """הגדרת callback לבדיקת חיבור"""
        self._connection_check_callback = callback
        logger.info("[OK] Connection check callback registered")

# יצירת instance גלובלי
data_freshness_manager = DataFreshnessManager(
    max_age_seconds=30,
    stale_threshold_seconds=60,
    auto_refresh=True
)