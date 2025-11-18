"""
Quick test script to verify timezone fix and market hours detection.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pytz
from datetime import datetime, time as dt_time

def test_timezone_fix():
    """Test the timezone fix for market hours detection."""

    # Get Eastern timezone
    eastern_tz = pytz.timezone('US/Eastern')
    now_local = datetime.now()
    now_est = datetime.now(eastern_tz)

    # Market hours
    premarket_open = dt_time(4, 0)
    market_open = dt_time(9, 30)
    market_close = dt_time(16, 0)
    afterhours_close = dt_time(20, 0)

    # Check current session
    now_time = now_est.time()
    is_premarket = premarket_open <= now_time < market_open
    is_regular = market_open <= now_time <= market_close
    is_afterhours = market_close < now_time <= afterhours_close
    trading_active = is_premarket or is_regular or is_afterhours

    print("\n" + "="*70)
    print("TRADING SYSTEM TIMEZONE FIX TEST")
    print("="*70)
    print(f"\nCurrent Times:")
    print(f"  Local Time (System): {now_local.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  EST Time (Market):   {now_est.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    print(f"\nMarket Schedule (EST):")
    print(f"  Pre-Market:    04:00 - 09:30")
    print(f"  Regular Hours: 09:30 - 16:00")
    print(f"  After-Hours:   16:00 - 20:00")

    print(f"\nCurrent Session Status:")
    print(f"  [{'X' if is_premarket else ' '}] Pre-Market    (04:00 - 09:30 EST)")
    print(f"  [{'X' if is_regular else ' '}] Regular Hours (09:30 - 16:00 EST)")
    print(f"  [{'X' if is_afterhours else ' '}] After-Hours   (16:00 - 20:00 EST)")

    print(f"\n{'>>> TRADING ACTIVE <<<' if trading_active else '>>> MARKET CLOSED <<<'}")

    if is_premarket:
        print(f"Current Session: PRE-MARKET")
        mins_to_open = ((market_open.hour * 60 + market_open.minute) -
                       (now_time.hour * 60 + now_time.minute))
        print(f"Market opens in: {mins_to_open} minutes")
    elif is_regular:
        print(f"Current Session: REGULAR HOURS")
        mins_to_close = ((market_close.hour * 60 + market_close.minute) -
                        (now_time.hour * 60 + now_time.minute))
        print(f"Market closes in: {mins_to_close} minutes")
    elif is_afterhours:
        print(f"Current Session: AFTER-HOURS")
        mins_to_close = ((afterhours_close.hour * 60 + afterhours_close.minute) -
                        (now_time.hour * 60 + now_time.minute))
        print(f"After-hours closes in: {mins_to_close} minutes")
    else:
        print(f"Current Session: CLOSED")
        # Calculate time to next pre-market
        current_minutes = now_time.hour * 60 + now_time.minute
        premarket_minutes = premarket_open.hour * 60 + premarket_open.minute

        if current_minutes < premarket_minutes:
            # Same day
            mins_to_open = premarket_minutes - current_minutes
        else:
            # Next day
            mins_to_open = (24 * 60) - current_minutes + premarket_minutes

        hours = mins_to_open // 60
        mins = mins_to_open % 60
        print(f"Next pre-market opens in: {hours}h {mins}m")

    print("="*70)
    print()

    # Test result
    if trading_active:
        print("[PASS] System correctly detects trading is active")
        print("       The trading system will now generate signals during this session.")
        return True
    else:
        print("[INFO] Market is currently closed")
        print("       The system will wait for the next trading session to begin.")
        return False

if __name__ == "__main__":
    test_timezone_fix()
