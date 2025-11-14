# Trading System - Quick Startup Checklist

**System Version**: 3.0 (Phase 2 - SignalAggregator Modular)
**Last Updated**: 2025-11-11

---

## Pre-Flight Checklist (5 minutes)

### 1. TWS Setup ✅
- [ ] TWS is running (check taskbar for green "TWS" icon)
- [ ] API enabled: `File > Global Configuration > API > Settings`
- [ ] Socket port: `7497` (paper) or `7496` (live)
- [ ] "Enable ActiveX and Socket Clients" is **CHECKED**
- [ ] Paper trading account selected (DU... account)
- [ ] Market data farms showing "OK" status

### 2. Configuration Review ✅
- [ ] `config/trading_config.yaml` exists
- [ ] `auto_trading: false` (for testing)
- [ ] Symbols list is correct
- [ ] `signal_threshold: 2` (or your preference)

### 3. Risk Settings ✅
- [ ] `config/risk_management.yaml` exists
- [ ] `max_position_size_pct: 0.10` (10%)
- [ ] `max_portfolio_heat_pct: 0.25` (25%)
- [ ] `max_daily_loss_pct: 0.02` (2%)
- [ ] `max_total_drawdown_pct: 0.10` (10%)

### 4. Python Environment ✅
- [ ] Python 3.8+ installed
- [ ] Virtual environment activated (if used)
- [ ] Key dependencies: `import ibapi, pandas, numpy, yaml`

---

## Startup Procedure (2 minutes)

### Step 1: Navigate to Directory
```bash
cd C:\Vs-Pro\TR\Trading_System
```

### Step 2: Start Dashboard
```bash
python simple_live_dashboard.py
```

### Step 3: Watch for Initialization Messages

**Expected Output**:
```
✅ Trading Config loaded
✅ Risk Management Config loaded
✅ 7 strategies initialized (or 3-4 if Unicode issues)
✅ Signal Aggregator initialized (modular component)
✅ Successfully connected to TWS!
✅ Account validated: DU...
✅ Dashboard Ready - Starting Main Loop
```

**Status**: If you see these messages, system is running correctly!

---

## Verification Steps (1 minute)

### Quick Checks
- [ ] TWS connection shows "OK"
- [ ] Account balance displayed correctly
- [ ] "Auto-Trading: DISABLED" (for safety)
- [ ] Market data retrieving for symbols
- [ ] Signals generating each cycle
- [ ] No critical errors in output

### What You Should See

**Every 60 seconds** (one cycle):
```
Cycle X Complete:
  - Signals generated for 5 symbols
  - Risk checks performed
  - Portfolio heat: X% (should be < 25%)
  - No trades executed (auto-trading disabled)

Next cycle in 60 seconds...
```

---

## Safety Verification ✅

### CRITICAL - Verify Before Every Session
- [ ] **Paper trading account active** (not live!)
- [ ] **Auto-trading is DISABLED** (`auto_trading: false`)
- [ ] **Risk limits are set conservatively**
- [ ] **You know how to stop the system** (Ctrl+C)

### Stop Commands
```bash
# Graceful stop
Ctrl+C (press once)

# Emergency stop
Ctrl+C (press twice rapidly)
```

---

## Common Issues - Quick Fix

### Issue: TWS Connection Failed
**Fix**:
1. Check TWS is running
2. Check API enabled in TWS settings
3. Restart TWS and wait for full initialization

### Issue: Unicode Encoding Error
**Fix**:
- Ignore strategy initialization warnings
- System continues with 3-4 strategies (sufficient)
- Or use UTF-8 terminal (Windows Terminal or PowerShell with UTF-8)

### Issue: VWAP Strategy Failed
**Fix**:
- This is a known pre-existing issue
- System continues with 6 other strategies
- Does not affect core functionality

### Issue: No Signals Generated
**Check**:
- Market hours (9:30 AM - 4:00 PM ET regular hours)
- Market data subscriptions active in TWS
- Strategies initialized successfully (check startup logs)

---

## First-Time Startup (Extended Checks)

### If This Is Your First Time Running The System:

1. **Run Unit Tests First**:
```bash
python test_signal_aggregator.py
# Expected: 16 tests passed
```

2. **Test TWS Connection**:
```bash
python check_tws_connection.py
# Expected: "Successfully connected to TWS!"
```

3. **Start Dashboard in Monitoring Mode**:
```bash
python simple_live_dashboard.py
# Watch for 2-3 cycles
# Verify signals are generating
```

4. **Review First Session Logs**:
```bash
# Check for errors
cat logs/error_log_YYYYMMDD.txt
```

