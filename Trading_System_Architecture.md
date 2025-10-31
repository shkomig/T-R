# ארכיטקטורת מערכת מסחר אוטומטית - פורט 7497

## סקירה כללית
מערכת מסחר אוטומטית מתקדמת המותאמת לסוחרי מניות בפורט 7497, עם התמקדות בנרות 30 דקות ורמת סיכון נמוכה.

## 1. ארכיטקטורה כללית

```
┌─────────────────────────────────────────────────────────────┐
│                    מערכת מסחר אוטומטית                        │
├─────────────────────────────────────────────────────────────┤
│  Data Layer          │  Processing Layer  │  Execution Layer │
│  ┌─────────────────┐ │  ┌───────────────┐ │  ┌─────────────┐ │
│  │ Interactive     │ │  │ AI Engine     │ │  │ Order       │ │
│  │ Brokers API     │ │  │ (Strategy     │ │  │ Management  │ │
│  │ (Port 7497)     │ │  │ Engine)       │ │  │ System      │ │
│  └─────────────────┘ │  └───────────────┘ │  └─────────────┘ │
│  ┌─────────────────┐ │  ┌───────────────┐ │  ┌─────────────┐ │
│  │ Market Data     │ │  │ Risk          │ │  │ Position    │ │
│  │ Feed            │ │  │ Management    │ │  │ Tracking    │ │
│  └─────────────────┘ │  └───────────────┘ │  └─────────────┘ │
│  ┌─────────────────┐ │  ┌───────────────┐ │  ┌─────────────┐ │
│  │ BI System       │ │  │ Backtesting   │ │  │ Monitoring  │ │
│  │ Integration     │ │  │ Engine        │ │  │ & Alerts    │ │
│  └─────────────────┘ │  └───────────────┘ │  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 2. רכיבי המערכת

### 2.1 Data Layer (שכבת הנתונים)
- **Interactive Brokers API** - חיבור ישיר לפורט 7497
- **Market Data Feed** - נתוני שוק בזמן אמת
- **BI System Integration** - אינטגרציה עם מערכת ה-BI הקיימת
- **Historical Data Storage** - אחסון נתונים היסטוריים

### 2.2 Processing Layer (שכבת העיבוד)
- **AI Strategy Engine** - מנוע אסטרטגיות מבוסס AI
- **Risk Management Module** - מודול ניהול סיכונים
- **Backtesting Engine** - מנוע בדיקות חזרה
- **Signal Generation** - יצירת סיגנלים

### 2.3 Execution Layer (שכבת הביצוע)
- **Order Management System** - מערכת ניהול הזמנות
- **Position Tracking** - מעקב פוזיציות
- **Monitoring & Alerts** - ניטור והתראות

## 3. אסטרטגיות מסחר (רמת סיכון נמוכה)

### 3.1 EMA Cross Strategy (30 דקות)
```python
# אסטרטגיה בסיסית - ממוצעים נעים
EMA_FAST = 12
EMA_SLOW = 26
SIGNAL_LINE = 9

# כללי כניסה:
# - EMA_FAST חוצה מעל EMA_SLOW = כניסה לונג
# - EMA_FAST חוצה מתחת EMA_SLOW = כניסה לשורט
```

### 3.2 VWAP Strategy (30 דקות)
```python
# אסטרטגיה מבוססת VWAP
VWAP_DEVIATION = 0.5%  # סטייה מ-VWAP

# כללי כניסה:
# - מחיר מעל VWAP + סטייה = כניסה לונג
# - מחיר מתחת VWAP - סטייה = כניסה לשורט
```

### 3.3 Volume Breakout Strategy (30 דקות)
```python
# אסטרטגיה מבוססת נפח
VOLUME_THRESHOLD = 1.5  # כפילות מהממוצע
BREAKOUT_CONFIRMATION = 3  # נרות לאישור

