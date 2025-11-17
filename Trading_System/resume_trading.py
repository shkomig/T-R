"""
Resume Trading Script
=====================
Script to clear emergency halt and resume trading operations.

Author: Claude AI
Date: 2025-11-17
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from risk_management.emergency_halt_manager import EmergencyHaltManager

def main():
    print("="*70)
    print("TRADING RESUME SCRIPT")
    print("="*70)

    # Initialize halt manager
    config_path = Path(__file__).parent / 'config' / 'risk_management.yaml'
    data_dir = Path(__file__).parent / 'data'

    manager = EmergencyHaltManager(
        config_path=str(config_path),
        data_dir=str(data_dir)
    )

    # Check current status
    print("\nCurrent Status:")
    print(manager.get_halt_summary())

    if not manager.is_halted():
        print("\n[INFO] System is not halted - already active")
        return

    # Confirm resume
    print("\n" + "="*70)
    print("RESUME TRADING CONFIRMATION")
    print("="*70)
    print("\nYou are about to resume trading operations.")
    print("Drawdown limit has been increased to 20%.")
    print("\nIMPORTANT:")
    print("- Ensure market conditions are favorable")
    print("- Review what caused the previous halt")
    print("- Monitor the system closely after resuming")
    print("\n" + "="*70)

    response = input("\nType 'RESUME' to proceed: ")

    if response.strip() != "RESUME":
        print("\n[CANCELLED] Resume operation cancelled")
        return

    # Force resume (bypasses cooldown)
    print("\n[ACTION] Forcing resume...")
    success, message = manager.resume_trading(
        authorization_code="Manual-Resume-2025-11-17",
        force=True
    )

    if success:
        print("\n" + "="*70)
        print("SUCCESS - TRADING RESUMED")
        print("="*70)
        print(f"\n{message}")
        print("\nNew Configuration:")
        print("- Max Drawdown: 20% (previously 15%)")
        print("- System Status: ACTIVE")
        print("\nNext Steps:")
        print("1. Monitor the dashboard closely")
        print("2. Watch for signals being generated")
        print("3. Check position sizes are appropriate")
        print("4. Review trades as they execute")
        print("\n" + "="*70)
    else:
        print("\n[ERROR] Failed to resume trading")
        print(f"Reason: {message}")
        print("\nPlease check the logs and try again.")

    # Show final status
    print("\nFinal Status:")
    print(manager.get_halt_summary())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Operation interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
