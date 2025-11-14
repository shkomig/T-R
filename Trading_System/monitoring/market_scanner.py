# -*- coding: utf-8 -*-
"""
Real-Time Market Scanner
סורק שוק בזמן אמת

Features:
- Volume breakouts detection
- Price movement alerts
- Gap up/down scanner
- High/Low momentum scanner
- Earnings announcement scanner
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import pandas as pd

class ScanType(Enum):
    """סוגי סריקות שוק"""
    VOLUME_BREAKOUT = "volume_breakout"
    PRICE_BREAKOUT = "price_breakout"
    GAP_UP = "gap_up"
    GAP_DOWN = "gap_down"
    HIGH_MOMENTUM = "high_momentum"
    EARNINGS_MOVERS = "earnings_movers"
    UNUSUAL_VOLUME = "unusual_volume"
    TECHNICAL_BREAKOUT = "technical_breakout"

@dataclass
class ScanResult:
    """תוצאת סריקה"""
    symbol: str
    scan_type: ScanType
    current_price: float
    change_percent: float
    volume: int
    avg_volume: int
    volume_ratio: float
    timestamp: datetime
    alert_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    details: Dict

class MarketScanner:
    """סורק שוק בזמן אמת"""
    
    def __init__(self, broker):
        self.broker = broker
        self.running = False
        self.scan_thread = None
        
        # רשימת מניות לסריקה (S&P 500 + NASDAQ 100)
        self.watchlist = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK.B',
            'UNH', 'JNJ', 'JPM', 'V', 'PG', 'XOM', 'HD', 'CVX', 'MA', 'PFE',
            'ABBV', 'BAC', 'KO', 'AVGO', 'LLY', 'WMT', 'PEP', 'TMO', 'COST',
            'DIS', 'ABT', 'DHR', 'NEE', 'VZ', 'ADBE', 'BMY', 'CRM', 'NFLX',
            'AMD', 'QCOM', 'T', 'INTC', 'ORCL', 'COP', 'ACN', 'TXN', 'WFC',
            'RTX', 'PM', 'HON', 'UNP', 'IBM', 'SBUX', 'CAT', 'GS', 'AXP',
            'NOW', 'DE', 'BKNG', 'ELV', 'SPGI', 'MDT', 'GILD', 'AMT', 'SYK',
            'AMGN', 'LOW', 'BLK', 'AMAT', 'CVS', 'PLD', 'TJX', 'ADP', 'LMT',
            'MO', 'MMC', 'TMUS', 'ZTS', 'CB', 'MDLZ', 'C', 'SO', 'FIS',
            'SCHW', 'PYPL', 'DUK', 'CI', 'REGN', 'NOC', 'SHW', 'CME', 'USB'
        ]
        
        # הגדרות סריקה
        self.scan_settings = {
            'volume_breakout_ratio': 3.0,      # נפח פי 3 מהממוצע
            'price_breakout_percent': 5.0,     # שינוי מחיר 5%+
            'gap_threshold': 2.0,               # פער 2%+
            'momentum_threshold': 3.0,          # מומנטום 3%+
            'unusual_volume_ratio': 2.5,       # נפח חריג פי 2.5
            'scan_interval': 30,                # סריקה כל 30 שניות
        }
        
        # callbacks למשתמש
        self.alert_callbacks = []
        
        # cache לנתונים
        self.price_cache = {}
        self.volume_cache = {}
        
    def add_alert_callback(self, callback: Callable[[ScanResult], None]):
        """הוספת callback לאלרטים"""
        self.alert_callbacks.append(callback)
    
    def start_scanning(self):
        """התחלת סריקה בזמן אמת"""
        if self.running:
            print("[SCAN] Scanner already running")
            return
        
        print("[LAUNCH] Starting real-time market scanner...")
        print(f"[CHART] Watching {len(self.watchlist)} symbols")
        print(f"[TIME] Scan interval: {self.scan_settings['scan_interval']} seconds")
        
        self.running = True
        self.scan_thread = threading.Thread(target=self._scanning_loop, daemon=True)
        self.scan_thread.start()
        
        print("[OK] Market scanner started successfully!")
    
    def stop_scanning(self):
        """עצירת הסריקה"""
        self.running = False
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(timeout=5)
        print("🛑 Market scanner stopped")
    
    def _scanning_loop(self):
        """הלולאה הראשית של הסריקה"""
        while self.running:
            try:
                scan_start = time.time()
                alerts = []
                
                # סריקת כל הסמלים
                for symbol in self.watchlist:
                    if not self.running:
                        break
                    
                    symbol_alerts = self._scan_symbol(symbol)
                    alerts.extend(symbol_alerts)
                
                # שליחת אלרטים
                for alert in alerts:
                    self._send_alert(alert)
                
                # הדפסת סטטיסטיקות
                scan_time = time.time() - scan_start
                print(f"[SCAN] Scan completed: {len(alerts)} alerts found in {scan_time:.1f}s")
                
                # המתנה לסריקה הבאה
                time.sleep(self.scan_settings['scan_interval'])
                
            except Exception as e:
                print(f"[ERROR] Scanner error: {e}")
                time.sleep(10)  # המתנה ארוכה יותר אם יש שגיאה
    
    def _scan_symbol(self, symbol: str) -> List[ScanResult]:
        """סריקת סמל בודד"""
        try:
            alerts = []
            
            # קבלת נתונים נוכחיים
            current_data = self._get_current_data(symbol)
            if not current_data:
                return alerts
            
            # בדיקת volume breakout
            volume_alert = self._check_volume_breakout(symbol, current_data)
            if volume_alert:
                alerts.append(volume_alert)
            
            # בדיקת price breakout
            price_alert = self._check_price_breakout(symbol, current_data)
            if price_alert:
                alerts.append(price_alert)
            
            # בדיקת gaps
            gap_alert = self._check_gaps(symbol, current_data)
            if gap_alert:
                alerts.append(gap_alert)
            
            # בדיקת momentum
            momentum_alert = self._check_momentum(symbol, current_data)
            if momentum_alert:
                alerts.append(momentum_alert)
            
            # עדכון cache
            self._update_cache(symbol, current_data)
            
            return alerts
            
        except Exception as e:
            print(f"[WARN] Error scanning {symbol}: {e}")
            return []
    
    def _get_current_data(self, symbol: str) -> Optional[Dict]:
        """קבלת נתונים נוכחיים לסמל"""
        try:
            # קבלת נתונים מהברוקר
            bars = self.broker.get_historical_data(symbol, "1 D", "1 min")
            if not bars or len(bars) < 2:
                return None
            
            current_bar = bars[-1]
            prev_bar = bars[-2]
            
            # חישוב ממוצע נפח (20 הדקות האחרונות)
            recent_volume = sum(bar.volume for bar in bars[-20:]) / 20
            
            return {
                'current_price': current_bar.close,
                'previous_price': prev_bar.close,
                'volume': current_bar.volume,
                'avg_volume': recent_volume,
                'high': current_bar.high,
                'low': current_bar.low,
                'open': current_bar.open,
                'timestamp': current_bar.date
            }
            
        except Exception as e:
            print(f"Error getting data for {symbol}: {e}")
            return None
    
    def _check_volume_breakout(self, symbol: str, data: Dict) -> Optional[ScanResult]:
        """בדיקת פריצת נפח"""
        try:
            volume_ratio = data['volume'] / max(data['avg_volume'], 1)
            threshold = self.scan_settings['volume_breakout_ratio']
            
            if volume_ratio >= threshold:
                change_pct = ((data['current_price'] - data['previous_price']) / 
                             data['previous_price']) * 100
                
                # רמת התראה
                if volume_ratio >= 10:
                    alert_level = "CRITICAL"
                elif volume_ratio >= 5:
                    alert_level = "HIGH"
                elif volume_ratio >= 3:
                    alert_level = "MEDIUM"
                else:
                    alert_level = "LOW"
                
                return ScanResult(
                    symbol=symbol,
                    scan_type=ScanType.VOLUME_BREAKOUT,
                    current_price=data['current_price'],
                    change_percent=change_pct,
                    volume=data['volume'],
                    avg_volume=int(data['avg_volume']),
                    volume_ratio=volume_ratio,
                    timestamp=datetime.now(),
                    alert_level=alert_level,
                    details={
                        'volume_ratio': volume_ratio,
                        'threshold': threshold,
                        'description': f"Volume {volume_ratio:.1f}x above average"
                    }
                )
            
            return None
            
        except Exception as e:
            print(f"Error checking volume breakout for {symbol}: {e}")
            return None
    
    def _check_price_breakout(self, symbol: str, data: Dict) -> Optional[ScanResult]:
        """בדיקת פריצת מחיר"""
        try:
            change_pct = ((data['current_price'] - data['previous_price']) / 
                         data['previous_price']) * 100
            
            threshold = self.scan_settings['price_breakout_percent']
            
            if abs(change_pct) >= threshold:
                volume_ratio = data['volume'] / max(data['avg_volume'], 1)
                
                # רמת התראה
                if abs(change_pct) >= 15:
                    alert_level = "CRITICAL"
                elif abs(change_pct) >= 10:
                    alert_level = "HIGH"
                elif abs(change_pct) >= 7:
                    alert_level = "MEDIUM"
                else:
                    alert_level = "LOW"
                
                return ScanResult(
                    symbol=symbol,
                    scan_type=ScanType.PRICE_BREAKOUT,
                    current_price=data['current_price'],
                    change_percent=change_pct,
                    volume=data['volume'],
                    avg_volume=int(data['avg_volume']),
                    volume_ratio=volume_ratio,
                    timestamp=datetime.now(),
                    alert_level=alert_level,
                    details={
                        'price_change': change_pct,
                        'threshold': threshold,
                        'direction': 'UP' if change_pct > 0 else 'DOWN',
                        'description': f"Price moved {change_pct:+.1f}%"
                    }
                )
            
            return None
            
        except Exception as e:
            print(f"Error checking price breakout for {symbol}: {e}")
            return None
    
    def _check_gaps(self, symbol: str, data: Dict) -> Optional[ScanResult]:
        """בדיקת פערי מחיר"""
        try:
            # חישוב פער בין פתיחה למחיר הקודם
            gap_pct = ((data['open'] - data['previous_price']) / 
                      data['previous_price']) * 100
            
            threshold = self.scan_settings['gap_threshold']
            
            if abs(gap_pct) >= threshold:
                volume_ratio = data['volume'] / max(data['avg_volume'], 1)
                change_pct = ((data['current_price'] - data['previous_price']) / 
                             data['previous_price']) * 100
                
                scan_type = ScanType.GAP_UP if gap_pct > 0 else ScanType.GAP_DOWN
                alert_level = "HIGH" if abs(gap_pct) >= 5 else "MEDIUM"
                
                return ScanResult(
                    symbol=symbol,
                    scan_type=scan_type,
                    current_price=data['current_price'],
                    change_percent=change_pct,
                    volume=data['volume'],
                    avg_volume=int(data['avg_volume']),
                    volume_ratio=volume_ratio,
                    timestamp=datetime.now(),
                    alert_level=alert_level,
                    details={
                        'gap_percent': gap_pct,
                        'threshold': threshold,
                        'direction': 'UP' if gap_pct > 0 else 'DOWN',
                        'description': f"Gap {gap_pct:+.1f}% from previous close"
                    }
                )
            
            return None
            
        except Exception as e:
            print(f"Error checking gaps for {symbol}: {e}")
            return None
    
    def _check_momentum(self, symbol: str, data: Dict) -> Optional[ScanResult]:
        """בדיקת מומנטום"""
        try:
            # חישוב שינוי מחיר מהדקות האחרונות
            change_pct = ((data['current_price'] - data['previous_price']) / 
                         data['previous_price']) * 100
            
            volume_ratio = data['volume'] / max(data['avg_volume'], 1)
            threshold = self.scan_settings['momentum_threshold']
            
            # מומנטום = שינוי מחיר + נפח חריג
            if (abs(change_pct) >= threshold and volume_ratio >= 1.5):
                
                alert_level = "HIGH" if abs(change_pct) >= 5 else "MEDIUM"
                
                return ScanResult(
                    symbol=symbol,
                    scan_type=ScanType.HIGH_MOMENTUM,
                    current_price=data['current_price'],
                    change_percent=change_pct,
                    volume=data['volume'],
                    avg_volume=int(data['avg_volume']),
                    volume_ratio=volume_ratio,
                    timestamp=datetime.now(),
                    alert_level=alert_level,
                    details={
                        'momentum_score': abs(change_pct) * volume_ratio,
                        'price_change': change_pct,
                        'volume_support': volume_ratio,
                        'description': f"Strong momentum: {change_pct:+.1f}% with {volume_ratio:.1f}x volume"
                    }
                )
            
            return None
            
        except Exception as e:
            print(f"Error checking momentum for {symbol}: {e}")
            return None
    
    def _update_cache(self, symbol: str, data: Dict):
        """עדכון cache הנתונים"""
        self.price_cache[symbol] = data['current_price']
        self.volume_cache[symbol] = data['volume']
    
    def _send_alert(self, alert: ScanResult):
        """שליחת אלרט למשתמש"""
        try:
            # הדפסת אלרט למסך
            self._print_alert(alert)
            
            # קריאה ל-callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    print(f"Error in alert callback: {e}")
                    
        except Exception as e:
            print(f"Error sending alert: {e}")
    
    def _print_alert(self, alert: ScanResult):
        """הדפסת אלרט למסך"""
        emoji_map = {
            "CRITICAL": "[CRIT]",
            "HIGH": "[HIGH]",
            "MEDIUM": "[MED]",
            "LOW": "[LOW]"
        }
        
        type_emoji_map = {
            ScanType.VOLUME_BREAKOUT: "[VOL]",
            ScanType.PRICE_BREAKOUT: "[BREAK]",
            ScanType.GAP_UP: "[GAP-UP]",
            ScanType.GAP_DOWN: "[GAP-DN]",
            ScanType.HIGH_MOMENTUM: "[MOMENTUM]"
        }
        
        emoji = emoji_map.get(alert.alert_level, "📊")
        type_emoji = type_emoji_map.get(alert.scan_type, "📊")
        
        print(f"{emoji} {type_emoji} {alert.symbol} | "
              f"${alert.current_price:.2f} ({alert.change_percent:+.1f}%) | "
              f"Vol: {alert.volume_ratio:.1f}x | "
              f"{alert.details.get('description', alert.scan_type.value)}")
    
    def get_current_alerts(self) -> List[ScanResult]:
        """קבלת אלרטים נוכחיים"""
        # מימוש פשוט - בפועל יכול לשמור אלרטים אקטיביים
        return []


# פונקציות נוחות
def start_basic_scanner(broker):
    """התחלת סורק בסיסי"""
    scanner = MarketScanner(broker)
    
    # הוספת callback פשוט
    def simple_alert_handler(alert: ScanResult):
        if alert.alert_level in ["HIGH", "CRITICAL"]:
            print(f"🚨 IMPORTANT ALERT: {alert.symbol} - {alert.details.get('description', '')}")
    
    scanner.add_alert_callback(simple_alert_handler)
    scanner.start_scanning()
    return scanner


if __name__ == "__main__":
    print("🔍 Real-Time Market Scanner")
    print("💡 Features: Volume/Price breakouts, Gaps, Momentum detection")
    print("💡 Import: from monitoring.market_scanner import MarketScanner")