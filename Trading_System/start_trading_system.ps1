# ===============================================
# Trading System + Web Dashboard Launcher
# ===============================================

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   Trading System + Web Dashboard" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check IB Gateway
Write-Host "Make sure IB Gateway is running on port 7497" -ForegroundColor Yellow
Write-Host ""

$response = Read-Host "Is IB Gateway running? (yes/no)"
if ($response -notmatch "^(yes|y)$") {
    Write-Host "Cancelled. Start IB Gateway and try again." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Starting system..." -ForegroundColor Green
Write-Host ""

# נתיב לתיקיית הפרויקט
$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Open Web Dashboard in separate window
Write-Host "Step 1: Opening Web Dashboard..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$projectPath'; python dashboard\web_dashboard.py"
)

Start-Sleep -Seconds 3

# 2. Display message
Write-Host "   Dashboard opened in separate window" -ForegroundColor Green
Write-Host ""
Write-Host "Step 2: Starting Trading Engine..." -ForegroundColor Cyan
Write-Host ""

Start-Sleep -Seconds 1

# 3. הרצת מנוע המסחר בחלון הנוכחי
Write-Host "==================================================" -ForegroundColor Green
Write-Host "SYSTEM RUNNING" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Dashboard: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Trading Engine: Running in this window" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop: Press Ctrl+C in both windows" -ForegroundColor Yellow
Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""

# הרצת המנוע
python test_live_trading.py full
