"""
Trading Dashboard - Web Interface
==================================

Real-time web dashboard for monitoring and controlling the trading system.

Features:
- Live position tracking
- Real-time P&L monitoring
- Strategy performance visualization
- Order management
- Risk metrics display
- Alert notifications
- System controls

Technology Stack:
- FastAPI (backend)
- Plotly Dash (charts)
- WebSockets (real-time updates)
- Bootstrap (responsive UI)

Author: Trading System
Date: October 29, 2025
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from datetime import datetime
from typing import List
import asyncio

# Import trading system components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from execution.live_engine import LiveTradingEngine
from execution.position_tracker import PositionTracker
from execution.order_manager import OrderManager
from monitoring.alert_system import AlertSystem

app = FastAPI(title="Trading System Dashboard", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global trading engine instance
trading_engine: LiveTradingEngine = None
connected_clients: List[WebSocket] = []


@app.on_event("startup")
async def startup_event():
    """Initialize trading engine on startup."""
    global trading_engine
    print("🚀 Starting Trading Dashboard...")
    # Trading engine will be initialized when user clicks "Start Trading"


@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown."""
    global trading_engine
    if trading_engine and trading_engine.is_running:
        trading_engine.stop()
    print("🛑 Trading Dashboard stopped")


@app.get("/")
async def get_dashboard():
    """Serve the main dashboard HTML."""
    return HTMLResponse(content=get_dashboard_html(), status_code=200)


@app.get("/favicon.ico")
async def favicon():
    """Return empty favicon to avoid 404."""
    return HTMLResponse(content="", status_code=204)


@app.get("/api/status")
async def get_status():
    """Get current system status."""
    if not trading_engine:
        return {
            "status": "stopped",
            "message": "Trading engine not initialized",
            "current_capital": 100000,
            "initial_capital": 100000,
            "pnl": 0,
            "signals_generated": 0,
            "orders_placed": 0,
            "positions_opened": 0,
            "positions_closed": 0,
            "market_hours": False,
            "paper_trading": True
        }
    
    try:
        stats = {
            "status": "running" if trading_engine.is_running else "stopped",
            "market_hours": getattr(trading_engine, 'is_market_hours', False),
            "paper_trading": getattr(trading_engine, 'paper_trading', True),
            "signals_generated": getattr(trading_engine, 'signals_generated', 0),
            "orders_placed": getattr(trading_engine, 'orders_placed', 0),
            "positions_opened": getattr(trading_engine, 'positions_opened', 0),
            "positions_closed": getattr(trading_engine, 'positions_closed', 0),
            "current_capital": getattr(trading_engine, 'current_capital', 100000),
            "initial_capital": getattr(trading_engine, 'initial_capital', 100000),
            "pnl": getattr(trading_engine, 'current_capital', 100000) - getattr(trading_engine, 'initial_capital', 100000)
        }
        return stats
    except Exception as e:
        print(f"Error in get_status: {e}")
        return {
            "status": "error",
            "message": str(e),
            "current_capital": 100000,
            "initial_capital": 100000,
            "pnl": 0
        }


@app.get("/api/positions")
async def get_positions():
    """Get all open positions."""
    if not trading_engine:
        return {"positions": []}
    
    try:
        if not hasattr(trading_engine, 'position_tracker') or not trading_engine.position_tracker:
            return {"positions": []}
        
        positions = []
        for pos in trading_engine.position_tracker.get_all_positions():
            positions.append(pos.to_dict())
        
        return {"positions": positions}
    except Exception as e:
        print(f"Error in get_positions: {e}")
        return {"positions": []}


@app.get("/api/orders")
async def get_orders():
    """Get recent orders."""
    if not trading_engine or not trading_engine.order_manager:
        return {"orders": []}
    
    active_orders = trading_engine.order_manager.get_active_orders()
    filled_orders = trading_engine.order_manager.get_filled_orders()
    
    return {
        "active": len(active_orders),
        "filled": len(filled_orders),
        "orders": [
            {
                "symbol": order.symbol,
                "side": order.side.value,
                "quantity": order.quantity,
                "status": order.status.value,
                "timestamp": order.created_at.isoformat()
            }
            for order in active_orders[:10]  # Last 10
        ]
    }


