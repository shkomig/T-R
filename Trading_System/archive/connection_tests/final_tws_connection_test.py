#!/usr/bin/env python3
"""
Final TWS Connection Test
Based on official IB API documentation and best practices
"""

import time
import socket
import threading
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

class TestWrapper(EWrapper):
    def __init__(self):
        EWrapper.__init__(self)
        self.connected = False
        self.nextOrderId = None
        self.connection_time = None
        
    def connectAck(self):
        """Called when API connection is acknowledged"""
        print("✅ API Connection Acknowledged!")
        self.connected = True
        self.connection_time = time.time()
        
    def nextValidId(self, orderId: int):
        """Called when connection is fully established"""
        print(f"✅ Connection Complete! Next Order ID: {orderId}")
        self.nextOrderId = orderId
        
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        """Handle all errors and status messages"""
        print(f"📊 Message {errorCode}: {errorString}")
        if errorCode in [2104, 2106, 2158]:  # Connection OK messages
            print("✅ Data farm connection is OK")
        elif errorCode == 502:
            print("❌ Cannot connect to TWS - Check TWS API settings")
        elif errorCode == 507:
            print("❌ Bad message - possible client ID conflict")
        elif errorCode == 326:
            print("❌ Client ID already in use")
        elif errorCode in [1100, 1101, 1102]:
            print("⚠️ TWS-IB Server connectivity issue")

class TestClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)

def test_port_connection(host, port):
    """Test if port is accessible"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            return result == 0
    except Exception as e:
        print(f"❌ Port test error: {e}")
        return False

def main():
    print("🔧 Final TWS API Connection Test")
    print("="*50)
    
    # Test configuration from your settings
    HOST = "127.0.0.1"
    PORT = 7497  # Paper Trading
    CLIENT_ID = 31  # Your Master API Client ID
    
    print(f"📋 Connection Parameters:")
    print(f"   Host: {HOST}")
    print(f"   Port: {PORT}")
    print(f"   Client ID: {CLIENT_ID}")
    print()
    
    # Step 1: Test port connectivity
    print("🔍 Step 1: Testing port connectivity...")
    if test_port_connection(HOST, PORT):
        print(f"✅ Port {PORT} is accessible")
    else:
        print(f"❌ Port {PORT} is NOT accessible")
        print("   Make sure TWS is running with API enabled")
        return
    
    # Step 2: Create API objects
    print("\n🔍 Step 2: Creating API objects...")
    wrapper = TestWrapper()
    client = TestClient(wrapper)
    
    try:
        # Step 3: Attempt connection
        print(f"\n🔍 Step 3: Connecting to TWS...")
        client.connect(HOST, PORT, CLIENT_ID)
        
        # Step 4: Start message processing thread
        print("🔍 Step 4: Starting message processing...")
        
        def run_loop():
            client.run()
        
        api_thread = threading.Thread(target=run_loop, daemon=True)
        api_thread.start()
        
        # Step 5: Wait for connection
        print("🔍 Step 5: Waiting for connection confirmation...")
        start_time = time.time()
        timeout = 15  # 15 seconds timeout
        
        while not wrapper.nextOrderId and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        if wrapper.nextOrderId:
            print(f"🎉 SUCCESS! Connected to TWS")
            print(f"   Connection time: {wrapper.connection_time}")
            print(f"   Next valid order ID: {wrapper.nextOrderId}")
            
            # Test basic functionality
            print("\n🔍 Step 6: Testing basic functionality...")
            current_time = client.reqCurrentTime()
            time.sleep(2)
            
        else:
            print(f"❌ TIMEOUT: No response after {timeout} seconds")
            print("   Possible issues:")
            print("   1. TWS API might not be properly enabled")
            print("   2. Client ID conflict")
            print("   3. TWS might be locked/frozen")
            print("   4. Windows Firewall blocking connection")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print(f"   Error type: {type(e).__name__}")
        
    finally:
        print("\n🔍 Step 7: Cleaning up...")
        try:
            client.disconnect()
        except:
            pass
        print("✅ Test completed")

if __name__ == "__main__":
    main()