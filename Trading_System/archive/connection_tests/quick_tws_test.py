#!/usr/bin/env python3
"""
Quick TWS API Test
==================
בדיקה מהירה לחיבור TWS API
"""

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import time
import threading

class QuickTest(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
        self.error_occurred = False
        
    def nextValidId(self, orderId: int):
        print(f'✅ SUCCESS: Connected to TWS! Next Order ID: {orderId}')
        self.connected = True
        
    def connectAck(self):
        print('📡 TWS acknowledged connection')
        
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=''):
        print(f'⚠️  TWS Error {errorCode}: {errorString}')
        self.error_occurred = True

def test_connection(client_id=31):
    print(f'🔌 Testing TWS connection with Client ID: {client_id}')
    
    app = QuickTest()
    
    try:
        # Connect
        app.connect('127.0.0.1', 7497, client_id)
        
        # Start message loop in thread
        thread = threading.Thread(target=app.run, daemon=True)
        thread.start()
        
        # Wait for result
        for i in range(10):  # 10 second timeout
            time.sleep(1)
            if app.connected:
                print('🎯 Connection successful!')
                app.disconnect()
                return True
            elif app.error_occurred:
                print('❌ Connection failed with error')
                break
                
        print('⏰ Connection timeout')
        return False
        
    except Exception as e:
        print(f'❌ Exception: {e}')
        return False

if __name__ == "__main__":
    print("🎯 TWS API CONNECTION TEST")
    print("=" * 40)
    
    # Test different client IDs
    for client_id in [31, 1, 32, 33]:
        print(f"\n🔄 Trying Client ID: {client_id}")
        if test_connection(client_id):
            print(f"✅ SUCCESS with Client ID: {client_id}")
            break
        time.sleep(2)
    else:
        print("\n❌ All connection attempts failed")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check Windows Firewall settings")
        print("2. Temporarily disable antivirus")
        print("3. In TWS: File → Global Configuration → API → Settings")
        print("   - Uncheck and recheck 'Enable ActiveX and Socket Clients'")
        print("   - Try changing Master API Client ID to 1")
        print("4. Restart TWS completely")