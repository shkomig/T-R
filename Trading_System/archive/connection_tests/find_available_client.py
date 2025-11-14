"""
Test multiple Client IDs to find available one
"""
import socket
import time
from ibapi.client import EClient
from ibapi.wrapper import EWrapper

class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
        self.client_id = None
    
    def nextValidId(self, orderId: int):
        print(f"✅ Client ID {self.client_id} connected! Next valid order ID: {orderId}")
        self.connected = True
        self.disconnect()
    
    def connectAck(self):
        print(f"✅ Client ID {self.client_id} - Connection acknowledged!")
    
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        if errorCode == 502:  # Already connected
            print(f"⚠️  Client ID {self.client_id} already in use")
        else:
            print(f"❌ Client ID {self.client_id} Error: {errorCode} - {errorString}")

def test_multiple_clients():
    print("🧪 Testing multiple Client IDs...")
    
    # Try different client IDs
    client_ids = [1000, 1001, 1002, 1003, 1004]
    
    for client_id in client_ids:
        print(f"\n🔌 Trying Client ID: {client_id}")
        app = TestApp()
        app.client_id = client_id
        
        try:
            app.connect("127.0.0.1", 7497, client_id)
            
            # Wait for connection
            timeout = 3
            start_time = time.time()
            
            while not app.connected and (time.time() - start_time) < timeout:
                app.run()
                time.sleep(0.1)
            
            if app.connected:
                print(f"🎉 SUCCESS! Client ID {client_id} is available!")
                return client_id
                
        except Exception as e:
            print(f"💥 Client ID {client_id} Exception: {e}")
        finally:
            if app.isConnected():
                app.disconnect()
    
    print("❌ No available Client ID found")
    return None

if __name__ == "__main__":
    available_id = test_multiple_clients()
    if available_id:
        print(f"\n🎯 Use Client ID: {available_id}")
    else:
        print("\n💭 Try restarting TWS or using a different range")