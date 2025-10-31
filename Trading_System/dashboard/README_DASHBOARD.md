# 🎛️ Trading System Dashboard - מדריך התקנה והפעלה

## סקירה כללית

מערכת ה-Dashboard מספקת שני ממשקים עיקריים:
1. **Web Dashboard** - ממשק אינטרנט מלא עם WebSocket לעדכונים בזמן אמת
2. **Jupyter Notebook Dashboard** - ממשק אינטראקטיבי לניתוח ופיתוח

---

## 📋 דרישות מערכת

### דרישות חומרה מינימליות:
- **CPU**: Intel i5 / AMD Ryzen 5 או טוב יותר
- **RAM**: 8GB (מומלץ 16GB)
- **Storage**: 1GB פנוי
- **רשת**: חיבור יציב לאינטרנט

### דרישות תוכנה:
- **Python**: 3.9 או גבוה יותר
- **IB Gateway**: גרסה עדכנית (מותקנת ומופעלת)
- **Browser**: Chrome/Firefox/Edge עדכני (ל-Web Dashboard)
- **pip**: מנהל החבילות של Python

---

## 🚀 התקנה

### שלב 1: התקנת חבילות Dashboard

```powershell
# נווט לתיקיית Dashboard
cd C:\Vs-Pro\TR\Trading_System\dashboard

# התקן את כל הדרישות
pip install -r requirements.txt
```

### שלב 2: בדיקת התקנה

```powershell
# בדוק שכל החבילות הותקנו
python -c "import fastapi, uvicorn, plotly, pandas; print('✅ All packages installed')"
```

---

## 🌐 Web Dashboard - הפעלה

### אופן 1: הפעלה ישירה

```powershell
# נווט לתיקיית Dashboard
cd C:\Vs-Pro\TR\Trading_System\dashboard

# הפעל את השרת
python web_dashboard.py
```

**תראה פלט כזה:**
```
============================================================
🚀 Starting Trading System Dashboard
============================================================

📊 Dashboard URL: http://localhost:8000
📡 WebSocket URL: ws://localhost:8000/ws

⚠️  Make sure IB Gateway is running on port 7497

Press Ctrl+C to stop

============================================================
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### אופן 2: הפעלה עם פרמטרים מותאמים אישית

```powershell
# הפעלה על פורט אחר
uvicorn dashboard.web_dashboard:app --host 0.0.0.0 --port 8080 --reload

# הפעלה ב-production mode
uvicorn dashboard.web_dashboard:app --host 0.0.0.0 --port 8000 --workers 4
```

### גישה ל-Dashboard:
1. פתח דפדפן
2. נווט ל: `http://localhost:8000`
3. תראה את ה-Dashboard המלא

---

## 📓 Jupyter Notebook Dashboard - הפעלה

### שלב 1: הפעל Jupyter

```powershell
# נווט לתיקיית Dashboard
cd C:\Vs-Pro\TR\Trading_System\dashboard

# הפעל Jupyter Notebook
jupyter notebook notebook_dashboard.ipynb
```

### שלב 2: הרץ את התאים

1. הדפדפן ייפתח אוטומטית
2. הרץ את התא הראשון (Imports)
3. התחבר למערכת עם כפתור "Connect"
4. השתמש בכפתורים השונים לניתוח

---

## 🎯 תכונות Web Dashboard

### 1. סטטיסטיקות בזמן אמת
- ✅ רווח/הפסד כולל (Total P&L)
- ✅ פוזיציות פתוחות (Open Positions)
- ✅ סיגנלים שנוצרו (Signals Generated)
- ✅ חשיפה כוללת (Total Exposure)

### 2. גרפים אינטראקטיביים
- 📈 עקומת הון (Equity Curve)
- 📊 התפלגות P&L לפי מניה
- 🥧 חשיפה לפי מניה (Pie Chart)

### 3. טבלת פוזיציות
- מניה, צד, כמות
- מחירי כניסה ונוכחי
- רווח/הפסד ממומש ולא ממומש
- אחוזי שינוי

### 4. בקרת מערכת
- ▶️ הפעלת מסחר (Start Trading)
- ⏹️ עצירת מסחר (Stop Trading)
- 🔄 עדכון אוטומטי כל שנייה

### 5. התראות
- 🔔 התראות בזמן אמת
- 📧 אינטגרציה עם Email
- 💬 אינטגרציה עם Telegram

---

## 🎨 Jupyter Dashboard - תכונות

### 1. ויזואליזציה מתקדמת
```python
# יצירת Dashboard
create_main_dashboard()
```
- גרפים דינמיים עם Plotly
- אינדיקטורים חיים
- תרשימי ביצועים

### 2. ניתוח עמוק
```python
# ניתוח ביצועים
create_performance_analysis()
```
- Win Rate, Sharpe Ratio
- Maximum Drawdown
- Risk-Adjusted Returns

