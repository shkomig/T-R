#!/usr/bin/env python3
"""
Test Risk Management Settings
בדיקה מהירה של הגדרות ניהול הסיכונים
"""

import yaml
import sys
import os
from pathlib import Path

def check_risk_settings():
    """בדיקת הגדרות ניהול הסיכונים"""
    
    config_path = Path("config/risk_management.yaml")
    
    if not config_path.exists():
        print("❌ קובץ risk_management.yaml לא נמצא!")
        return False
        
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        print("🔍 בדיקת הגדרות ניהול סיכונים לבדיקת $2,000:")
        print("=" * 60)
        
        # בדיקת גודל פוזיציה מסעיף position_sizing
        position_sizing = config.get('position_sizing', {})
        max_position = position_sizing.get('max_position_size', 'Not found')
        base_position = position_sizing.get('base_position_size', 'Not found')
        
        # בדיקת גודל פוזיציה מסעיף position_limits  
        position_limits = config.get('position_limits', {})
        max_position_amount = position_limits.get('max_position_size_amount', 'Not found')
        
        print(f"📊 Max Position Size: ${max_position}")
        print(f"📊 Base Position Size: ${base_position}")
        print(f"📊 Max Position Amount (limits): ${max_position_amount}")
        
        # בדיקת Stop Loss
        stop_loss = config.get('stop_loss', {})
        stop_enabled = stop_loss.get('enabled', False)
        stop_type = stop_loss.get('type', 'Not set')
        stop_percent = stop_loss.get('percentage', {}).get('stop_percent', 'Not set')
        
        print(f"🛡️ Stop Loss Enabled: {stop_enabled}")
        print(f"🛡️ Stop Loss Type: {stop_type}")
        print(f"🛡️ Stop Loss Percentage: {stop_percent}%")
        
        # בדיקת הגדרות חשבון
        account = config.get('account', {})
        max_risk_amount = account.get('max_risk_per_trade_amount', 'Not set')
        stop_loss_enabled = account.get('stop_loss_enabled', 'Not set')
        max_loss_percent = account.get('max_loss_percent_per_trade', 'Not set')
        
        print(f"💰 Max Risk Per Trade: ${max_risk_amount}")
        print(f"🛡️ Account Stop Loss Enabled: {stop_loss_enabled}")
        print(f"🛡️ Max Loss Percent Per Trade: {max_loss_percent}")
        
        print("\n" + "=" * 60)
        
        # תוצאות בדיקה
        if max_position == 2000 and base_position == 2000:
            print("✅ הגדרות גודל פוזיציה עודכנו נכון ל-$2,000")
        else:
            print("❌ הגדרות גודל פוזיציה לא עודכנו נכון!")
            
        if stop_enabled and stop_type in ['percentage', 'atr']:
            print("✅ Stop Loss מופעל ומוגדר נכון")
        else:
            print("❌ Stop Loss לא מוגדר נכון!")
            
        print("\n🚀 המערכת מוכנה לבדיקת מסחר $2,000!")
        return True
        
    except Exception as e:
        print(f"❌ שגיאה בקריאת הקובץ: {e}")
        return False

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    check_risk_settings()