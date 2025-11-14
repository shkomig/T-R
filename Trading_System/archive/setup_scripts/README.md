# Setup Scripts Archive

**Archived Date**: 2025-11-10
**Archived By**: MCP-20251110-004
**Total Files**: 2

## Purpose
Initial setup and environment configuration scripts.

## Files Archived

- `setup_live_trading.ps1` - PowerShell setup script for Windows
- `setup_live_trading.sh` - Bash setup script for Linux/Mac

## Functionality
These scripts automated:
- Python environment setup
- Dependency installation
- Configuration file creation
- Directory structure setup
- TWS API connection setup

## Why Archived
- Setup now documented in SETUP_INSTRUCTIONS.md
- Manual setup preferred for production systems
- Automated setup can mask configuration issues
- Individual setup steps better for understanding

## Current Setup Process
See current documentation:
1. `README.md` - Overview and requirements
2. `SETUP_INSTRUCTIONS.md` - Detailed setup guide
3. `TWS_API_SETUP_GUIDE.md` - TWS-specific setup

## Restoration
Scripts can be restored if automated setup is needed:
```bash
cp archive/setup_scripts/<filename> ./
```

## Notes
- Scripts preserved for reference
- May require updates for current dependencies
- Test in non-production environment first
