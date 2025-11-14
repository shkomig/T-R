# Simulation Scripts Archive

**Archived Date**: 2025-11-10
**Archived By**: MCP-20251110-004
**Total Files**: 2

## Purpose
Simulation and demonstration scripts used during development.

## Files Archived

- `professional_simulation.py` - Professional trading system simulation with random signals
- `demo_advanced_features.py` - Demo of advanced system features

## Critical Issues

### professional_simulation.py
⚠️ **CONTAINS RANDOM SIGNAL GENERATION**
- Used `random.choice()` to generate trading signals
- Was NEVER intended for production use
- Kept for reference of what NOT to do
- See MCP-20251110-001 for removal of similar code from production

### demo_advanced_features.py
- Feature demonstration script
- Used for testing and presentations
- Not connected to real broker

## Notes
- These files demonstrate the importance of clear separation between test and production code
- Random signal generation has been completely removed from production code (Task 1.1)
- Professional simulation approach documented in backtesting/ module
- Do NOT use these files as templates for new code

## Lessons Learned
1. Never use random signals in production code
2. Clearly separate simulation from live trading
3. Always use proper strategy-based signals
4. Test thoroughly before live deployment
