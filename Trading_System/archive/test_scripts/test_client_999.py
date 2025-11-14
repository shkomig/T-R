"""
Test TWS connection with Client ID 999
"""
import socket
import time
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
    
    def nextValidId(self, orderId: int):
        print(f"✅ Connected! Next valid order ID: {orderId}")
        self.connected = True
        self.disconnect()
    
    def connectAck(self):
        print("✅ Connection acknowledged!")
    
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        print(f"❌ Error: {errorCode} - {errorString}")

def test_connection():
    print("🧪 Testing TWS connection with Client ID 999...")
    
    app = TestApp()
    
    try:
        app.connect("127.0.0.1", 7497, 999)
        print("🔌 Connection attempt initiated...")
        
        # Wait for connection
        timeout = 10
        start_time = time.time()
        
        while not app.connected and (time.time() - start_time) < timeout:
            app.run()
            time.sleep(0.1)
        
        if app.connected:
            print("🎉 SUCCESS! Client ID 999 works!")
            return True
        else:
            print("❌ TIMEOUT! Connection failed")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False
    finally:
        if app.isConnected():
            app.disconnect()

if __name__ == "__main__":
    test_connection()