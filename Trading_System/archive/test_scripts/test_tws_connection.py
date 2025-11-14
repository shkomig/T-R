#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TWS Connection Test
בדיקת חיבור ל-TWS

Tests different ports and client IDs to find the correct connection.
"""

import sys
from pathlib import Path
import time

# Add project path
sys.path.append(str(Path(__file__).parent))

try:
    from execution.broker_interface import IBBroker
except ImportError:
    print("❌ Cannot import IBBroker - check if the module exists")
    sys.exit(1)

def test_connection(port, client_id):
    """בדיקת חיבור עם פורט ו-client ID ספציפיים"""
    print(f"🔌 Testing connection: Port {port}, Client ID {client_id}")
    
    try:
        broker = IBBroker(port=port, client_id=client_id)
        
        if broker.connect():
            print(f"✅ SUCCESS! Connected on Port {port}, Client ID {client_id}")
            broker.disconnect()
            return True
        else:
            print(f"❌ Failed to connect on Port {port}, Client ID {client_id}")
            return False
            
    except Exception as e:
        print(f"❌ Error on Port {port}, Client ID {client_id}: {e}")
        return False

def main():
    """בדיקה ראשית"""
    print("🎯 TWS Connection Test")
    print("=" * 50)
    print("🔍 Testing different ports and client IDs...")
    print()
    
    # רשימת אפשרויות לבדיקה
    test_configs = [
        (7497, 31),   # TWS Live - מה שהגדרנו
        (7497, 30),   # TWS Live - client ID ישן
        (7497, 1),    # TWS Live - client ID רגיל
        (7496, 31),   # TWS Paper Trading
        (7496, 30),   # TWS Paper Trading
        (7496, 1),    # TWS Paper Trading
        (4001, 31),   # IB Gateway Live
        (4001, 30),   # IB Gateway Live
        (4002, 31),   # IB Gateway Paper
        (4002, 30),   # IB Gateway Paper
    ]
    
    successful_connections = []
    
    for port, client_id in test_configs:
        if test_connection(port, client_id):
            successful_connections.append((port, client_id))
        time.sleep(1)  # המתנה קצרה בין בדיקות
        print()
    
    print("=" * 50)
    print("📊 RESULTS:")
    
    if successful_connections:
        print(f"✅ Found {len(successful_connections)} working connection(s):")
        for port, client_id in successful_connections:
            print(f"   ➤ Port {port}, Client ID {client_id}")
        
        print("\n💡 Update your trading system with:")
        best_port, best_client_id = successful_connections[0]
        print(f"   self.broker = IBBroker(port={best_port}, client_id={best_client_id})")
        
    else:
        print("❌ No working connections found!")
        print("\n🔧 Troubleshooting steps:")
        print("1. Make sure TWS is open and logged in")
        print("2. Check API settings: File > Global Configuration > API")
        print("3. Verify 'Enable ActiveX and Socket Clients' is checked")
        print("4. Try paper trading mode (port 7496)")
        print("5. Restart TWS and try again")

if __name__ == "__main__":
    main()