@app.get("/api/performance")
async def get_performance():
    """Get performance metrics."""
    if not trading_engine:
        return {"metrics": {
            "total_pnl": 0,
            "unrealized_pnl": 0,
            "realized_pnl": 0,
            "open_positions": 0,
            "winning_positions": 0,
            "losing_positions": 0,
            "total_exposure": 0,
            "commission": 0
        }}
    
    try:
        if not hasattr(trading_engine, 'position_tracker') or not trading_engine.position_tracker:
            return {"metrics": {
                "total_pnl": 0,
                "unrealized_pnl": 0,
                "realized_pnl": 0,
                "open_positions": 0,
                "winning_positions": 0,
                "losing_positions": 0,
                "total_exposure": 0,
                "commission": 0
            }}
        
        stats = trading_engine.position_tracker.get_statistics()
        
        return {
            "metrics": {
                "total_pnl": stats.get('total_pnl', 0),
                "unrealized_pnl": stats.get('total_unrealized_pnl', 0),
                "realized_pnl": stats.get('total_realized_pnl', 0),
                "open_positions": stats.get('open_positions', 0),
                "winning_positions": stats.get('winning_positions', 0),
                "losing_positions": stats.get('losing_positions', 0),
                "total_exposure": stats.get('total_exposure', 0),
                "commission": stats.get('total_commission', 0)
            }
        }
    except Exception as e:
        print(f"Error in get_performance: {e}")
        return {"metrics": {
            "total_pnl": 0,
            "unrealized_pnl": 0,
            "realized_pnl": 0,
            "open_positions": 0,
            "winning_positions": 0,
            "losing_positions": 0,
            "total_exposure": 0,
            "commission": 0
        }}


