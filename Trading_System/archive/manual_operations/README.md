# Manual Operations Scripts Archive

**Archived Date**: 2025-11-10
**Archived By**: MCP-20251110-004
**Total Files**: 4

## Purpose
Manual intervention scripts for emergency situations and system corrections.

## Files Archived

### Emergency Controls
- `emergency_close_all_positions.py` - Emergency position closer
- `emergency_close_all_positions_smart.py` - Smart emergency closer with validation

### Manual Adjustments
- `add_stop_loss_to_all_positions.py` - Manually add stop losses to existing positions
- `reset_peak_balance_manual.py` - Manually reset peak balance tracking

## Usage
These scripts were used for:
- Emergency position closing during testing
- Adding missing stop losses to positions
- Correcting peak balance tracking issues
- Manual system state adjustments

## Safety Warning
⚠️ **CRITICAL**: These scripts bypass normal trading system controls
- Only use in genuine emergencies
- Verify current system state before execution
- Document any manual interventions in logs
- Report issues that required manual intervention

## Notes
- Emergency controls now integrated into ExecutionManager
- Peak balance reset integrated into AdvancedRiskCalculator
- Stop loss management integrated into position sizing
- Scripts preserved for exceptional circumstances only
