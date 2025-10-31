# הוראות התקנה והפעלה
## Trading System Setup Guide

### שלב 1: יצירת סביבה וירטואלית

פתח PowerShell בתיקיית המערכת והרץ:

```powershell
cd c:\Vs-Pro\TR\Trading_System

# יצירת virtual environment
python -m venv venv

# הפעלת הסביבה
.\venv\Scripts\Activate.ps1
```

אם מתקבלת שגיאה של Execution Policy, הרץ:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### שלב 2: התקנת ספריות

```powershell
# שדרוג pip
python -m pip install --upgrade pip

# התקנת כל הספריות
pip install -r requirements.txt
```

### שלב 3: התקנת TA-Lib (Windows)

TA-Lib דורש התקנה מיוחדת ב-Windows:

**אופציה 1: דרך pip (מומלץ)**
```powershell
pip install TA-Lib
```

**אופציה 2: אם אופציה 1 לא עובדת**
1. הורד את הקובץ המתאים מ: https://github.com/cgohlke/talib-build/releases
2. בחר לפי גרסת Python שלך (cp310 = Python 3.10, cp311 = Python 3.11)
3. התקן:
```powershell
pip install TA_Lib-0.4.XX-cpXXX-cpXXX-win_amd64.whl
```

### שלב 4: הגדרת TWS/IB Gateway

1. **פתח TWS או IB Gateway**
2. **הגדר API Settings:**
   - עבור ל: File → Global Configuration → API → Settings
   - ✅ Enable ActiveX and Socket Clients
   - ✅ Allow connections from localhost only
   - Port: 7497 (Paper Trading) או 7496 (Live)
   - ✅ Read-Only API
   - ✅ Download open orders on connection
   - לחץ OK

3. **אשר חיבור:**
   - בפעם הראשונה תקבל התראה - אשר את החיבור

### שלב 5: עדכון פרטי חיבור

ערוך את `config/api_credentials.yaml`:

```yaml
interactive_brokers:
  host: "127.0.0.1"
  port: 7497  # Paper Trading (7496 for Live)
  client_id: 1
  account_id: "YOUR_ACCOUNT_ID"  # החלף במספר חשבון שלך
```

⚠️ **חשוב:** אל תשתף את הקובץ הזה!

### שלב 6: בדיקת חיבור

```powershell
# ודא ש-TWS/Gateway פועל ו-API מופעל
python test_ib_connection.py
```

אם הכל עובד, תראה:

```
==============================================================
  TESTING INTERACTIVE BROKERS CONNECTION
==============================================================

✓ Configuration loaded
Connecting to 127.0.0.1:7497...
✓ Connection successful

--------------------------------------------------------------
ACCOUNT INFORMATION
--------------------------------------------------------------
  NetLiquidation     :      1000000.00 USD
  TotalCashValue     :      1000000.00 USD
  BuyingPower        :      4000000.00 USD
  ...

--------------------------------------------------------------
CURRENT POSITIONS
--------------------------------------------------------------
  No open positions

--------------------------------------------------------------
TESTING HISTORICAL DATA RETRIEVAL
--------------------------------------------------------------
Fetching 1 day of 30-minute bars for AAPL...
✓ Retrieved 13 bars
...
```

### שלב 7: בדיקת main.py

```powershell
# בדיקה במצב paper trading
python main.py --mode paper --log-level INFO
```

### פתרון בעיות נפוצות

#### שגיאה: "Failed to connect to IB"

**פתרונות:**
1. ודא ש-TWS/Gateway פועל
2. בדוק ש-API Settings מופעל (Enable ActiveX and Socket Clients)
3. בדוק שהפורט נכון (7497 ל-Paper, 7496 ל-Live)
4. נסה להפעיל מחדש את TWS/Gateway

#### שגיאה: "No module named 'talib'"

```powershell
# התקן TA-Lib
pip install TA-Lib

# אם לא עובד, הורד wheel מהלינק למעלה
```

#### שגיאה: "Cannot be loaded because running scripts is disabled"

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### שגיאה: Connection refused / Timeout

1. בדוק שהפיירוול לא חוסם
2. ודא שלא יש תוכנית אחרת שמשתמשת באותו client_id
3. נסה client_id אחר (2, 3, 4...)

### המשך עבודה

לאחר שהכל עובד:

1. **התאם את config/trading_config.yaml** לצרכים שלך
2. **התאם את config/risk_management.yaml** לרמת הסיכון שלך  
3. **התחל לפתח אסטרטגיות** בתיקיית strategies/

### פקודות שימושיות

```powershell
# הפעלת הסביבה הוירטואלית
.\venv\Scripts\Activate.ps1

# כיבוי הסביבה
deactivate

# בדיקת גרסאות מותקנות
pip list

# עדכון ספרייה ספציפית
pip install --upgrade pandas

# הרצת בדיקות
pytest tests/ -v

# הצגת לוגים
python main.py --mode paper --log-level DEBUG
```

### מצב Paper Trading vs Live

**Paper Trading (פורט 7497):**
- ✅ בטוח לבדיקות
- ✅ כסף וירטואלי
- ✅ מומלץ להתחיל כאן

**Live Trading (פורט 7496):**
- ⚠️ כסף אמיתי!
- ⚠️ רק אחרי backtesting מקיף
- ⚠️ התחל עם הון קטן

---

**זכור:** 
- תמיד התחל ב-Paper Trading
- בדוק את המערכת מספר שבועות לפחות
- אל תסחור בכסף אמיתי בלי backtesting מקיף!

**בהצלחה! 🚀**
