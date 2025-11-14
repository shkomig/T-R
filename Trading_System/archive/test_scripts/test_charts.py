#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Charts Integration
בדיקת שילוב הגרפים

This script tests the charts functionality without connecting to IB.
"""

import sys
import time
from pathlib import Path

# Add project path
sys.path.append(str(Path(__file__).parent))

def test_charts_import():
    """בדיקת import של מודול הגרפים"""
    print("📊 Testing charts import...")
    
    try:
        from charts.live_charts import LiveChartWindow
        print("✅ Charts module imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Failed to import charts: {e}")
        print("💡 You may need to install matplotlib: pip install matplotlib")
        return False

def test_charts_demo():
    """בדיקת גרפים עם נתונים דמו"""
    print("📊 Testing charts with demo data...")
    
    try:
        from charts.live_charts import LiveChartWindow
        
        # יצירת אובייקט גרפים ללא broker (נתונים דמו)
        chart_window = LiveChartWindow(None, ['AAPL', 'TSLA', 'MSFT', 'NVDA'])
        
        print("✅ Chart window created successfully!")
        print("🚀 Starting demo charts...")
        
        # הפעלת גרפים
        chart_thread = chart_window.start()
        
        print("📊 Charts are running...")
        print("💡 Close the chart window to continue...")
        print("⏳ Demo will run for 30 seconds...")
        
        # המתנה 30 שניות
        time.sleep(30)
        
        # עצירת גרפים
        chart_window.stop()
        print("✅ Charts stopped successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing charts: {e}")
        return False

def main():
    """בדיקה ראשית"""
    print("🎯 Charts Integration Test")
    print("=" * 50)
    
    # בדיקת import
    if not test_charts_import():
        print("\n❌ Charts import failed - stopping test")
        return
    
    print("\n" + "─" * 30)
    
    # שאלת משתמש אם לבדוק גרפים
    try:
        user_input = input("\n🤔 Run demo charts test? (y/n): ").lower().strip()
        if user_input in ['y', 'yes', 'כן']:
            print()
            if test_charts_demo():
                print("\n✅ All tests passed!")
            else:
                print("\n❌ Demo test failed")
        else:
            print("\n📊 Chart import test completed successfully!")
            print("💡 Charts are ready to use in the main system")
    
    except KeyboardInterrupt:
        print("\n\n📊 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")

if __name__ == "__main__":
    main()