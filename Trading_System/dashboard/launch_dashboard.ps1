# Quick Start - Dashboard Launcher
# ==================================
# Run this script to quickly start your preferred dashboard

# Display menu
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "   📊 Trading System Dashboard Launcher    " -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

Write-Host "Select Dashboard Type:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 🌐 Web Dashboard (Recommended)" -ForegroundColor Green
Write-Host "   - Professional web interface" -ForegroundColor Gray
Write-Host "   - Real-time updates via WebSocket" -ForegroundColor Gray
Write-Host "   - Access from any device" -ForegroundColor Gray
Write-Host ""

Write-Host "2. 📓 Jupyter Notebook Dashboard" -ForegroundColor Blue
Write-Host "   - Interactive analysis environment" -ForegroundColor Gray
Write-Host "   - Full Python flexibility" -ForegroundColor Gray
Write-Host "   - Perfect for strategy development" -ForegroundColor Gray
Write-Host ""

Write-Host "3. 💻 CLI Dashboard" -ForegroundColor Magenta
Write-Host "   - Fast terminal interface" -ForegroundColor Gray
Write-Host "   - Minimal resource usage" -ForegroundColor Gray
Write-Host "   - Great for SSH/remote access" -ForegroundColor Gray
Write-Host ""

Write-Host "4. 🚀 Install Dashboard Requirements" -ForegroundColor Yellow
Write-Host ""
Write-Host "Q. Quit" -ForegroundColor Red
Write-Host ""

$choice = Read-Host "Enter your choice (1-4, Q)"

switch ($choice) {
    "1" {
        Write-Host "`n🌐 Starting Web Dashboard..." -ForegroundColor Green
        Write-Host "Dashboard will be available at: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Yellow
        
        # Check if already in dashboard directory
        if (Test-Path ".\web_dashboard.py") {
            python web_dashboard.py
        } elseif (Test-Path ".\dashboard\web_dashboard.py") {
            cd dashboard
            python web_dashboard.py
            cd ..
        } else {
            Write-Host "❌ Error: web_dashboard.py not found!" -ForegroundColor Red
            Write-Host "Make sure you're in the Trading_System directory" -ForegroundColor Yellow
        }
    }
    
    "2" {
        Write-Host "`n📓 Starting Jupyter Notebook Dashboard..." -ForegroundColor Blue
        Write-Host "Opening notebook_dashboard.ipynb..." -ForegroundColor Cyan
        Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Yellow
        
        if (Test-Path ".\notebook_dashboard.ipynb") {
            jupyter notebook notebook_dashboard.ipynb
        } elseif (Test-Path ".\dashboard\notebook_dashboard.ipynb") {
            cd dashboard
            jupyter notebook notebook_dashboard.ipynb
            cd ..
        } else {
            Write-Host "❌ Error: notebook_dashboard.ipynb not found!" -ForegroundColor Red
        }
    }
    
    "3" {
        Write-Host "`n💻 Starting CLI Dashboard..." -ForegroundColor Magenta
        Write-Host "Use menu to navigate" -ForegroundColor Cyan
        Write-Host ""
        
        if (Test-Path ".\cli_dashboard.py") {
            python cli_dashboard.py
        } elseif (Test-Path ".\dashboard\cli_dashboard.py") {
            cd dashboard
            python cli_dashboard.py
            cd ..
        } else {
            Write-Host "❌ Error: cli_dashboard.py not found!" -ForegroundColor Red
        }
    }
    
    "4" {
        Write-Host "`n🚀 Installing Dashboard Requirements..." -ForegroundColor Yellow
        
        if (Test-Path ".\requirements.txt") {
            pip install -r requirements.txt
        } elseif (Test-Path ".\dashboard\requirements.txt") {
            pip install -r dashboard\requirements.txt
        } else {
            Write-Host "❌ Error: requirements.txt not found!" -ForegroundColor Red
            Write-Host "Trying to install common packages..." -ForegroundColor Yellow
            pip install fastapi uvicorn plotly pandas jupyter ipywidgets rich
        }
        
        Write-Host "`n✅ Installation complete!" -ForegroundColor Green
        Write-Host "Run this script again to launch a dashboard." -ForegroundColor Cyan
    }
    
    "Q" {
        Write-Host "`n👋 Goodbye!" -ForegroundColor Yellow
        exit
    }
    
    default {
        Write-Host "`n❌ Invalid choice. Please run the script again." -ForegroundColor Red
    }
}

Write-Host ""
