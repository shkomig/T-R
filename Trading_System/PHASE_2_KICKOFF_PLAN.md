# Phase 2 Kickoff Plan: Architectural Refactoring
## Trading System Stabilization Project

**Phase Start Date**: 2025-11-11
**Phase Duration**: 20 business days (4 weeks)
**Phase Status**: ✅ INITIATED
**Phase 1 Status**: ✅ DEPLOYED

---

## Executive Summary

Phase 2 begins immediately following successful Phase 1 deployment. The focus shifts from critical hotfixes to architectural improvements for maintainability, testability, and scalability.

**Primary Goals**:
1. Break monolithic dashboard into modules (<300 lines each)
2. Separate production and simulation code paths
3. Implement resilience patterns (circuit breaker, retry logic)
4. Add operational capabilities (health monitoring, graceful shutdown)

---

## Phase 2 Overview

### Timeline

```
Week 1-2 (Nov 11-22): Dashboard Refactoring
Week 3 (Nov 25-29):   Code Separation & Circuit Breaker
Week 4 (Dec 2-6):     Monitoring & Operations
```

### Task Breakdown

| Task | Duration | Priority | Owner | Start | End |
|------|----------|----------|-------|-------|-----|
| 2.1 Refactor Dashboard | 8 days | HIGH | Claude AI | Nov 11 | Nov 20 |
| 2.2 Separate Prod/Sim | 3 days | HIGH | Claude AI | Nov 21 | Nov 25 |
| 2.3 Circuit Breaker | 3 days | MEDIUM | Claude AI | Nov 21 | Nov 25 |
| 2.4 Retry Logic | 2 days | MEDIUM | Claude AI | Nov 26 | Nov 27 |
| 2.5 Health Monitoring | 3 days | MEDIUM | Claude AI | Nov 28 | Dec 2 |
| 2.6 Graceful Shutdown | 2 days | MEDIUM | Claude AI | Dec 3 | Dec 4 |

---

## Task 2.1: Refactor Monolithic Dashboard

### Current State Analysis

**File**: `simple_live_dashboard.py`
- **Size**: ~1,500+ lines
- **Concerns**: Multiple responsibilities mixed together
- **Issues**: Difficult to test, hard to maintain

**Mixed Responsibilities**:
1. Signal generation and aggregation
2. UI rendering (console output)
3. Market data management
4. Trade execution logic
5. State tracking
6. Logging and monitoring

### Target Architecture

```
dashboard/
├── core/
│   ├── __init__.py
│   ├── dashboard_controller.py      # Main orchestration (200 lines)
│   ├── signal_aggregator.py         # Strategy signal collection (250 lines)
│   └── trade_executor.py            # Trade execution logic (250 lines)
├── ui/
│   ├── __init__.py
│   ├── console_display.py           # Terminal UI (200 lines)
│   └── status_renderer.py           # Status display (150 lines)
├── data/
│   ├── __init__.py
│   ├── market_data_manager.py       # Data fetching/caching (200 lines)
│   └── position_tracker.py          # Position monitoring (200 lines)
└── __init__.py
```

### Refactoring Strategy

**Phase 1: Extract Signal Aggregation** (Days 1-2)
- Create `signal_aggregator.py`
- Move signal generation logic
- Add tests

**Phase 2: Extract UI Rendering** (Day 3)
- Create `console_display.py`
- Move UI logic
- Add tests

**Phase 3: Extract Market Data** (Day 4)
- Create `market_data_manager.py`
- Move data fetching logic
- Add tests

**Phase 4: Extract Trade Execution** (Days 5-6)
- Create `trade_executor.py`
- Move execution logic
- Add tests

**Phase 5: Create Controller** (Day 7)
- Create `dashboard_controller.py`
- Orchestrate all modules
- Add integration tests

**Phase 6: Testing & Integration** (Day 8)
- Run full test suite
- Performance benchmarking
- Documentation update

---

## Task 2.2: Separate Production and Simulation Code

### Current Issues
- Production and simulation code mixed
- Risk of running simulation code in production
- 40+ test scripts in main directory

### Target Structure
```
Trading_System/
├── production/          # Only production code
│   ├── dashboard/
│   ├── execution/
│   ├── strategies/
│   └── risk_management/
├── simulation/          # Only simulation code
│   ├── price_simulator.py
│   ├── market_simulator.py
│   └── backtesting/
└── tests/              # Only test code
    ├── unit/
    ├── integration/
    └── manual/
```

### Implementation
1. Create directory structure
2. Move files to appropriate locations
3. Add runtime guards
4. Update imports
5. Add environment variable checks

---

## Task 2.3: Implement Circuit Breaker Pattern

### Purpose
Prevent cascading failures with graduated failure response.

### States
- **CLOSED**: Normal operation
- **OPEN**: Failures exceeded threshold, reject calls
- **HALF_OPEN**: Testing if service recovered

