"""
הרצת מערכת המסחר עם דשבורד Web
====================================
סקריפט זה מריץ:
1. מנוע המסחר (מתחבר ל-IB Gateway)
2. Web Dashboard (ממשק ניטור)

שניהם רצים במקביל בתהליכים נפרדים.
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def main():
    print("=" * 60)
    print("🚀 מתחיל מערכת מסחר + דשבורד")
    print("=" * 60)
    print()
    
    # בדיקת IB Gateway
    print("⚠️  וודא ש-IB Gateway רץ על פורט 7497")
    print()
    
    response = input("האם IB Gateway רץ? (yes/no): ").strip().lower()
    if response not in ['yes', 'y', 'כן']:
        print("❌ בטל. הפעל את IB Gateway ונסה שוב.")
        return
    
    print()
    print("📊 מתחיל תהליכים...")
    print()
    
    # תיקיית הפרויקט
    project_dir = Path(__file__).parent
    dashboard_dir = project_dir / "dashboard"
    
    try:
        # 1. הפעלת Web Dashboard
        print("1️⃣  מפעיל Web Dashboard...")
        dashboard_process = subprocess.Popen(
            [sys.executable, str(dashboard_dir / "web_dashboard.py")],
            cwd=str(project_dir),
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        time.sleep(3)  # המתנה לאתחול השרת
        print("   ✅ Dashboard רץ על http://localhost:8000")
        print()
        
        # 2. הפעלת Live Trading Engine
        print("2️⃣  מפעיל מנוע מסחר...")
        print("   מתחבר ל-IB Gateway...")
        print()
        
        # רץ בחלון הנוכחי כדי לראות את הלוגים
        trading_process = subprocess.Popen(
            [sys.executable, "test_live_trading.py", "full"],
            cwd=str(project_dir)
        )
        
        print()
        print("=" * 60)
        print("✅ המערכת רצה!")
        print("=" * 60)
        print()
        print("📱 דשבורד: http://localhost:8000")
        print("🔍 מנוע מסחר: רץ בחלון זה")
        print()
        print("⚠️  לעצירה: לחץ Ctrl+C")
        print()
        
        # המתנה לסיום
        trading_process.wait()
        
    except KeyboardInterrupt:
        print()
        print("🛑 עוצר את המערכת...")
        
        # עצירת התהליכים
        try:
            dashboard_process.terminate()
            trading_process.terminate()
        except:
            pass
        
        print("✅ המערכת נעצרה")
    
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        print()
        print("אפשר להריץ את הרכיבים בנפרד:")
        print("1. python dashboard/web_dashboard.py")
        print("2. python test_live_trading.py full")

if __name__ == "__main__":
    main()
