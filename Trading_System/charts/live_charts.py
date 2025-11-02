# -*- coding: utf-8 -*-
"""
Live Charts Module for Trading System
מודול גרפים חיים למערכת המסחר

Features:
- Real-time charts from IB Gateway
- Multiple symbols display
- Candlestick-style charts
- Volume indicators
- Non-blocking operation
"""

import time
import threading
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np

class LiveChartWindow:
    """חלון גרפים חיים שלא מפריע למערכת הראשית"""
    
    def __init__(self, broker, symbols=['AAPL', 'TSLA', 'MSFT', 'NVDA']):
        self.broker = broker
        self.symbols = symbols
        self.running = False
        self.chart_thread = None
        self.fig = None
        self.axes = None
        
        print(f"📊 Initializing charts for: {', '.join(symbols)}")
        
    def setup_charts(self):
        """הגדרת חלון הגרפים"""
        try:
            # סגנון כהה מקצועי
            plt.style.use('dark_background')
            
            # יצירת החלון
            self.fig, self.axes = plt.subplots(2, 2, figsize=(16, 10))
            self.fig.suptitle('📊 Live Trading Charts - Interactive Brokers Gateway', 
                             fontsize=16, color='cyan', weight='bold')
            
            # הגדרת כל subplot
            for i, symbol in enumerate(self.symbols):
                if i < 4:  # רק 4 גרפים
                    row, col = i // 2, i % 2
                    ax = self.axes[row, col]
                    ax.set_title(f'{symbol} - Loading...', fontsize=12, color='yellow')
                    ax.grid(True, alpha=0.2, color='gray')
                    ax.set_facecolor('#0a0a0a')
                    ax.tick_params(colors='white')
            
            plt.tight_layout()
            return True
            
        except Exception as e:
            print(f"❌ Error setting up charts: {e}")
            return False
    
    def get_chart_data(self, symbol):
        """קבלת נתונים לגרף מ-IB"""
        try:
            # נתונים היסטוריים לגרף
            bars = self.broker.get_historical_data(
                symbol=symbol,
                duration="1 D",      # יום אחד
                bar_size="5 mins"    # כל 5 דקות
            )
            
            if bars and len(bars) > 10:  # לפחות 10 נקודות נתונים
                return bars
            else:
                # נתונים חלופיים אם אין מספיק
                return self.generate_demo_data(symbol)
                
        except Exception as e:
            print(f"⚠️  Error getting data for {symbol}: {e}")
            return self.generate_demo_data(symbol)
    
    def generate_demo_data(self, symbol):
        """יצירת נתונים דמו אם אין חיבור טוב"""
        class DemoBar:
            def __init__(self, date, open_p, high, low, close, volume):
                self.date = date
                self.open = open_p
                self.high = high
                self.low = low
                self.close = close
                self.volume = volume
        
        # מחיר בסיס לכל סמל
        base_prices = {'AAPL': 150, 'TSLA': 250, 'MSFT': 300, 'NVDA': 400}
        base_price = base_prices.get(symbol, 100)
        
        bars = []
        now = datetime.now()
        
        for i in range(50):  # 50 נקודות נתונים
            time_point = now - timedelta(minutes=5*i)
            
            # סימולציה של תנועת מחיר
            volatility = 0.02
            price_change = np.random.normal(0, volatility)
            
            open_price = base_price * (1 + price_change)
            close_price = open_price * (1 + np.random.normal(0, volatility/2))
            high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, volatility/3)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, volatility/3)))
            volume = int(np.random.normal(100000, 30000))
            
            bars.append(DemoBar(time_point, open_price, high_price, low_price, close_price, volume))
            base_price = close_price
        
        return list(reversed(bars))
    
    def update_single_chart(self, symbol, ax, position):
        """עדכון גרף בודד"""
        try:
            # קבלת נתונים
            bars = self.get_chart_data(symbol)
            
            if not bars:
                return
            
            # הכנת הנתונים
            times = [bar.date for bar in bars[-30:]]  # 30 הנקודות האחרונות
            opens = [bar.open for bar in bars[-30:]]
            highs = [bar.high for bar in bars[-30:]]
            lows = [bar.low for bar in bars[-30:]]
            closes = [bar.close for bar in bars[-30:]]
            volumes = [bar.volume for bar in bars[-30:]]
            
            # ניקוי הגרף
            ax.clear()
            
            # גרף נרות מפושט (Candlestick-style)
            for j in range(len(bars[-30:])):
                if j < len(times):
                    color = '#00ff88' if closes[j] >= opens[j] else '#ff3366'
                    alpha = 0.8
                    
                    # קו גבוה-נמוך
                    ax.plot([times[j], times[j]], [lows[j], highs[j]], 
                           color=color, linewidth=1, alpha=alpha)
                    
                    # גוף הנר
                    ax.plot([times[j], times[j]], [opens[j], closes[j]], 
                           color=color, linewidth=4, alpha=alpha)
            
            # קו מחיר נוכחי
            current_price = closes[-1] if closes else 0
            change_pct = ((current_price - opens[0]) / opens[0] * 100) if opens else 0
            
            ax.axhline(y=current_price, color='yellow', 
                      linestyle='--', alpha=0.9, linewidth=1.5)
            
            # כותרת עם מחיר נוכחי
            color_title = '#00ff88' if change_pct >= 0 else '#ff3366'
            ax.set_title(f'{symbol} - ${current_price:.2f} ({change_pct:+.1f}%)', 
                        fontsize=11, color=color_title, weight='bold')
            
            # עיצוב
            ax.set_ylabel('מחיר ($)', color='lightgray', fontsize=9)
            ax.grid(True, alpha=0.15, color='gray')
            ax.set_facecolor('#0a0a0a')
            ax.tick_params(colors='lightgray', labelsize=8)
            
            # גרף נפח בצד ימין
            ax2 = ax.twinx()
            ax2.bar(times, volumes, alpha=0.2, color='cyan', width=0.001)
            ax2.set_ylabel('נפח', color='lightblue', fontsize=8)
            ax2.tick_params(axis='y', labelcolor='lightblue', labelsize=7)
            
            # עיצוב ציר זמן
            if len(times) > 0:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, fontsize=7)
            
        except Exception as e:
            print(f"⚠️  Error updating chart for {symbol}: {e}")
            ax.text(0.5, 0.5, f'{symbol}\nChart Error', 
                   transform=ax.transAxes, ha='center', va='center',
                   color='red', fontsize=12)
    
    def update_all_charts(self):
        """עדכון כל הגרפים"""
        if not self.fig or self.axes is None:
            return
            
        try:
            for i, symbol in enumerate(self.symbols[:4]):  # רק 4 גרפים
                row, col = i // 2, i % 2
                ax = self.axes[row, col]
                self.update_single_chart(symbol, ax, i)
            
            # עדכון התצוגה
            self.fig.suptitle(f'📊 Live Charts - {datetime.now().strftime("%H:%M:%S")}', 
                             fontsize=16, color='cyan', weight='bold')
            plt.tight_layout()
            plt.pause(0.1)  # רענון קצר
            
        except Exception as e:
            print(f"⚠️  Error updating charts: {e}")
    
    def chart_main_loop(self):
        """הלולאה הראשית של הגרפים"""
        print("📊 Starting chart main loop...")
        
        try:
            # הגדרת הגרפים
            if not self.setup_charts():
                print("❌ Failed to setup charts")
                return
            
            plt.ion()  # מצב אינטראקטיבי
            plt.show(block=False)
            
            update_counter = 0
            
            while self.running:
                try:
                    self.update_all_charts()
                    update_counter += 1
                    
                    if update_counter % 6 == 0:  # הודעה כל דקה
                        print(f"📊 Charts updated #{update_counter} at {datetime.now().strftime('%H:%M:%S')}")
                    
                    # המתנה 10 שניות
                    for _ in range(100):  # 10 שניות בצעדים של 0.1
                        if not self.running:
                            break
                        time.sleep(0.1)
                    
                except KeyboardInterrupt:
                    print("📊 Chart update interrupted by user")
                    break
                except Exception as e:
                    print(f"⚠️  Chart loop error: {e}")
                    time.sleep(5)  # המתנה לפני ניסיון חוזר
                    
        except Exception as e:
            print(f"❌ Fatal chart error: {e}")
        finally:
            print("📊 Chart loop ended")
            plt.close('all')
    
    def start(self):
        """התחלת הגרפים החיים"""
        if self.running:
            print("📊 Charts already running")
            return
            
        print("🚀 Starting live charts...")
        self.running = True
        
        # הפעלה בthread נפרד
        self.chart_thread = threading.Thread(target=self.chart_main_loop, daemon=True)
        self.chart_thread.start()
        
        print("✅ Live charts started successfully!")
        print("💡 Charts will update every 10 seconds")
        print("💡 Close the chart window to stop charts")
        
        return self.chart_thread
    
    def stop(self):
        """עצירת הגרפים"""
        print("📊 Stopping charts...")
        self.running = False
        
        if self.chart_thread and self.chart_thread.is_alive():
            self.chart_thread.join(timeout=5)
        
        plt.close('all')
        print("✅ Charts stopped")


# פונקציה נוחה להפעלה
def start_live_charts(broker, symbols=['AAPL', 'TSLA', 'MSFT', 'NVDA']):
    """הפעלת גרפים חיים - פונקציה נוחה"""
    chart_window = LiveChartWindow(broker, symbols)
    return chart_window.start()


if __name__ == "__main__":
    print("📊 Live Charts Module")
    print("💡 This module provides live charts for the trading system")
    print("💡 Import and use: from charts.live_charts import LiveChartWindow")