### Integration Points
- Strategy signal generation
- Broker order execution
- Market data fetching
- Risk calculation

### Implementation
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=3, timeout=300):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.timeout = timeout

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpen()

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
```

---

## Task 2.4: Retry Logic with Exponential Backoff

### Purpose
Intelligent retry mechanism for transient failures.

### Configuration
```yaml
retry_settings:
  broker_connection:
    max_attempts: 5
    base_delay: 2.0
    max_delay: 120.0

  order_placement:
    max_attempts: 3
    base_delay: 1.0
    max_delay: 30.0
```

### Implementation
```python
@retry_with_backoff(max_attempts=3, base_delay=1.0)
def place_order(symbol, quantity, price):
    # Order placement logic
    pass
```

---

## Task 2.5: Health Monitoring System

### Health Checks
1. Broker connection (latency, last successful call)
2. Strategy performance (win rate, recent failures)
3. Risk metrics (within bounds)
4. Position count (within limits)
5. Memory usage (< 80% threshold)
6. Disk space (> 10% free)

### Implementation
```python
class HealthMonitor:
    def __init__(self):
        self.health_checks = {}

    def register_check(self, name, check_func):
        self.health_checks[name] = check_func

    def run_checks(self):
        results = {}
        for name, check_func in self.health_checks.items():
            status, details = check_func()
            results[name] = {
                'status': status,  # healthy, degraded, unhealthy
                'details': details
            }
        return results
```

---

## Task 2.6: Graceful Shutdown

### Shutdown Sequence
1. Stop accepting new signals
2. Cancel all pending orders
3. Close positions (optional, configurable)
4. Disconnect broker
5. Save state
6. Close logs

### Implementation
```python
def handle_shutdown(signum, frame):
    logger.info("Graceful shutdown initiated...")

    # 1. Stop trading
    self.auto_trading = False

    # 2. Cancel orders
    self.broker.cancel_all_open_orders()

    # 3. Disconnect
    self.broker.disconnect()

    # 4. Save state
    self.save_system_state()

    sys.exit(0)
```

---

## Success Criteria

### Technical Criteria
- [ ] Dashboard modules < 300 lines each
- [ ] Production/simulation code separated
- [ ] Circuit breaker operational
- [ ] Retry logic implemented
- [ ] Health monitoring working
- [ ] Graceful shutdown functional
- [ ] All tests passing
- [ ] No performance degradation

### Quality Criteria
- [ ] Code coverage > 80%
- [ ] Module size < 300 lines average
- [ ] All APIs documented
- [ ] Integration tests passing
- [ ] Performance benchmarks met

---

## MCP Tracking

### MCPs to Create
1. **MCP-20251111-008**: Task 2.1 - Refactor Dashboard
2. **MCP-20251111-009**: Task 2.2 - Separate Prod/Sim
3. **MCP-20251111-010**: Task 2.3 - Circuit Breaker
4. **MCP-20251111-011**: Task 2.4 - Retry Logic
5. **MCP-20251111-012**: Task 2.5 - Health Monitoring
6. **MCP-20251111-013**: Task 2.6 - Graceful Shutdown

---

## Risk Management

### Identified Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|---------|------------|
| Breaking existing functionality | Medium | High | Comprehensive test suite |
| Integration issues | Medium | High | Incremental refactoring |
| Performance degradation | Low | Medium | Benchmark before/after |
| Timeline slip | Low | Medium | Already ahead of schedule |

---

## Communication Plan

### Daily Updates
- Progress tracking in MCP reports
- Update MCP index daily
- Document blockers immediately

### Weekly Milestones
- Week 1 End: Dashboard refactored
- Week 2 End: Code separated, circuit breaker done
- Week 3 End: Retry logic, health monitoring done
- Week 4 End: Graceful shutdown, documentation complete

---

## Resource Requirements

### Development
- Claude AI: Full time
- Estimated effort: 20 days

### Infrastructure
- Development environment
- Testing framework
- Version control

---

## Getting Started

### Immediate Actions (Today)

1. ✅ **Create Phase 2 Kickoff Plan** (this document)
2. **Create MCP-008** for Task 2.1
3. **Analyze Dashboard File** (`simple_live_dashboard.py`)
4. **Begin Signal Aggregation Extraction**

### This Week
- Complete dashboard refactoring foundation
- Extract signal aggregator
- Extract UI components
- Begin market data extraction

---

## Conclusion

Phase 2 is officially initiated. Work begins immediately on Task 2.1 (Dashboard Refactoring), the most critical architectural improvement.

**Status**: ✅ PHASE 2 INITIATED

**Next Actions**:
1. Create MCP-008
2. Analyze dashboard file
3. Begin refactoring

---

**Document Created**: 2025-11-11
**Phase 2 Start**: 2025-11-11
**Expected Completion**: 2025-12-06
**Status**: ✅ ACTIVE

---

*Phase 2: Architectural Refactoring - In Progress*