# כללי כניסה:
# - נפח חריג + פריצת התנגדות = כניסה
```

## 4. ניהול סיכונים

### 4.1 כללי סיכון בסיסיים
- **גודל פוזיציה מקסימלי**: 2% מהון החשבון
- **סטופ לוס**: 1% מהפוזיציה
- **טייק פרופיט**: 2:1 (רווח:הפסד)
- **מקסימום פוזיציות פתוחות**: 5

### 4.2 כללי סיכון מתקדמים
- **Drawdown מקסימלי**: 5%
- **הפסקת מסחר**: לאחר 3 הפסדים רצופים
- **ניתוח קורלציה**: מניעת פוזיציות קורלטיביות

## 5. אינדיקטורים מותאמים

### 5.1 אינדיקטורים טכניים
- **EMA (12, 26, 50)** - ממוצעים נעים
- **VWAP** - נפח ממוצע משוקלל
- **RSI (14)** - אינדיקטור מומנטום
- **Bollinger Bands (20, 2)** - פסי בולינגר
- **Volume Profile** - פרופיל נפח

### 5.2 אינדיקטורים מותאמים אישית
- **Smart Volume** - נפח חכם עם התראות
- **Risk Meter** - מד סיכון בזמן אמת
- **Market Sentiment** - סנטימנט שוק
- **Volatility Index** - מדד תנודתיות

## 6. מבנה קבצים מוצע

```
Trading_System/
├── config/
│   ├── trading_config.yaml
│   ├── risk_management.yaml
│   └── api_credentials.yaml
├── data/
│   ├── market_data/
│   ├── historical_data/
│   └── backtest_results/
├── strategies/
│   ├── ema_cross_strategy.py
│   ├── vwap_strategy.py
│   └── volume_breakout_strategy.py
├── indicators/
│   ├── custom_indicators.py
│   ├── volume_analysis.py
│   └── risk_indicators.py
├── risk_management/
│   ├── position_sizing.py
│   ├── stop_loss.py
│   └── portfolio_risk.py
├── execution/
│   ├── order_manager.py
│   ├── position_tracker.py
│   └── broker_interface.py
├── backtesting/
│   ├── backtest_engine.py
│   ├── performance_analyzer.py
│   └── report_generator.py
├── monitoring/
│   ├── alert_system.py
│   ├── dashboard.py
│   └── logger.py
└── utils/
    ├── data_processor.py
    ├── math_utils.py
    └── file_utils.py
```

## 7. זרימת עבודה (Workflow)

### 7.1 זרימת מסחר יומית
1. **התחלת יום** - בדיקת פוזיציות פתוחות
2. **ניתוח שוק** - סריקת סיגנלים
3. **יצירת הזמנות** - לפי אסטרטגיות
4. **ניהול פוזיציות** - מעקב והתאמות
5. **סיום יום** - דוח ביצועים

### 7.2 זרימת פיתוח
1. **פיתוח אסטרטגיה** - כתיבת קוד
2. **בדיקות חזרה** - Backtesting
3. **אופטימיזציה** - שיפור פרמטרים
4. **בדיקות נייר** - Paper Trading
5. **הפעלה חיה** - Live Trading

## 8. טכנולוגיות מומלצות

### 8.1 שפות תכנות
- **Python** - שפת פיתוח ראשית
- **Pine Script** - אינדיקטורים ב-TradingView
- **SQL** - ניהול בסיס נתונים

### 8.2 ספריות Python
- **pandas** - עיבוד נתונים
- **numpy** - חישובים מתמטיים
- **ta-lib** - אינדיקטורים טכניים
- **ib_insync** - חיבור ל-Interactive Brokers
- **plotly** - ויזואליזציה
- **fastapi** - API

### 8.3 כלים נוספים
- **TradingView** - פיתוח אינדיקטורים
- **Jupyter Notebook** - ניתוח ופיתוח
- **Docker** - קונטיינריזציה
- **Git** - ניהול קוד

## 9. מדדי ביצוע

### 9.1 מדדי רווחיות
- **Total Return** - תשואה כוללת
- **Sharpe Ratio** - יחס שארפ
- **Sortino Ratio** - יחס סורטינו
- **Calmar Ratio** - יחס קלמר

### 9.2 מדדי סיכון
- **Maximum Drawdown** - מקסימום נסיגה
- **VaR (Value at Risk)** - ערך בסיכון
- **Beta** - בטא
- **Volatility** - תנודתיות

## 10. שלבי יישום

### שלב 1: הכנה (שבוע 1)
- הגדרת סביבת פיתוח
- חיבור ל-Interactive Brokers
- הגדרת מערכת ניהול סיכונים

### שלב 2: פיתוח (שבוע 2-3)
- פיתוח אינדיקטורים בסיסיים
- יצירת אסטרטגיות מסחר
- בניית מערכת Backtesting

### שלב 3: בדיקות (שבוע 4)
- Backtesting מקיף
- אופטימיזציה של פרמטרים
- בדיקות נייר

### שלב 4: הפעלה (שבוע 5+)
- הפעלה חיה עם הון קטן
- ניטור וביקורת
- שיפור מתמיד

---

**הערה**: ארכיטקטורה זו נועדה להיות בסיס לפיתוח מערכת מסחר אוטומטית מתקדמת. כל רכיב יכול להיות מותאם ומותאם אישית לפי הצרכים הספציפיים.


