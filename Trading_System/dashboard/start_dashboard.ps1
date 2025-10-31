# ===============================================
# הפעלת Web Dashboard בלבד (מצב ניטור)
# ===============================================

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   Web Dashboard - מצב ניטור" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 הדשבורד יוצג עם ערכי ברירת מחדל" -ForegroundColor Yellow
Write-Host "💡 כדי לראות נתונים אמיתיים, הרץ את המנוע במקביל" -ForegroundColor Yellow
Write-Host ""

$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "🚀 מפעיל דשבורד..." -ForegroundColor Green
Write-Host ""

cd $projectPath\dashboard
python web_dashboard.py
