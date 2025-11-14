# Position Management Scripts Archive

**Archived Date**: 2025-11-10
**Archived By**: MCP-20251110-004
**Total Files**: 12

## Purpose
Manual position management and analysis utilities used during development and emergency situations.

## Files Archived

### Emergency Position Closing
- `close_all_positions.py` - Close all open positions
- `force_close_all.py` - Force close all positions (aggressive)
- `force_close_and_short.py` - Force close and establish short positions

### Position Analysis
- `analyze_positions.py` - Analyze current positions
- `check_real_status.py` - Check real position status
- `check_orders.py` - Check pending orders
- `check_open_orders.py` - Check open orders status
- `balance_positions.py` - Balance portfolio positions

### Position Corrections
- `close_positions_corrected.py` - Corrected position closing logic
- `smart_position_manager.py` - Smart position management utility
- `smart_cleanup.py` - Smart cleanup of stale positions

### Risk Management
- `margin_liberation.py` - Free up margin from positions

## Notes
- These scripts were created for manual intervention during testing
- Position management is now integrated into ExecutionManager
- Preserved for emergency use cases
- Use with caution - these bypass normal risk checks

## Safety Warning
⚠️ These scripts can close positions without normal safety checks. Always verify current positions before using.
