#!/usr/bin/env python3
"""
TWS Connection Diagnostics
=========================
בודק את החיבור ל-TWS ומספק הנחיות לתיקון
"""

import socket
import time
import subprocess
import platform

def check_port_listening(host='127.0.0.1', port=7497):
    """בודק אם הפורט פתוח"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def check_tws_process():
    """בודק אם TWS רץ"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq tws.exe'], 
                                  capture_output=True, text=True)
            return 'tws.exe' in result.stdout.lower()
        else:
            result = subprocess.run(['pgrep', '-f', 'tws'], capture_output=True)
            return len(result.stdout) > 0
    except:
        return False

def main():
    print("🔍 TWS CONNECTION DIAGNOSTICS")
    print("=" * 50)
    
    # Check if TWS process is running
    print("\n1. 🖥️  Checking if TWS is running...")
    tws_running = check_tws_process()
    if tws_running:
        print("   ✅ TWS process detected")
    else:
        print("   ❌ TWS process not found")
        print("   💡 Please start TWS first")
    
    # Check if API port is listening
    print("\n2. 📡 Checking API port 7497...")
    port_open = check_port_listening()
    if port_open:
        print("   ✅ Port 7497 is OPEN and listening")
        print("   🎯 TWS API is ready!")
    else:
        print("   ❌ Port 7497 is NOT listening")
        print("   💡 API is not enabled or TWS needs restart")
    
    # Check paper trading port too
    print("\n3. 📡 Checking Live Trading port 7496...")
    live_port_open = check_port_listening(port=7496)
    if live_port_open:
        print("   ✅ Port 7496 is OPEN (Live Trading)")
    else:
        print("   ❌ Port 7496 is not listening")
    
    print("\n" + "=" * 50)
    
    # Provide recommendations
    if not tws_running:
        print("🚨 ACTION NEEDED:")
        print("   1. Start TWS (Trader Workstation)")
        print("   2. Log in to your account")
        print("   3. Enable API in Global Configuration")
        
    elif not port_open and not live_port_open:
        print("🚨 ACTION NEEDED:")
        print("   1. In TWS: File → Global Configuration → API → Settings")
        print("   2. Check: ✅ Enable ActiveX and Socket Clients")
        print("   3. Set Socket port: 7497")
        print("   4. Set Master API client ID: 31")
        print("   5. Click OK and RESTART TWS")
        
    elif port_open or live_port_open:
        print("✅ TWS API IS READY!")
        print("🚀 You can now run the trading system:")
        print("   python start_professional_trading.py")
        
        if port_open:
            print("   📊 Mode: Paper Trading (Port 7497)")
        if live_port_open:
            print("   💰 Mode: Live Trading (Port 7496)")

if __name__ == "__main__":
    main()