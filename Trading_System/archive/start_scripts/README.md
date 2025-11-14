# Start Scripts Archive

**Archived Date**: 2025-11-10
**Archived By**: MCP-20251110-004
**Total Files**: 1

## Purpose
Legacy start scripts superseded by current dashboard system.

## Files Archived

- `start_professional_trading.py` - Old professional trading system starter

## Why Archived
- Superseded by `simple_live_dashboard.py`
- Old initialization logic
- Missing recent improvements
- Dashboard provides better monitoring

## Current System
Use the current production dashboard:
```bash
python simple_live_dashboard.py
```

Features of current system:
- Real-time portfolio monitoring
- Multi-strategy signal generation
- Advanced risk management integration
- Professional execution management
- Live charts and metrics

## Historical Context
This script was an early version before the dashboard integration. It:
- Initialized trading components
- Started basic trading loop
- Lacked comprehensive monitoring
- Did not include all risk checks

## Notes
- Do NOT use this script for live trading
- Preserved for historical reference only
- See `simple_live_dashboard.py` for current implementation
- All improvements since Nov 2 are in the dashboard