### 3. מעקב חי
```python
# מוניטור בזמן אמת
create_live_monitor(duration_seconds=60)
```
- עדכון כל 2 שניות
- מעקב אחר כל הפוזיציות
- התראות אוטומטיות

---

## 🔧 התאמה אישית

### שינוי צבעים (Web Dashboard)

ערוך את `web_dashboard.py` - שינוי ב-CSS:

```css
:root {
    --primary-color: #2563eb;    /* כחול */
    --success-color: #10b981;    /* ירוק */
    --danger-color: #ef4444;     /* אדום */
}
```

### הוספת מדדים חדשים

```python
# הוסף endpoint חדש
@app.get("/api/custom_metric")
async def get_custom_metric():
    # הלוגיקה שלך כאן
    return {"metric": value}
```

### שינוי תדירות עדכון

```javascript
// ב-HTML של web_dashboard.py
await asyncio.sleep(1)  // שנה ל-5 לעדכון כל 5 שניות
```

---

## 🐛 פתרון בעיות

### בעיה 1: "Module not found"
**פתרון:**
```powershell
pip install --upgrade -r requirements.txt
```

### בעיה 2: "Port already in use"
**פתרון:**
```powershell
# מצא את התהליך תפוס
netstat -ano | findstr :8000

# סגור את התהליך
taskkill /PID <PID_NUMBER> /F

# או השתמש בפורט אחר
python web_dashboard.py --port 8080
```

### בעיה 3: "Cannot connect to IB Gateway"
**פתרון:**
1. וודא ש-IB Gateway פועל
2. בדוק שהפורט 7497 פתוח
3. בדוק הגדרות API ב-IB Gateway:
   - Socket Port: 7497
   - Read-Only API: No
   - Allow connections from localhost

### בעיה 4: Dashboard לא מתעדכן
**פתרון:**
1. בדוק את ה-WebSocket connection בקונסול הדפדפן
2. רענן את הדף
3. נקה Cache ונסה שוב

---

## 📊 השוואת ממשקים

| תכונה | Web Dashboard | Jupyter Dashboard |
|-------|---------------|-------------------|
| **גישה** | דפדפן | Jupyter |
| **עדכונים** | WebSocket (real-time) | Manual/Auto refresh |
| **התאמה אישית** | HTML/CSS/JS | Python Code |
| **ניתוח** | בסיסי | מתקדם |
| **שיתוף** | URL | Notebook File |
| **ייצוא** | API | CSV/Excel |
| **קלות שימוש** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **גמישות** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎯 איזה ממשק לבחור?

### בחר Web Dashboard אם:
- ✅ אתה רוצה ממשק פשוט וקל לשימוש
- ✅ צריך גישה מרחוק (מכל מכשיר)
- ✅ רוצה עדכונים בזמן אמת אוטומטיים
- ✅ מעדיף ממשק מקצועי ומלוטש

### בחר Jupyter Dashboard אם:
- ✅ אתה מפתח/אנליסט
- ✅ צריך להתאים אישית ולנתח לעומק
- ✅ רוצה להוסיף ניתוחים סטטיסטיים
- ✅ מעדיף סביבת פיתוח גמישה

### המלצה שלי:
**השתמש בשניהם!**
- **Web Dashboard** למעקב יומיומי
- **Jupyter Dashboard** לניתוח ופיתוח

---

## 🚀 הפעלה מהירה (Quick Start)

### Web Dashboard:
```powershell
cd C:\Vs-Pro\TR\Trading_System\dashboard
pip install -r requirements.txt
python web_dashboard.py
# פתח דפדפן: http://localhost:8000
```

### Jupyter Dashboard:
```powershell
cd C:\Vs-Pro\TR\Trading_System\dashboard
pip install -r requirements.txt
jupyter notebook notebook_dashboard.ipynb
# הרץ את התאים בסדר
```

---

## 📞 תמיכה ועזרה

### קבצים רלוונטיים:
- `web_dashboard.py` - קוד הממשק האינטרנטי
- `notebook_dashboard.ipynb` - Jupyter Notebook
- `requirements.txt` - רשימת חבילות
- `README_DASHBOARD.md` - מדריך זה

### לוגים:
```powershell
# בדוק לוגים של Web Dashboard
# הלוגים יופיעו בטרמינל

# בדוק לוגים של מערכת המסחר
cat ..\logs\TradingSystem_main.log
```

---

## ✅ סיכום

שני הממשקים שיצרתי מותאמים במיוחד למערכת המסחר שלך:

1. **Web Dashboard** - פתרון מוכן ומקצועי לניטור בזמן אמת
2. **Jupyter Dashboard** - כלי עוצמתי לניתוח ופיתוח

שניהם:
- ✅ מחוברים ל-Live Trading Engine
- ✅ תומכים ב-IB Gateway
- ✅ מציגים נתונים בזמן אמת
- ✅ מותאמים לעברית
- ✅ קלים להתקנה ולשימוש

**בהצלחה! 🎉**