@app.post("/api/start")
async def start_trading():
    """Start the trading engine."""
    global trading_engine
    
    if trading_engine and trading_engine.is_running:
        return {"status": "error", "message": "Already running"}
    
    try:
        # Change to parent directory for config access
        import os
        original_dir = os.getcwd()
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(parent_dir)
        
        trading_engine = LiveTradingEngine()
        # Start in background task
        asyncio.create_task(run_trading_engine())
        
        return {"status": "success", "message": "Trading engine started"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/stop")
async def stop_trading():
    """Stop the trading engine."""
    global trading_engine
    
    if not trading_engine or not trading_engine.is_running:
        return {"status": "error", "message": "Not running"}
    
    try:
        trading_engine.stop()
        return {"status": "success", "message": "Trading engine stopped"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates."""
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        while True:
            # Send updates every second - always send, even without engine
            data = {
                "type": "update",
                "timestamp": datetime.now().isoformat(),
                "status": await get_status(),
                "positions": await get_positions(),
                "performance": await get_performance()
            }
            await websocket.send_json(data)
            
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        connected_clients.remove(websocket)


async def run_trading_engine():
    """Run trading engine in background."""
    global trading_engine
    if trading_engine:
        # Run in a way that allows other async tasks
        await asyncio.get_event_loop().run_in_executor(None, trading_engine.start)


def get_dashboard_html():
    """Generate the dashboard HTML."""
    return """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>מערכת מסחר אוטומטית - Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css">
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        :root {
            --primary-color: #2563eb;
            --success-color: #10b981;
            --danger-color: #ef4444;
            --warning-color: #f59e0b;
            --dark-bg: #1e293b;
            --card-bg: #334155;
        }
        
        body {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: #e2e8f0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        
        .dashboard-header {
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(10px);
            border-bottom: 2px solid var(--primary-color);
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .stat-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            margin: 0.5rem 0;
        }
        
        .stat-label {
            color: #94a3b8;
            font-size: 0.875rem;
            text-transform: uppercase;
        }
        
        .status-badge {
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
        }
        
        .status-running {
            background: var(--success-color);
            color: white;
        }
        
        .status-stopped {
            background: var(--danger-color);
            color: white;
        }
        
        .position-table {
            background: var(--card-bg);
            border-radius: 12px;
            overflow: hidden;
        }
        
        .position-table th {
            background: #475569;
            padding: 1rem;
            font-weight: 600;
        }
        
        .position-table td {
            padding: 1rem;
            border-bottom: 1px solid #475569;
        }
        
        .pnl-positive {
            color: var(--success-color);
        }
        
        .pnl-negative {
            color: var(--danger-color);
        }
        
        .control-button {
            padding: 0.75rem 2rem;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            margin: 0.5rem;
        }
        
        .btn-start {
            background: var(--success-color);
            color: white;
        }
        
        .btn-start:hover {
            background: #059669;
        }
        
        .btn-stop {
            background: var(--danger-color);
            color: white;
        }
        
        .btn-stop:hover {
            background: #dc2626;
        }
        
        .chart-container {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .alert-item {
            background: rgba(239, 68, 68, 0.1);
            border-right: 4px solid var(--danger-color);
            padding: 1rem;
            margin-bottom: 0.5rem;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="dashboard-header">
        <div class="container-fluid">
            <div class="row align-items-center">
                <div class="col-md-6">
                    <h1 class="mb-0">
                        <i class="bi bi-graph-up-arrow"></i>
                        מערכת מסחר אוטומטית
                    </h1>
                </div>
                <div class="col-md-6 text-start">
                    <span id="systemStatus" class="status-badge status-stopped">
                        <i class="bi bi-circle-fill"></i> מצב: כבוי
                    </span>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="container-fluid mt-4">
        <!-- Control Buttons -->
        <div class="row mb-4">
            <div class="col-12 text-center">
                <button class="control-button btn-start" onclick="startTrading()">
                    <i class="bi bi-play-fill"></i> הפעל מסחר
                </button>
                <button class="control-button btn-stop" onclick="stopTrading()">
                    <i class="bi bi-stop-fill"></i> עצור מסחר
                </button>
            </div>
        </div>

        <!-- Stats Row -->
        <div class="row">
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="stat-label">רווח/הפסד כולל</div>
                    <div class="stat-value" id="totalPnL">$0.00</div>
                    <small id="pnlPercent">0.00%</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="stat-label">פוזיציות פתוחות</div>
                    <div class="stat-value" id="openPositions">0</div>
                    <small><span id="winningPos">0</span> רווחיות | <span id="losingPos">0</span> הפסדיות</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="stat-label">סיגנלים היום</div>
                    <div class="stat-value" id="signalsToday">0</div>
                    <small>פקודות: <span id="ordersPlaced">0</span></small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="stat-label">חשיפה כוללת</div>
                    <div class="stat-value" id="totalExposure">$0.00</div>
                    <small id="capitalUsed">0%</small>
                </div>
            </div>
        </div>

        <!-- Charts Row -->
        <div class="row mt-4">
            <div class="col-md-8">
                <div class="chart-container">
                    <h4>עקומת הון (Equity Curve)</h4>
                    <div id="equityChart"></div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="chart-container">
                    <h4>התראות אחרונות</h4>
                    <div id="alertsList" style="max-height: 400px; overflow-y: auto;">
                        <p class="text-muted">אין התראות</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Positions Table -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="chart-container">
                    <h4>פוזיציות פתוחות</h4>
                    <table class="table position-table">
                        <thead>
                            <tr>
                                <th>מניה</th>
                                <th>צד</th>
                                <th>כמות</th>
                                <th>מחיר כניסה</th>
                                <th>מחיר נוכחי</th>
                                <th>רווח/הפסד</th>
                                <th>אחוז</th>
                                <th>פעולות</th>
                            </tr>
                        </thead>
                        <tbody id="positionsTable">
                            <tr>
                                <td colspan="8" class="text-center text-muted">אין פוזיציות פתוחות</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        console.log('🚀 Dashboard JavaScript loaded');
        
        let ws = null;
        let equityData = [];
        
        // Connect to WebSocket
        function connectWebSocket() {
            console.log('🔌 Attempting WebSocket connection...');
            ws = new WebSocket('ws://localhost:8000/ws');
            
            ws.onopen = () => {
                console.log('✅ Connected to trading system');
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            ws.onclose = () => {
                console.log('❌ Disconnected from trading system');
                setTimeout(connectWebSocket, 3000); // Reconnect
            };
        }
        
        // Update dashboard with real-time data
        function updateDashboard(data) {
            if (!data) return;
            
            console.log('📊 Received data:', data);
            
            const status = data.status || {};
            const positions = data.positions?.positions || [];
            const performance = data.performance?.metrics || {};
            
            console.log('Status:', status);
            console.log('Performance:', performance);
            
            // Update status badge
            const statusBadge = document.getElementById('systemStatus');
            if (status.status === 'running') {
                statusBadge.className = 'status-badge status-running';
                statusBadge.innerHTML = '<i class="bi bi-circle-fill"></i> מצב: פועל';
            } else {
                statusBadge.className = 'status-badge status-stopped';
                statusBadge.innerHTML = '<i class="bi bi-circle-fill"></i> מצב: כבוי';
            }
            
            // Update stats with error handling
            try {
                const pnl = status.pnl || 0;
                const pnlPercent = status.initial_capital ? (pnl / status.initial_capital * 100) : 0;
                
                const totalPnLEl = document.getElementById('totalPnL');
                if (totalPnLEl) {
                    totalPnLEl.textContent = `$${pnl.toFixed(2)}`;
                    totalPnLEl.className = `stat-value ${pnl >= 0 ? 'pnl-positive' : 'pnl-negative'}`;
                }
                
                const pnlPercentEl = document.getElementById('pnlPercent');
                if (pnlPercentEl) pnlPercentEl.textContent = `${pnlPercent.toFixed(2)}%`;
                
                const openPosEl = document.getElementById('openPositions');
                if (openPosEl) openPosEl.textContent = performance.open_positions || 0;
                
                const winningPosEl = document.getElementById('winningPos');
                if (winningPosEl) winningPosEl.textContent = performance.winning_positions || 0;
                
                const losingPosEl = document.getElementById('losingPos');
                if (losingPosEl) losingPosEl.textContent = performance.losing_positions || 0;
                
                const signalsEl = document.getElementById('signalsToday');
                if (signalsEl) signalsEl.textContent = status.signals_generated || 0;
                
                const ordersEl = document.getElementById('ordersPlaced');
                if (ordersEl) ordersEl.textContent = status.orders_placed || 0;
                
                const exposureEl = document.getElementById('totalExposure');
                if (exposureEl) exposureEl.textContent = `$${(performance.total_exposure || 0).toFixed(2)}`;
                
                const capitalUsed = status.current_capital ? (performance.total_exposure / status.current_capital * 100) : 0;
                const capitalUsedEl = document.getElementById('capitalUsed');
                if (capitalUsedEl) capitalUsedEl.textContent = `${capitalUsed.toFixed(1)}% בשימוש`;
                
                console.log('✅ Stats updated successfully');
            } catch (error) {
                console.error('❌ Error updating stats:', error);
            }
            
            // Update positions table
            updatePositionsTable(positions);
            
            // Update equity chart
            equityData.push({
                time: new Date(data.timestamp),
                value: status.current_capital || 100000
            });
            updateEquityChart();
        }
        
        // Update positions table
        function updatePositionsTable(positions) {
            const tbody = document.getElementById('positionsTable');
            
            if (positions.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">אין פוזיציות פתוחות</td></tr>';
                return;
            }
            
            tbody.innerHTML = positions.map(pos => `
                <tr>
                    <td><strong>${pos.symbol}</strong></td>
                    <td>${pos.side}</td>
                    <td>${pos.quantity}</td>
                    <td>$${pos.entry_price.toFixed(2)}</td>
                    <td>$${pos.current_price.toFixed(2)}</td>
                    <td class="${pos.unrealized_pnl >= 0 ? 'pnl-positive' : 'pnl-negative'}">
                        $${pos.unrealized_pnl.toFixed(2)}
                    </td>
                    <td class="${pos.unrealized_pnl_percent >= 0 ? 'pnl-positive' : 'pnl-negative'}">
                        ${pos.unrealized_pnl_percent.toFixed(2)}%
                    </td>
                    <td>
                        <button class="btn btn-sm btn-danger" onclick="closePosition('${pos.symbol}')">
                            <i class="bi bi-x-circle"></i> סגור
                        </button>
                    </td>
                </tr>
            `).join('');
        }
        
        // Update equity chart
        function updateEquityChart() {
            const trace = {
                x: equityData.map(d => d.time),
                y: equityData.map(d => d.value),
                type: 'scatter',
                mode: 'lines',
                line: {color: '#10b981', width: 2},
                fill: 'tozeroy'
            };
            
            const layout = {
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: {color: '#e2e8f0'},
                xaxis: {gridcolor: '#475569'},
                yaxis: {gridcolor: '#475569'},
                margin: {t: 20, b: 40, l: 60, r: 20}
            };
            
            Plotly.newPlot('equityChart', [trace], layout, {responsive: true});
        }
        
        // Control functions
        async function startTrading() {
            const response = await fetch('/api/start', {method: 'POST'});
            const result = await response.json();
            alert(result.message);
        }
        
        async function stopTrading() {
            const response = await fetch('/api/stop', {method: 'POST'});
            const result = await response.json();
            alert(result.message);
        }
        
        async function closePosition(symbol) {
            if (confirm(`האם לסגור את הפוזיציה ב-${symbol}?`)) {
                // Implement close position API call
                alert('סגירת פוזיציה - בפיתוח');
            }
        }
        
        // Initialize
        connectWebSocket();
        
        // Initial empty chart
        updateEquityChart();
    </script>
</body>
</html>
    """


if __name__ == "__main__":
    print("="*60)
    print("🚀 Starting Trading System Dashboard")
    print("="*60)
    print("\n📊 Dashboard URL: http://localhost:8000")
    print("📡 WebSocket URL: ws://localhost:8000/ws")
    print("\n⚠️  Make sure IB Gateway is running on port 7497")
    print("\nPress Ctrl+C to stop\n")
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
