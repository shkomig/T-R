# Test Scripts Archive

**Archived Date**: 2025-11-10
**Archived By**: MCP-20251110-004
**Total Files**: 17

## Purpose
This directory contains all test scripts that were used during development and debugging. These files are archived to keep the project root clean while preserving them for reference.

## Files Archived

### Strategy Tests
- `test_advanced_strategies.py` - Tests for advanced trading strategies
- `test_charts.py` - Chart generation tests
- `test_live_professional.py` - Live trading professional mode tests
- `test_professional_execution.py` - Professional execution manager tests
- `test_simple_professional.py` - Simple professional mode tests

### Risk Management Tests
- `test_risk_management.py` - Comprehensive risk management tests
- `test_risk_simple.py` - Simple risk calculation tests
- `test_risk_settings.py` - Risk settings validation tests
- `test_live_risk.py` - Live risk management tests
- `test_enhanced_position_sizer.py` - Position sizing tests

### Connection & Infrastructure Tests
- `test_tws_connection.py` - TWS API connection tests
- `test_client_ids.py` - Client ID management tests
- `test_client_999.py` - Specific client 999 tests
- `test_market_data.py` - Market data fetching tests

### System Tests
- `test_config_load.py` - Configuration loading tests
- `test_path.py` - Path resolution tests
- `test_reset_peak_balance.py` - Peak balance reset tests

## Restoration
To restore any test file:
```bash
cp archive/test_scripts/<filename> ./
```

## Notes
- All tests should be migrated to a proper test suite (pytest) in Phase 3
- These files are preserved for reference but are not part of production code
- Some tests may be outdated and require updates to run successfully