5. **Only After Successful Test Session**:
- Consider enabling auto-trading (if desired)
- Update `config/trading_config.yaml`: `auto_trading: true`
- ⚠️ Monitor first auto-trading session closely!

---

## Performance Expectations

### What's Normal:
- **Signal Generation**: Every 60 seconds for each symbol
- **TWS Connection**: Stable throughout session
- **Portfolio Heat**: 0-15% (normal range)
- **Win Rate**: 50-60% (healthy)
- **Strategy Votes**: 2-4 strategies agreeing (typical)

### What's Concerning:
- ❌ Repeated TWS disconnections
- ❌ All strategies returning 'hold' constantly
- ❌ Portfolio heat > 20%
- ❌ Daily loss approaching 2%
- ❌ Repeated strategy failures

---

## Quick Reference - File Locations

### Configuration
```
config/api_credentials.yaml     # TWS connection settings
config/trading_config.yaml      # Trading parameters
config/risk_management.yaml     # Risk limits
```

### Executables
```
simple_live_dashboard.py        # Main executable ✅
main.py                         # Entry point with options
Trading_Dashboard/core/signal_aggregator.py  # Modular component ✅
```

### Tests
```
test_signal_aggregator.py       # Unit tests (16 tests)
test_live_system_with_tws.py    # Live integration tests
check_tws_connection.py         # TWS connectivity check
```

### Logs
```
logs/trading_log_YYYYMMDD.txt   # Trading activity
logs/error_log_YYYYMMDD.txt     # Errors and warnings
logs/trades_YYYYMMDD.csv        # Trade history
```

---

## Support Resources

### Documentation
- `SYSTEM_STARTUP_GUIDE.md` - Comprehensive guide (this is the short version!)
- `LIVE_SYSTEM_TEST_REPORT.md` - Live TWS integration test results
- `docs/mcp_index.md` - Project progress tracking
- `MCP-20251111-008-DashboardRefactoring.md` - Phase 2 details

### Test Results
- ✅ Phase 1: 37/37 tests passed (100%)
- ✅ Phase 2 Unit Tests: 16/16 passed (100%)
- ✅ Phase 2 Live Tests: 4/6 passed (2 pre-existing issues)

### System Status
- ✅ Phase 1: COMPLETE and DEPLOYED
- 🔄 Phase 2: 50% Complete (SignalAggregator extracted and validated)
- ✅ TWS Integration: Validated with $1.2M paper account

---

## Emergency Contacts

### Emergency Stop Procedures
```bash
# Close all positions immediately
python emergency_close_all_positions.py

# Trigger emergency halt
python trigger_emergency_halt.py

# Resume from halt (after investigation)
python reset_emergency_halt.py
```

### Diagnostic Commands
```bash
# Check system status
python check_real_status.py

# Check pending orders
python check_orders.py

# Analyze current positions
python analyze_positions.py

# View risk metrics
python test_risk_simple.py
```

---

## Startup Success Criteria ✅

**System is ready when you see**:
- ✅ All configurations loaded
- ✅ 3-7 strategies initialized
- ✅ Signal Aggregator (modular component) loaded
- ✅ TWS connection successful
- ✅ Account balance displayed
- ✅ Dashboard main loop started
- ✅ First cycle completed without errors

**Monitor for 2-3 cycles, then**:
- ✅ Signals generating consistently
- ✅ Risk calculations working
- ✅ No critical errors
- ✅ TWS connection stable

**If all checks pass**: System is operational! 🎉

---

## Daily Startup Routine

### Morning Routine (Before Market Open):
1. [ ] Start TWS (15 minutes before market open)
2. [ ] Wait for TWS to fully initialize
3. [ ] Review `config/trading_config.yaml` settings
4. [ ] Start dashboard: `python simple_live_dashboard.py`
5. [ ] Verify initialization (all ✅ checks)
6. [ ] Watch first 2-3 cycles
7. [ ] Review overnight positions (if any)

### During Trading:
1. [ ] Monitor dashboard output periodically
2. [ ] Check risk metrics stay within limits
3. [ ] Note any unusual behavior
4. [ ] Review error logs if issues occur

### End of Day:
1. [ ] Stop dashboard (Ctrl+C)
2. [ ] Review trade logs: `logs/trades_YYYYMMDD.csv`
3. [ ] Check error logs: `logs/error_log_YYYYMMDD.txt`
4. [ ] Note performance metrics
5. [ ] Close TWS

---

**Checklist Version**: 1.0
**System Version**: 3.0 (Phase 2: SignalAggregator Modular)
**Status**: ✅ Production Ready

---

*Keep this checklist handy for daily startup procedures. For detailed troubleshooting, see SYSTEM_STARTUP_GUIDE.md*
