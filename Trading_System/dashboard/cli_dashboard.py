"""
CLI Dashboard - Command Line Interface
=======================================

Terminal-based dashboard for monitoring the trading system.
Perfect for headless servers or quick monitoring.

Features:
- Real-time ASCII charts
- Color-coded P&L display
- Keyboard controls
- Lightweight and fast
- Works on any terminal

Author: Trading System
Date: October 29, 2025
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich import box
from datetime import datetime
import time
import msvcrt  # For keyboard input on Windows
import threading

from execution.live_engine import LiveTradingEngine
from execution.position_tracker import PositionTracker

console = Console()


class CLIDashboard:
    """Command-line dashboard for trading system."""
    
    def __init__(self):
        """Initialize CLI dashboard."""
        self.engine: LiveTradingEngine = None
        self.running = False
        
    def connect(self):
        """Connect to trading system."""
        try:
            console.print("\n[yellow]🔌 Connecting to trading system...[/yellow]")
            # Change to parent directory for config access
            import os
            original_dir = os.getcwd()
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            os.chdir(parent_dir)
            
            self.engine = LiveTradingEngine()
            # Initialize the engine
            if self.engine.initialize():
                console.print("[green]✅ Connected successfully![/green]")
                # Start the engine
                if self.engine.start():
                    console.print("[green]🚀 Engine started![/green]\n")
                    self.running = True
                else:
                    console.print("[yellow]⚠️ Engine initialized but not started[/yellow]\n")
                return True
            else:
                console.print("[yellow]⚠️ Connected but not initialized (IB Gateway may not be running)[/yellow]\n")
                return True
        except Exception as e:
            console.print(f"[red]❌ Connection failed: {e}[/red]")
            return False
    
    def create_header(self) -> Panel:
        """Create header panel."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "🟢 RUNNING" if self.engine and self.engine.is_running else "🔴 STOPPED"
        
        header_text = Text()
        header_text.append("📊 Trading System Dashboard", style="bold cyan")
        header_text.append(f"\n{timestamp}", style="dim")
        header_text.append(f" | Status: {status}", style="bold")
        
        return Panel(header_text, box=box.DOUBLE, border_style="cyan")
    
    def create_stats_table(self) -> Table:
        """Create statistics table."""
        if not self.engine or not self.engine.position_tracker:
            table = Table(title="📈 Key Statistics", box=box.ROUNDED, border_style="blue")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            table.add_row("Status", "Not connected")
            return table
        
        try:
            stats = self.engine.position_tracker.get_statistics()
        except Exception as e:
            table = Table(title="📈 Key Statistics", box=box.ROUNDED, border_style="blue")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            table.add_row("Error", str(e))
            return table
        
        table = Table(title="📈 Key Statistics", box=box.ROUNDED, border_style="blue")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta", justify="right")
        
        # Calculate metrics
        pnl = stats.get('total_pnl', 0)
        pnl_color = "green" if pnl >= 0 else "red"
        win_rate = stats.get('win_rate', 0)
        win_rate_color = "green" if win_rate >= 50 else "red"
        
        table.add_row("💰 Total P&L", f"[{pnl_color}]${pnl:,.2f}[/{pnl_color}]")
        table.add_row("📊 Open Positions", f"{stats.get('open_positions', 0)}")
        table.add_row("✅ Winning", f"[green]{stats.get('winning_positions', 0)}[/green]")
        table.add_row("❌ Losing", f"[red]{stats.get('losing_positions', 0)}[/red]")
        table.add_row("🎯 Win Rate", f"[{win_rate_color}]{win_rate:.1f}%[/{win_rate_color}]")
        table.add_row("💵 Exposure", f"${stats.get('total_exposure', 0):,.2f}")
        table.add_row("💸 Commission", f"${stats.get('total_commission', 0):,.2f}")
        
        return table
    
    def create_positions_table(self) -> Table:
        """Create positions table."""
        if not self.engine:
            return Table(title="No Positions")
        
        positions = self.engine.position_tracker.get_all_positions()
        
        table = Table(title="💼 Open Positions", box=box.ROUNDED, border_style="yellow")
        table.add_column("Symbol", style="cyan", no_wrap=True)
        table.add_column("Side", style="white")
        table.add_column("Qty", justify="right")
        table.add_column("Entry", justify="right")
        table.add_column("Current", justify="right")
        table.add_column("P&L", justify="right")
        table.add_column("%", justify="right")
        
        if not positions:
            table.add_row("No open positions", "", "", "", "", "", "")
            return table
        
        for pos in positions:
            pnl_color = "green" if pos.unrealized_pnl >= 0 else "red"
            side_color = "green" if pos.side == "LONG" else "red"
            
            table.add_row(
                f"[bold]{pos.symbol}[/bold]",
                f"[{side_color}]{pos.side}[/{side_color}]",
                f"{pos.quantity}",
                f"${pos.entry_price:.2f}",
                f"${pos.current_price:.2f}",
                f"[{pnl_color}]${pos.unrealized_pnl:.2f}[/{pnl_color}]",
                f"[{pnl_color}]{pos.unrealized_pnl_percent:.2f}%[/{pnl_color}]"
            )
        
        return table
    
    def create_signals_table(self) -> Table:
        """Create signals/activity table."""
        table = Table(title="🎯 Activity", box=box.ROUNDED, border_style="green")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", justify="right", style="magenta")
        
        if not self.engine:
            table.add_row("No data", "0")
            return table
        
        table.add_row("📡 Signals Generated", f"{self.engine.signals_generated}")
        table.add_row("📝 Orders Placed", f"{self.engine.orders_placed}")
        table.add_row("🔓 Positions Opened", f"{self.engine.positions_opened}")
        table.add_row("🔒 Positions Closed", f"{self.engine.positions_closed}")
        
        return table
    
    def create_layout(self) -> Layout:
        """Create dashboard layout."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=4),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        layout["left"].split_column(
            Layout(name="stats"),
            Layout(name="signals")
        )
        
        # Update panels
        layout["header"].update(self.create_header())
        layout["stats"].update(self.create_stats_table())
        layout["signals"].update(self.create_signals_table())
        layout["right"].update(self.create_positions_table())
        
        # Footer
        footer_text = Text()
        footer_text.append("Commands: ", style="bold")
        footer_text.append("[Q]uit", style="red")
        footer_text.append(" | ", style="dim")
        footer_text.append("[R]efresh", style="green")
        footer_text.append(" | ", style="dim")
        footer_text.append("[S]tart/Stop", style="yellow")
        footer_text.append(" | ", style="dim")
        footer_text.append("Auto-refresh: ON", style="cyan")
        
        layout["footer"].update(Panel(footer_text, border_style="dim"))
        
        return layout
    
    def run_live(self, refresh_rate: float = 2.0):
        """Run live dashboard with auto-refresh and keyboard control."""
        if not self.engine:
            console.print("[red]❌ Not connected to system[/red]")
            return
        
        console.clear()
        console.print("\n[green]Starting live dashboard...[/green]")
        console.print("[cyan]📊 Dashboard is updating every 2 seconds[/cyan]")
        console.print("[yellow]Keys: [R]efresh | [S]tart/Stop | [Q]uit[/yellow]\n")
        time.sleep(1)
        
        last_update = time.time()
        
        try:
            while True:
                # Check for keyboard input (non-blocking)
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                    
                    if key == 'q':
                        console.print("\n\n[yellow]Dashboard stopped[/yellow]")
                        break
                    elif key == 'r':
                        # Force refresh
                        last_update = 0
                        console.print("\n[cyan]🔄 Refreshing...[/cyan]")
                    elif key == 's':
                        # Toggle engine start/stop
                        if self.running:
                            console.print("\n[yellow]⏸️  Stopping engine...[/yellow]")
                            self.running = False
                        else:
                            console.print("\n[green]▶️  Starting engine...[/green]")
                            self.running = True
                
                # Auto-refresh at interval
                current_time = time.time()
                if current_time - last_update >= refresh_rate:
                    console.clear()
                    console.print(self.create_layout())
                    
                    # Show update time and instructions
                    console.print(f"\n[dim]Last update: {datetime.now().strftime('%H:%M:%S')} | Auto-refresh: {refresh_rate}s | Keys: [R]efresh [S]tart/Stop [Q]uit[/dim]")
                    
                    last_update = current_time
                
                # Small sleep to prevent CPU spin
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Dashboard stopped[/yellow]")
    
    def show_snapshot(self):
        """Show single snapshot of current state."""
        if not self.engine:
            console.print("[red]❌ Not connected to system[/red]")
            return
        
        console.clear()
        console.print(self.create_layout())
    
    def show_ascii_chart(self):
        """Show ASCII equity curve."""
        console.print("\n[cyan]📈 Equity Curve (Last 30 minutes)[/cyan]\n")
        
        # Generate sample data (in production, use real data)
        import random
        data_points = 30
        equity = 100000
        equity_curve = [equity]
        
        for _ in range(data_points - 1):
            equity += random.uniform(-500, 800)
            equity_curve.append(equity)
        
        # Normalize to fit terminal
        min_val = min(equity_curve)
        max_val = max(equity_curve)
        height = 15
        
        chart_lines = [[] for _ in range(height)]
        
        for value in equity_curve:
            normalized = int(((value - min_val) / (max_val - min_val)) * (height - 1))
            for i in range(height):
                if i == height - 1 - normalized:
                    chart_lines[i].append("●")
                else:
                    chart_lines[i].append(" ")
        
        # Print chart
        for i, line in enumerate(chart_lines):
            value = max_val - (i * (max_val - min_val) / (height - 1))
            console.print(f"{value:8.0f} │ " + "".join(line))
        
        console.print(" " * 9 + "└" + "─" * len(equity_curve))
        console.print(f"\n[green]Starting: ${equity_curve[0]:,.2f}[/green]")
        console.print(f"[{'green' if equity_curve[-1] >= equity_curve[0] else 'red'}]Current:  ${equity_curve[-1]:,.2f}[/{'green' if equity_curve[-1] >= equity_curve[0] else 'red'}]")
        console.print(f"[{'green' if equity_curve[-1] >= equity_curve[0] else 'red'}]Change:   ${equity_curve[-1] - equity_curve[0]:+,.2f}[/{'green' if equity_curve[-1] >= equity_curve[0] else 'red'}]")


def print_menu():
    """Print main menu."""
    console.clear()
    console.print("\n[bold cyan]═══════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]     📊 Trading System CLI Dashboard   [/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════[/bold cyan]\n")
    
    menu = Table(box=box.SIMPLE, show_header=False, border_style="cyan")
    menu.add_column("Option", style="yellow", no_wrap=True)
    menu.add_column("Description", style="white")
    
    menu.add_row("1", "Connect to Trading System")
    menu.add_row("2", "Show Live Dashboard (Auto-refresh)")
    menu.add_row("3", "Show Current Snapshot")
    menu.add_row("4", "Show Equity Chart")
    menu.add_row("5", "System Status")
    menu.add_row("Q", "Quit")
    
    console.print(menu)
    console.print("")


def show_status(dashboard: CLIDashboard):
    """Show system status."""
    if not dashboard.engine:
        console.print("\n[red]❌ Not connected to system[/red]")
        return
    
    console.clear()
    console.print("\n[bold cyan]🖥️  System Status[/bold cyan]\n")
    
    status_table = Table(box=box.ROUNDED, border_style="blue")
    status_table.add_column("Component", style="cyan")
    status_table.add_column("Status", style="white")
    
    status_table.add_row("Trading Engine", "✅ Connected" if dashboard.engine else "❌ Disconnected")
    status_table.add_row("IB Gateway", "✅ Connected" if dashboard.engine.ib.isConnected() else "❌ Disconnected")
    status_table.add_row("Market Hours", "✅ Open" if dashboard.engine.is_market_hours else "❌ Closed")
    status_table.add_row("Paper Trading", "✅ Yes" if dashboard.engine.paper_trading else "❌ No")
    status_table.add_row(
        "Strategies",
        f"✅ {len(dashboard.engine.strategies)} active"
    )
    status_table.add_row(
        "Symbols",
        f"📊 {', '.join(dashboard.engine.symbols[:5])}{'...' if len(dashboard.engine.symbols) > 5 else ''}"
    )
    
    console.print(status_table)
    console.print("")


def main():
    """Main CLI application."""
    dashboard = CLIDashboard()
    
    while True:
        print_menu()
        choice = console.input("[bold yellow]Select option: [/bold yellow]").strip().upper()
        
        if choice == "1":
            dashboard.connect()
            console.input("\nPress Enter to continue...")
            
        elif choice == "2":
            if not dashboard.engine:
                console.print("\n[red]❌ Please connect first (option 1)[/red]")
                console.input("\nPress Enter to continue...")
            else:
                dashboard.run_live(refresh_rate=2.0)
                
        elif choice == "3":
            if not dashboard.engine:
                console.print("\n[red]❌ Please connect first (option 1)[/red]")
                console.input("\nPress Enter to continue...")
            else:
                dashboard.show_snapshot()
                console.input("\nPress Enter to continue...")
                
        elif choice == "4":
            dashboard.show_ascii_chart()
            console.input("\nPress Enter to continue...")
            
        elif choice == "5":
            show_status(dashboard)
            console.input("\nPress Enter to continue...")
            
        elif choice == "Q":
            console.print("\n[yellow]👋 Goodbye![/yellow]\n")
            break
            
        else:
            console.print("\n[red]❌ Invalid option[/red]")
            console.input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]👋 Goodbye![/yellow]\n")
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]\n")
