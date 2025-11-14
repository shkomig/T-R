"""
בדיקת חיבור TWS עם Client IDs שונים
"""
import socket
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import threading
import time

class TestWrapper(EWrapper):
    def __init__(self):
        EWrapper.__init__(self)
        self.connected = False
        
    def connectAck(self):
        print("🟢 Connection acknowledged!")
        self.connected = True
        
    def error(self, reqId, errorCode, errorString):
        print(f"❌ Error {errorCode}: {errorString}")

class TestClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)

def test_connection_with_client_id(client_id):
    print(f"\n🔌 Testing with Client ID: {client_id}")
    
    wrapper = TestWrapper()
    client = TestClient(wrapper)
    
    try:
        # נסיון חיבור
        client.connect("127.0.0.1", 7497, client_id)
        
        # Start the message loop in a thread
        api_thread = threading.Thread(target=client.run, daemon=True)
        api_thread.start()
        
        # Wait for connection
        timeout = 10
        start_time = time.time()
        
        while not wrapper.connected and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        if wrapper.connected:
            print(f"✅ SUCCESS! Connected with Client ID {client_id}")
            client.disconnect()
            return True
        else:
            print(f"❌ TIMEOUT! Failed to connect with Client ID {client_id}")
            client.disconnect()
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION with Client ID {client_id}: {e}")
        return False

def main():
    print("🔍 Testing TWS Connection with Multiple Client IDs")
    print("=" * 60)
    
    # רשימת Client IDs לבדיקה
    client_ids = [0, 1, 2, 31, 32, 33, 100, 999]
    
    successful_connections = []
    
    for client_id in client_ids:
        success = test_connection_with_client_id(client_id)
        if success:
            successful_connections.append(client_id)
        time.sleep(2)  # Wait between attempts
    
    print("\n" + "=" * 60)
    print("📊 RESULTS:")
    if successful_connections:
        print(f"✅ Successful Client IDs: {successful_connections}")
        print(f"🎯 Recommended Client ID: {successful_connections[0]}")
    else:
        print("❌ No successful connections!")
        print("🔧 TWS API might not be properly configured or running")

if __name__ == "__main__":
    main()