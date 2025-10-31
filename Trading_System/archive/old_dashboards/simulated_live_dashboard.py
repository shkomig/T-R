"""
Simulated Live Trading Dashboard
=================================
סימולציה של מסחר חי עם ממשק ויזואלי

מריץ Backtest בסגנון "Live Trading" עם:
- עדכונים כל 2 שניות
- תצוגה ויזואלית של מצב המסחר
- סטטיסטיקות בזמן אמת
- סימולציה של סיגנלים וביצוע עסקאות
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import time
import yaml
import pandas as pd
import numpy as np
from colorama import Fore, Back, Style, init

sys.path.append(str(Path(__file__).parent))

from strategies import VWAPStrategy
from backtesting import BacktestEngine

# Initialize colorama
init(autoreset=True)


class SimulatedLiveDashboard:
    """Simulated Live Trading Dashboard"""
    
    def __init__(self):
        self.current_bar = 0
        self.total_bars = 0
        self.equity = 100000.0
        self.initial_equity = 100000.0
        self.positions = {}
        self.trades = []
        self.signals = []
        
        # Load config
        with open('config/trading_config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Generate data
        self.data = self._generate_data()
        self.total_bars = len(self.data['AAPL'])
        
        # Initialize strategy
        self.strategy = VWAPStrategy(self.config['strategies']['vwap'])
    
    def _generate_data(self):
        """Generate realistic market data"""
        print("📊 Generating market data...")
        
        data = {}
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        
        # Generate 2 hours of data (4 bars x 30min = 2 hours)
        bars = 120  # 120 bars for demo
        
        for symbol in symbols:
            base_prices = {'AAPL': 270, 'GOOGL': 145, 'MSFT': 315}
            base = base_prices[symbol]
            
            # Generate timestamps
            start_time = datetime.now() - timedelta(hours=2)
            timestamps = pd.date_range(start=start_time, periods=bars, freq='1min')
            
            # Generate realistic price movement
            trend = np.linspace(0, base * 0.03, bars)  # 3% trend
            cycle = np.sin(np.linspace(0, 6 * np.pi, bars)) * (base * 0.01)
            noise = np.random.randn(bars) * (base * 0.005)
            
            close = base + trend + cycle + noise
            
            # Generate OHLC
            df = pd.DataFrame({
                'open': close + np.random.randn(bars) * (base * 0.002),
                'high': close + abs(np.random.randn(bars)) * (base * 0.003),
                'low': close - abs(np.random.randn(bars)) * (base * 0.003),
                'close': close,
                'volume': np.random.randint(50000, 200000, bars)
            }, index=timestamps)
            
            data[symbol] = df
        
        print(f"✓ Generated {bars} bars for {len(symbols)} symbols")
        return data
    
    def _clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _print_header(self):
        """Print dashboard header"""
        print(Fore.CYAN + "="*80)
        print(Fore.CYAN + Style.BRIGHT + "     📊 LIVE TRADING DASHBOARD - SIMULATED MODE")
        print(Fore.CYAN + "="*80)
        print()
    
    def _print_account_info(self):
        """Print account information"""
        pnl = self.equity - self.initial_equity
        pnl_pct = (pnl / self.initial_equity) * 100
        
        print(Fore.WHITE + Style.BRIGHT + "ACCOUNT STATUS")
        print(Fore.WHITE + "─"*80)
        
        # Equity
        equity_color = Fore.GREEN if pnl >= 0 else Fore.RED
        print(f"💰 Equity:    {equity_color}${self.equity:,.2f}{Style.RESET_ALL}  "
              f"({equity_color}{pnl:+,.2f}{Style.RESET_ALL} | "
              f"{equity_color}{pnl_pct:+.2f}%{Style.RESET_ALL})")
        
        # Cash
        cash = self.equity - sum(pos['value'] for pos in self.positions.values())
        print(f"💵 Cash:      ${cash:,.2f}")
        
        # Positions value
        pos_value = sum(pos['value'] for pos in self.positions.values())
        print(f"📈 Positions: ${pos_value:,.2f}")
        print()
    
    def _print_positions(self):
        """Print current positions"""
        print(Fore.WHITE + Style.BRIGHT + "POSITIONS")
        print(Fore.WHITE + "─"*80)
        
        if not self.positions:
            print(Fore.YELLOW + "  No open positions")
        else:
            for symbol, pos in self.positions.items():
                current_price = self.data[symbol].iloc[self.current_bar]['close']
                entry_price = pos['entry_price']
                quantity = pos['quantity']
                pnl = (current_price - entry_price) * quantity
                pnl_pct = ((current_price - entry_price) / entry_price) * 100
                
                pnl_color = Fore.GREEN if pnl >= 0 else Fore.RED
                
                print(f"  {Fore.CYAN}{symbol:<8}{Style.RESET_ALL} | "
                      f"Qty: {quantity:>3} | "
                      f"Entry: ${entry_price:>7.2f} | "
                      f"Current: ${current_price:>7.2f} | "
                      f"P&L: {pnl_color}{pnl:>+8.2f}{Style.RESET_ALL} "
                      f"({pnl_color}{pnl_pct:>+6.2f}%{Style.RESET_ALL})")
        print()
    
    def _print_market_data(self):
        """Print current market data"""
        print(Fore.WHITE + Style.BRIGHT + "MARKET DATA")
        print(Fore.WHITE + "─"*80)
        
        for symbol in ['AAPL', 'GOOGL', 'MSFT']:
            df = self.data[symbol].iloc[:self.current_bar+1]
            
            if len(df) < 2:
                continue
            
            current = df.iloc[-1]
            prev = df.iloc[-2]
            
            change = current['close'] - prev['close']
            change_pct = (change / prev['close']) * 100
            
            price_color = Fore.GREEN if change >= 0 else Fore.RED
            
            # Calculate VWAP
            df['typical'] = (df['high'] + df['low'] + df['close']) / 3
            df['vwap'] = (df['typical'] * df['volume']).cumsum() / df['volume'].cumsum()
            vwap = df['vwap'].iloc[-1]
            
            deviation = ((current['close'] - vwap) / vwap) * 100
            
            # Signal
            signal = ""
            if deviation < -0.8:
                signal = f"{Fore.GREEN}📈 LONG{Style.RESET_ALL}"
            elif deviation > 0.8:
                signal = f"{Fore.RED}📉 EXIT{Style.RESET_ALL}"
            else:
                signal = f"{Fore.YELLOW}⏸️  HOLD{Style.RESET_ALL}"
            
            print(f"  {Fore.CYAN}{symbol:<8}{Style.RESET_ALL} | "
                  f"${current['close']:>7.2f} "
                  f"{price_color}{change:>+6.2f}{Style.RESET_ALL} "
                  f"({price_color}{change_pct:>+5.2f}%{Style.RESET_ALL}) | "
                  f"VWAP: ${vwap:>7.2f} | "
                  f"Dev: {deviation:>+5.2f}% | "
                  f"{signal}")
        print()
    
    def _print_recent_trades(self):
        """Print recent trades"""
        print(Fore.WHITE + Style.BRIGHT + "RECENT TRADES")
        print(Fore.WHITE + "─"*80)
        
        if not self.trades:
            print(Fore.YELLOW + "  No trades yet")
        else:
            for trade in self.trades[-5:]:  # Last 5 trades
                action_color = Fore.GREEN if trade['action'] == 'BUY' else Fore.RED
                pnl_color = Fore.GREEN if trade.get('pnl', 0) >= 0 else Fore.RED
                
                pnl_str = ""
                if 'pnl' in trade:
                    pnl_str = f"| P&L: {pnl_color}{trade['pnl']:>+8.2f}{Style.RESET_ALL}"
                
                print(f"  {trade['time']} | "
                      f"{action_color}{trade['action']:<4}{Style.RESET_ALL} | "
                      f"{Fore.CYAN}{trade['symbol']:<8}{Style.RESET_ALL} | "
                      f"{trade['quantity']:>3} @ ${trade['price']:>7.2f} "
                      f"{pnl_str}")
        print()
    
    def _print_statistics(self):
        """Print trading statistics"""
        print(Fore.WHITE + Style.BRIGHT + "STATISTICS")
        print(Fore.WHITE + "─"*80)
        
        total_trades = len([t for t in self.trades if 'pnl' in t])
        winning_trades = len([t for t in self.trades if t.get('pnl', 0) > 0])
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        print(f"  Total Trades:    {total_trades}")
        print(f"  Winning Trades:  {winning_trades}")
        print(f"  Win Rate:        {win_rate:.1f}%")
        print(f"  Signals:         {len(self.signals)}")
        print()
    
    def _print_progress(self):
        """Print progress bar"""
        progress = (self.current_bar / self.total_bars) * 100
        bar_length = 50
        filled = int(bar_length * self.current_bar / self.total_bars)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(Fore.WHITE + "─"*80)
        print(f"Progress: {Fore.CYAN}{bar}{Style.RESET_ALL} {progress:.1f}% "
              f"(Bar {self.current_bar}/{self.total_bars})")
        print(Fore.WHITE + "─"*80)
        print()
        print(Fore.YELLOW + "⏸️  Press Ctrl+C to stop")
        print()
    
    def _process_bar(self):
        """Process current bar and generate signals"""
        for symbol in ['AAPL', 'GOOGL', 'MSFT']:
            df = self.data[symbol].iloc[:self.current_bar+1]
            
            if len(df) < 20:  # Need minimum data
                continue
            
            # Analyze with VWAP strategy
            analysis = self.strategy.analyze(df)
            
            if analysis.get('signal') == 'long' and symbol not in self.positions:
                # BUY signal
                price = df.iloc[-1]['close']
                quantity = int(10000 / price)  # $10k position
                
                self.positions[symbol] = {
                    'quantity': quantity,
                    'entry_price': price,
                    'value': quantity * price
                }
                
                self.trades.append({
                    'time': df.index[-1].strftime('%H:%M:%S'),
                    'action': 'BUY',
                    'symbol': symbol,
                    'quantity': quantity,
                    'price': price
                })
                
                self.signals.append({'type': 'LONG', 'symbol': symbol})
            
            elif analysis.get('signal') == 'exit' and symbol in self.positions:
                # SELL signal
                price = df.iloc[-1]['close']
                pos = self.positions[symbol]
                pnl = (price - pos['entry_price']) * pos['quantity']
                
                self.trades.append({
                    'time': df.index[-1].strftime('%H:%M:%S'),
                    'action': 'SELL',
                    'symbol': symbol,
                    'quantity': pos['quantity'],
                    'price': price,
                    'pnl': pnl
                })
                
                self.equity += pnl
                del self.positions[symbol]
                
                self.signals.append({'type': 'EXIT', 'symbol': symbol})
    
    def run(self):
        """Run the simulated live dashboard"""
        print("="*80)
        print("     🚀 STARTING SIMULATED LIVE TRADING")
        print("="*80)
        print()
        print("✓ Strategy: VWAP (Best performer: +1.46%, Win Rate: 42.86%)")
        print("✓ Mode: Simulated Real-Time")
        print("✓ Update Frequency: 2 seconds per bar")
        print()
        print("Press Ctrl+C to stop...")
        print()
        time.sleep(3)
        
        try:
            while self.current_bar < self.total_bars:
                # Clear screen
                self._clear_screen()
                
                # Process current bar
                self._process_bar()
                
                # Print dashboard
                self._print_header()
                self._print_account_info()
                self._print_positions()
                self._print_market_data()
                self._print_recent_trades()
                self._print_statistics()
                self._print_progress()
                
                # Next bar
                self.current_bar += 1
                
                # Wait
                time.sleep(2)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("\n" + "="*80)
            print(Fore.CYAN + Style.BRIGHT + "     📊 SIMULATION COMPLETED")
            print("="*80)
            print()
            
            final_pnl = self.equity - self.initial_equity
            final_pnl_pct = (final_pnl / self.initial_equity) * 100
            
            pnl_color = Fore.GREEN if final_pnl >= 0 else Fore.RED
            
            print(f"Final Equity: {pnl_color}${self.equity:,.2f}{Style.RESET_ALL}")
            print(f"Total P&L:    {pnl_color}{final_pnl:+,.2f}{Style.RESET_ALL} "
                  f"({pnl_color}{final_pnl_pct:+.2f}%{Style.RESET_ALL})")
            print(f"Total Trades: {len([t for t in self.trades if 'pnl' in t])}")
            print()


if __name__ == "__main__":
    dashboard = SimulatedLiveDashboard()
    dashboard.run()
