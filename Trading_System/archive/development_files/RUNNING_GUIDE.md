# 🚀 הרצת מערכת המסחר עם דשבורד

## שיטות הפעלה

### אפשרות 1: הרצה מלאה (מומלץ) ✨

הרצת המנוע + הדשבורד ביחד:

```powershell
.\start_trading_system.ps1
```

**מה זה עושה:**
- פותח חלון עם Web Dashboard (http://localhost:8000)
- מריץ את מנוע המסחר בחלון הנוכחי
- שני הרכיבים עובדים במקביל

**דרישות:**
- IB Gateway חייב לרוץ על פורט 7497
- Python 3.12+ מותקן

---

### אפשרות 2: הרצה נפרדת

#### שלב 1: הפעל את הדשבורד

```powershell
cd dashboard
.\start_dashboard.ps1
```

או:

```powershell
python dashboard\web_dashboard.py
```

#### שלב 2: הפעל את המנוע (בחלון נפרד)

```powershell
python test_live_trading.py full
```

---

## 📊 גישה לדשבורד

פתח דפדפן:
```
http://localhost:8000
```

**תכונות הדשבורד:**
- ✅ מעקב בזמן אמת אחר P&L
- ✅ הצגת פוזיציות פתוחות
- ✅ גרף עקומת הון (Equity Curve)
- ✅ סטטיסטיקות ביצועים
- ✅ חיווי סטטוס מערכת

---

## 🛑 עצירת המערכת

### אם השתמשת ב-start_trading_system.ps1:
1. לחץ `Ctrl+C` בחלון המסחר
2. סגור את חלון הדשבורד

### אם הרצת בנפרד:
לחץ `Ctrl+C` בכל אחד מהחלונות

---

## ⚠️ פתרון בעיות

### הדשבורד לא מציג נתונים

**בעיה:** הדשבורד מציג $0.00 בכל מקום

**פתרון:** 
- הדשבורד עובד במצב "ניטור בלבד" כאשר המנוע לא רץ
- הרץ את המנוע במקביל: `python test_live_trading.py full`
- הדשבורד יתעדכן אוטומטית ברגע שהמנוע מתחבר

### אי אפשר להתחיל מסחר מהדשבורד

**בעיה:** לחיצה על "התחל מסחר" נכשלת עם שגיאה

**סיבה:** IB Gateway דורש להרץ בתהליך הראשי, לא דרך FastAPI

**פתרון:** השתמש באפשרות 1 - הרץ את המנוע ישירות:
```powershell
python test_live_trading.py full
```

### IB Gateway לא מחובר

**שגיאה:** `Failed to connect to IB Gateway`

**פתרון:**
1. ודא ש-IB Gateway רץ
2. בדוק שהפורט 7497 פתוח
3. אשר את החיבור ב-IB Gateway (תיבת דו-שיח)

---

## 📁 מבנה הקבצים

```
Trading_System/
├── start_trading_system.ps1          # הפעלה מלאה (מומלץ)
├── test_live_trading.py              # מנוע המסחר
└── dashboard/
    ├── start_dashboard.ps1           # הדשבורד בלבד
    ├── web_dashboard.py              # שרת הדשבורד
    └── cli_dashboard.py              # דשבורד טרמינל (חלופי)
```

---

## 💡 טיפים

### מצב פיתוח
אם אתה מפתח ורוצה לבדוק שינויים:
```powershell
# חלון 1: Dashboard עם auto-reload
python dashboard\web_dashboard.py

# חלון 2: מנוע עם לוגים
python test_live_trading.py full
```

### מצב ייצור
להרצה רציפה 24/7:
```powershell
.\start_trading_system.ps1
```

### בדיקה מהירה
רק לבדיקת חיבור (לא מסחר):
```powershell
python test_live_trading.py quick
```

---

## 📚 דשבורדים נוספים

### CLI Dashboard (טרמינל)
```powershell
cd dashboard
python cli_dashboard.py
```

טוב לשימוש ב:
- SSH / Remote
- בדיקות מהירות
- מערכות בלי GUI

### Jupyter Dashboard (ניתוח)
```powershell
jupyter notebook dashboard\notebook_dashboard.ipynb
```

טוב ל:
- ניתוח עמוק
- גרפים אינטראקטיביים
- פיתוח אסטרטגיות

---

## 🔗 קישורים שימושיים

- **דשבורד Web:** http://localhost:8000
- **API Status:** http://localhost:8000/api/status
- **API Performance:** http://localhost:8000/api/performance
- **תיעוד מלא:** `dashboard/README_DASHBOARD.md`

---

## 📞 תמיכה

אם יש בעיות:
1. בדוק שIB Gateway רץ ומחובר
2. ודא שהפורטים 8000 ו-7497 פנויים
3. הפעל מחדש את המערכת
4. בדוק לוגים ב-`logs/` directory

---

**בהצלחה! 🎯📈**
