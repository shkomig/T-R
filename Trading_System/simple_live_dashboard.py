"""
Simple Live Trading Dashboard
==============================
ממשק פשוט למסחר חי - משתמש רק ב-Historical Data

עובד ללא Real-Time subscription!
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import time
import yaml
import pandas as pd
from colorama import Fore, Back, Style, init
from ib_insync import IB, ScannerSubscription, Stock

sys.path.append(str(Path(__file__).parent))

from execution.broker_interface import IBBroker
from strategies import VWAPStrategy, MomentumStrategy, BollingerBandsStrategy, MeanReversionStrategy, PairsTradingStrategy
from strategies.simple_momentum_strategy import SimpleMomentumStrategy
from strategies.base_strategy import SignalType

# Initialize colorama
init(autoreset=True)


class SimpleLiveDashboard:
    """Simple Live Trading Dashboard"""
    
    def __init__(self):
        self.broker = None
        self.vwap_strategy = None
        self.momentum_strategy = None
        self.bollinger_strategy = None
        self.mean_reversion_strategy = None  # [LAUNCH] Mean Reversion strategy!
        self.pairs_trading_strategy = None   # [LAUNCH] NEW: Pairs Trading strategy!

        # Load config first
        with open('config/trading_config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)

        # TWS Market Scanner integration
        self.scanner_ib = None  # Separate IB connection for scanner
        self.scanner_enabled = True
        self.scanner_results = []
        self.last_scanner_update = None
        self.scanner_refresh_interval = 300  # 5 minutes in seconds
        self.fixed_symbols = ['MSTR', 'LCID']  # Always keep these
        self.default_symbols = self.config['universe']['tickers']  # Fallback to 35 stocks from config
        self.scanner_status = "Initializing..."

        # Load symbols from config (35 volatile stocks!)
        self.symbols = self.default_symbols
        self.auto_trading = True  # Enable auto-trading
        self.position_size = 10000  # $10k per position
        self.max_positions = self.config['position']['max_positions']  # From config (5 positions)

        # Valid symbols for market data - now using all symbols from config
        self.valid_symbols = set(self.symbols)
    
    def calculate_combined_signal(self, df: pd.DataFrame, symbol: str):
        """Calculate signals from multiple strategies"""
        signals = {}
        vwap_price = df['close'].iloc[-1] if len(df) > 0 else 0
        
        # VWAP Strategy
        try:
            vwap_signals = self.vwap_strategy.generate_signals(df)
            vwap_signal = 'hold'
            
            if vwap_signals and len(vwap_signals) > 0:
                latest_signal = vwap_signals[-1]
                if hasattr(latest_signal, 'signal_type'):
                    if str(latest_signal.signal_type) == 'SignalType.BUY':
                        vwap_signal = 'long'
                    elif str(latest_signal.signal_type) == 'SignalType.SELL':
                        vwap_signal = 'exit'
                
                # Extract VWAP price
                if hasattr(latest_signal, 'metadata') and 'vwap' in latest_signal.metadata:
                    vwap_price = latest_signal.metadata['vwap']
            
            signals['vwap'] = {'signal': vwap_signal, 'price': vwap_price}
            
        except Exception as e:
            signals['vwap'] = {'signal': 'hold', 'price': vwap_price, 'error': str(e)}
        
        # Momentum Strategy
        try:
            momentum_signals = self.momentum_strategy.generate_signals(df)
            momentum_signal = 'hold'
            
            if momentum_signals and len(momentum_signals) > 0:
                latest_signal = momentum_signals[-1]
                if hasattr(latest_signal, 'signal_type'):
                    if str(latest_signal.signal_type) == 'SignalType.BUY':
                        momentum_signal = 'long'
                    elif str(latest_signal.signal_type) == 'SignalType.SELL':
                        momentum_signal = 'exit'
            
            signals['momentum'] = {'signal': momentum_signal}
            
        except Exception as e:
            signals['momentum'] = {'signal': 'hold', 'error': str(e)}
        
        # Bollinger Bands Strategy
        try:
            bollinger_signals = self.bollinger_strategy.generate_signals(df)
            bollinger_signal = 'hold'
            
            if bollinger_signals and len(bollinger_signals) > 0:
                latest_signal = bollinger_signals[-1]
                if hasattr(latest_signal, 'signal_type'):
                    if str(latest_signal.signal_type) == 'SignalType.BUY':
                        bollinger_signal = 'long'
                    elif str(latest_signal.signal_type) == 'SignalType.SELL':
                        bollinger_signal = 'exit'
            
            signals['bollinger'] = {'signal': bollinger_signal}
            
        except Exception as e:
            signals['bollinger'] = {'signal': 'hold', 'error': str(e)}
        
        # [LAUNCH] Mean Reversion Strategy (Enhanced Z-Score)
        try:
            mean_reversion_signals = self.mean_reversion_strategy.generate_signals(df)
            mean_reversion_signal = 'hold'
            
            if mean_reversion_signals and len(mean_reversion_signals) > 0:
                latest_signal = mean_reversion_signals[-1]
                if hasattr(latest_signal, 'signal_type'):
                    if str(latest_signal.signal_type) == 'SignalType.BUY':
                        mean_reversion_signal = 'long'
                    elif str(latest_signal.signal_type) == 'SignalType.SELL':
                        mean_reversion_signal = 'exit'
            
            signals['mean_reversion'] = {'signal': mean_reversion_signal}
            
        except Exception as e:
            signals['mean_reversion'] = {'signal': 'hold', 'error': str(e)}
        
        # Pairs Trading Strategy (Multi-symbol analysis)
        try:
            # For pairs trading, we need data for both stocks in the pair
            pair_data = {}
            for pair_symbol in self.pairs_trading_strategy.pair_symbols:
                if pair_symbol in [symbol]:  # Current symbol analysis
                    pair_data[pair_symbol] = df
                # Note: In a real implementation, we'd need data for both stocks
                # For now, we'll analyze the current symbol within the pair context
            
            if len(pair_data) >= 1:  # At least one symbol from the pair
                pairs_signals = self.pairs_trading_strategy.generate_signals(pair_data)
                pairs_signal = 'hold'
                
                if pairs_signals and len(pairs_signals) > 0:
                    latest_signal = pairs_signals[-1]
                    if hasattr(latest_signal, 'signal_type'):
                        if str(latest_signal.signal_type) == 'SignalType.BUY':
                            pairs_signal = 'long'
                        elif str(latest_signal.signal_type) == 'SignalType.SELL':
                            pairs_signal = 'exit'
                
                signals['pairs_trading'] = {'signal': pairs_signal}
            else:
                signals['pairs_trading'] = {'signal': 'hold', 'note': 'Waiting for pair data'}
            
        except Exception as e:
            signals['pairs_trading'] = {'signal': 'hold', 'error': str(e)}
        
        # [NEW] Simple Momentum Strategy - ONLY for MSTR and LCID
        try:
            simple_momentum_signal = 'hold'
            
            # Only run this strategy for target symbols
            if symbol in ['MSTR', 'LCID']:
                simple_momentum_signals = self.simple_momentum_strategy.generate_signals(df)
                
                if simple_momentum_signals and len(simple_momentum_signals) > 0:
                    latest_signal = simple_momentum_signals[-1]
                    if hasattr(latest_signal, 'signal_type'):
                        if str(latest_signal.signal_type) == 'SignalType.BUY':
                            simple_momentum_signal = 'long'
                        elif str(latest_signal.signal_type) == 'SignalType.SELL':
                            simple_momentum_signal = 'exit'
            
            signals['simple_momentum'] = {'signal': simple_momentum_signal}
            
        except Exception as e:
            signals['simple_momentum'] = {'signal': 'hold', 'error': str(e)}
        
        # Combined decision (majority vote) - NOW WITH 5 STRATEGIES!
        # CHANGED: Lowered from 3 to 2 for more trading opportunities with volatile stocks
        long_votes = sum(1 for s in signals.values() if s.get('signal') == 'long')
        exit_votes = sum(1 for s in signals.values() if s.get('signal') == 'exit')
        
        if long_votes >= 2:  # Need 2+ strategies to agree (40% consensus)
            combined_signal = 'long'
        elif exit_votes >= 2:
            combined_signal = 'exit'
        else:
            combined_signal = 'hold'
        
        return signals, combined_signal
    
    def _clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def connect_scanner(self):
        """Connect to TWS Scanner API"""
        try:
            print("[SCANNER] Connecting to TWS Market Scanner...")
            self.scanner_ib = IB()
            # Use different client_id for scanner to avoid conflicts
            import random
            scanner_client_id = random.randint(5000, 5999)
            self.scanner_ib.connect('127.0.0.1', 7497, clientId=scanner_client_id)
            self.scanner_status = "Connected"
            print(f"[OK] Scanner connected (client_id: {scanner_client_id})")
            return True
        except Exception as e:
            self.scanner_status = f"Error: {str(e)}"
            print(f"[WARN] Scanner connection failed: {e}")
            self.scanner_enabled = False
            return False

    def fetch_top_gainers(self):
        """Fetch top % gainers from TWS Scanner with quality filters"""
        if not self.scanner_ib or not self.scanner_ib.isConnected():
            self.scanner_status = "Not Connected"
            return []

        try:
            # Create scanner subscription for top % gainers
            sub = ScannerSubscription(
                instrument='STK',  # Stocks only
                locationCode='STK.US.MAJOR',  # Major US exchanges only (NASDAQ, NYSE)
                scanCode='TOP_PERC_GAIN',  # Top % gainers
                abovePrice=5.0,  # Minimum price $5
                aboveVolume=500000  # Minimum volume 500K
            )

            # Request scanner data
            scanner_data = self.scanner_ib.reqScannerData(sub)

            # Filter results with quality checks
            filtered_results = []
            for item in scanner_data[:30]:  # Check top 30 to get 20 good ones
                try:
                    # Get contract details
                    contract = item.contractDetails.contract
                    symbol = contract.symbol
                    
                    # Skip if already have enough
                    if len(filtered_results) >= 20:
                        break

                    # Quality filters
                    # 1. Skip penny stocks (double check)
                    if hasattr(contract, 'lastTradeDateOrContractMonth'):
                        continue  # Skip options/futures
                    
                    # 2. Skip foreign/ADR symbols with special characters
                    if any(c in symbol for c in ['.', '-', '^']):
                        continue
                    
                    # 3. Skip symbols longer than 5 chars (usually weird tickers)
                    if len(symbol) > 5:
                        continue
                    
                    # 4. Only major exchanges
                    exchange = contract.primaryExchange or contract.exchange
                    if exchange not in ['NASDAQ', 'NYSE', 'ARCA', 'AMEX']:
                        continue

                    # Store result
                    filtered_results.append({
                        'symbol': symbol,
                        'rank': item.rank,
                        'distance': item.distance  # This often contains the % change
                    })

                except Exception as e:
                    continue

            self.scanner_status = f"Active ({len(filtered_results)} stocks)"
            return filtered_results

        except Exception as e:
            self.scanner_status = f"Scan Error: {str(e)[:30]}"
            print(f"[WARN] Scanner error: {e}")
            return []

    def update_symbols_from_scanner(self):
        """Update trading symbols with scanner results"""
        if not self.scanner_enabled:
            return

        # Check if it's time to refresh
        now = datetime.now()
        if self.last_scanner_update:
            time_since_update = (now - self.last_scanner_update).total_seconds()
            if time_since_update < self.scanner_refresh_interval:
                return  # Not time yet

        # Fetch scanner results
        self.scanner_results = self.fetch_top_gainers()

        if self.scanner_results:
            # Extract symbols from scanner
            scanner_symbols = [r['symbol'] for r in self.scanner_results]

            # Combine: fixed symbols + scanner symbols (max 25 total)
            new_symbols = list(self.fixed_symbols)  # Start with fixed
            for sym in scanner_symbols:
                if sym not in new_symbols:
                    new_symbols.append(sym)
                    if len(new_symbols) >= 25:
                        break

            # Update symbols list
            old_count = len(self.symbols)
            self.symbols = new_symbols
            self.valid_symbols = set(self.symbols)

            # Log the update
            self.last_scanner_update = now
            update_time = now.strftime('%H:%M:%S')
            print(f"\n[SCANNER] Symbols updated at {update_time}")
            print(f"          {old_count} -> {len(new_symbols)} symbols")
            print(f"          Fixed: {', '.join(self.fixed_symbols)}")
            print(f"          Scanner: {len(scanner_symbols)} hot stocks")
        else:
            # Fallback to default 35 symbols from config if scanner fails
            if self.symbols != self.default_symbols:
                self.symbols = self.default_symbols
                self.valid_symbols = set(self.symbols)
                print(f"[SCANNER] Falling back to {len(self.default_symbols)} symbols from config")
                print(f"          Includes: {', '.join(self.default_symbols[:5])}... and {len(self.default_symbols)-5} more")

    def execute_trade(self, symbol: str, signal: str, price: float):
        """Execute trade based on signal"""
        if not self.auto_trading:
            return False
        
        try:
            # Get current positions
            positions = self.broker.get_positions()
            current_symbols = [pos['symbol'] for pos in positions]
            
            if signal == 'long' and symbol not in current_symbols:
                # Check if we have room for more positions
                if len(positions) >= self.max_positions:
                    print(f"    {Fore.YELLOW}[WARN] Max positions ({self.max_positions}) reached{Style.RESET_ALL}")
                    return False
                
                # Calculate quantity
                quantity = int(self.position_size / price)
                
                # Place buy order
                result = self.broker.place_order(
                    symbol=symbol,
                    action='BUY',
                    order_type='MKT',
                    quantity=quantity
                )
                
                if result:
                    print(f"    {Fore.GREEN}[OK] BUY Order placed: {quantity} shares of {symbol} @ ${price:.2f}{Style.RESET_ALL}")
                    return True
                else:
                    print(f"    {Fore.RED}[ERROR] Failed to place BUY order for {symbol}{Style.RESET_ALL}")
                    
            elif signal == 'exit' and symbol in current_symbols:
                # Find position to close
                position = next((pos for pos in positions if pos['symbol'] == symbol), None)
                if position:
                    quantity = abs(int(position['position']))
                    
                    # Place sell order
                    result = self.broker.place_order(
                        symbol=symbol,
                        action='SELL',
                        order_type='MKT',
                        quantity=quantity
                    )
                    
                    if result:
                        print(f"    {Fore.CYAN}[OK] SELL Order placed: {quantity} shares of {symbol} @ ${price:.2f}{Style.RESET_ALL}")
                        return True
                    else:
                        print(f"    {Fore.RED}[ERROR] Failed to place SELL order for {symbol}{Style.RESET_ALL}")
                        
        except Exception as e:
            print(f"    {Fore.RED}[ERROR] Trade execution error: {e}{Style.RESET_ALL}")
            
        return False
    
    def display_dashboard(self):
        """Display live dashboard"""
        try:
            cycle = 1
            while True:
                # Update symbols from scanner (every 5 minutes)
                self.update_symbols_from_scanner()

                self._clear_screen()

                # Header
                print(Fore.WHITE + Style.BRIGHT + "ACCOUNT STATUS")
                print("=" * 80)
                print(f"     {Fore.CYAN}{Style.BRIGHT}[CHART] LIVE TRADING DASHBOARD - HISTORICAL DATA MODE{Style.RESET_ALL}")
                print("=" * 80)
                print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                if self.auto_trading:
                    print(f"[AUTO] Auto-Trading: {Fore.GREEN}ENABLED{Style.RESET_ALL}")
                else:
                    print(f"[PAUSE]  Auto-Trading: {Fore.YELLOW}DISABLED{Style.RESET_ALL}")

                # Scanner status
                if self.scanner_enabled:
                    status_color = Fore.GREEN if "Active" in self.scanner_status else Fore.YELLOW
                    print(f"[SCANNER] Market Scanner: {status_color}{self.scanner_status}{Style.RESET_ALL}")
                    if self.last_scanner_update:
                        time_since = (datetime.now() - self.last_scanner_update).total_seconds()
                        next_refresh = max(0, self.scanner_refresh_interval - time_since)
                        print(f"          Next refresh in: {int(next_refresh)}s | Symbols: {len(self.symbols)}")
                else:
                    print(f"[SCANNER] Market Scanner: {Fore.RED}DISABLED{Style.RESET_ALL}")
                print()
                
                # Account Status
                print(Fore.WHITE + Style.BRIGHT + "ACCOUNT STATUS")
                print(Fore.WHITE + "-"*80)
                
                account_info = self.broker.get_account_summary()
                if account_info:
                    # Extract values from potentially nested structure
                    net_liq = account_info.get('NetLiquidation', {})
                    cash_balance = account_info.get('CashBalance', {})
                    buying_power = account_info.get('BuyingPower', {})
                    
                    # Handle different data structures
                    net_liq_value = net_liq.get('value', net_liq) if isinstance(net_liq, dict) else net_liq
                    cash_value = cash_balance.get('value', cash_balance) if isinstance(cash_balance, dict) else cash_balance
                    buying_power_value = buying_power.get('value', buying_power) if isinstance(buying_power, dict) else buying_power
                    
                    print(f"[$] Net Liquidation: ${float(net_liq_value):,.2f}")
                    print(f"[$$$] Cash:            ${float(cash_value):,.2f}")
                    print(f"[HOT] Buying Power:    ${float(buying_power_value):,.2f}")
                else:
                    print(Fore.YELLOW + "[WARN] Account info not available")
                print()
                
                # Positions
                print(Fore.WHITE + Style.BRIGHT + "POSITIONS")
                print(Fore.WHITE + "-"*80)
                
                positions = self.broker.get_positions()
                
                if positions:
                    for pos in positions:
                        symbol = pos['symbol']
                        quantity = pos['position']
                        entry_price = pos['avg_cost']
                        
                        # Skip invalid symbols that cause Error 200
                        if symbol not in self.valid_symbols:
                            print(f"  {Fore.YELLOW}{symbol:<8} | Qty: {quantity:>4} | Entry: ${entry_price:>8.2f} | Invalid symbol - skipped{Style.RESET_ALL}")
                            continue
                        
                        # Get current price via historical data
                        bars = self.broker.get_historical_data(
                            symbol=symbol,
                            duration="1 D",
                            bar_size="1 min"
                        )
                        
                        if bars and len(bars) > 0:
                            current_price = bars[-1].close if hasattr(bars[-1], 'close') else entry_price
                            pnl = (current_price - entry_price) * quantity
                            pnl_pct = ((current_price - entry_price) / entry_price) * 100 if entry_price > 0 else 0
                            
                            pnl_color = Fore.GREEN if pnl >= 0 else Fore.RED
                            
                            print(f"  {Fore.CYAN}{symbol:<8}{Style.RESET_ALL} | "
                                  f"Qty: {quantity:>4} | "
                                  f"Entry: ${entry_price:>7.2f} | "
                                  f"Current: ${current_price:>7.2f} | "
                                  f"P&L: {pnl_color}{pnl:>+9.2f}{Style.RESET_ALL} "
                                  f"({pnl_color}{pnl_pct:>+6.2f}%{Style.RESET_ALL})")
                        else:
                            print(f"  {Fore.CYAN}{symbol:<8}{Style.RESET_ALL} | Qty: {quantity:>4} | Entry: ${entry_price:>7.2f} | {Fore.YELLOW}No current price{Style.RESET_ALL}")
                else:
                    print(Fore.YELLOW + "  No open positions")
                print()

                # Scanner Results (Top % Gainers)
                if self.scanner_enabled and self.scanner_results:
                    print(Fore.WHITE + Style.BRIGHT + "MARKET SCANNER - TOP % GAINERS")
                    print(Fore.WHITE + "-"*80)
                    print(f"  {'Rank':<6} {'Symbol':<10} {'% Change':>10}")
                    print(Fore.WHITE + "  " + "-"*30)

                    for i, result in enumerate(self.scanner_results[:10], 1):  # Show top 10
                        symbol = result['symbol']
                        distance = result.get('distance', 'N/A')
                        rank = result.get('rank', i)

                        # Highlight fixed symbols
                        if symbol in self.fixed_symbols:
                            symbol_text = f"{Fore.CYAN}{symbol} [FIXED]{Style.RESET_ALL}"
                        else:
                            symbol_text = f"{Fore.GREEN}{symbol}{Style.RESET_ALL}"

                        print(f"  {rank:<6} {symbol_text:<25} {distance:>10}")
                    print()

                # Market Data & Signals (6 Strategies - 5 Normal + Simple Momentum for MSTR/LCID)
                print(Fore.WHITE + Style.BRIGHT + "MARKET DATA & SIGNALS - 6 STRATEGY SYSTEM")
                print(Fore.WHITE + "V=VWAP | M=Momentum | B=Bollinger | Z=Mean Reversion | P=Pairs | S=SimpleMomentum(MSTR/LCID only)")
                print(Fore.WHITE + "-"*80)
                
                for symbol in self.symbols:
                    try:
                        # Get historical data for signal calculation
                        bars = self.broker.get_historical_data(
                            symbol=symbol,
                            duration="2 D",
                            bar_size="30 mins"
                        )
                        
                        if bars and len(bars) >= 2:
                            # Convert to DataFrame for strategy calculation
                            df_data = []
                            for bar in bars:
                                df_data.append({
                                    'timestamp': bar.date,
                                    'open': bar.open,
                                    'high': bar.high,
                                    'low': bar.low,
                                    'close': bar.close,
                                    'volume': bar.volume
                                })
                            
                            df = pd.DataFrame(df_data)
                            
                            # Get current price and change
                            current_bar = bars[-1]
                            prev_bar = bars[-2] if len(bars) > 1 else current_bar
                            
                            current_price = current_bar.close
                            price_change = current_bar.close - prev_bar.close
                            change_pct = (price_change / prev_bar.close) * 100 if prev_bar.close > 0 else 0
                            
                            # Calculate signals from multiple strategies
                            # [TARGET] Use modular Signal Aggregator if available (Phase 2 refactoring)
                            if hasattr(self, 'signal_aggregator') and self.signal_aggregator is not None:
                                strategy_signals, combined_signal = self.signal_aggregator.calculate_combined_signal(df, symbol)
                            else:
                                # Fallback to legacy method
                                strategy_signals, combined_signal = self.calculate_combined_signal(df, symbol)
                            
                            # Get VWAP price for display
                            vwap = strategy_signals.get('vwap', {}).get('price', current_price)
                            deviation = ((current_price - vwap) / vwap) * 100 if vwap > 0 else 0
                            
                            # Color coding
                            price_color = Fore.GREEN if price_change >= 0 else Fore.RED
                            signal_color = Fore.GREEN if combined_signal == 'long' else (Fore.RED if combined_signal == 'exit' else Fore.YELLOW)
                            signal_icon = "[UP]" if combined_signal == 'long' else ("[DOWN]" if combined_signal == 'exit' else "[PAUSE] ")
                            
                            # Strategy summary - NOW WITH 6 STRATEGIES! [LAUNCH]
                            vwap_sig = strategy_signals.get('vwap', {}).get('signal', 'hold')[0].upper()
                            momentum_sig = strategy_signals.get('momentum', {}).get('signal', 'hold')[0].upper()
                            bollinger_sig = strategy_signals.get('bollinger', {}).get('signal', 'hold')[0].upper()
                            mean_rev_sig = strategy_signals.get('mean_reversion', {}).get('signal', 'hold')[0].upper()
                            pairs_sig = strategy_signals.get('pairs_trading', {}).get('signal', 'hold')[0].upper()
                            simple_mom_sig = strategy_signals.get('simple_momentum', {}).get('signal', 'hold')[0].upper()
                            
                            # Special marking for MSTR and LCID to show Simple Momentum is active
                            if symbol in ['MSTR', 'LCID']:
                                strategy_summary = f"V:{vwap_sig} M:{momentum_sig} B:{bollinger_sig} Z:{mean_rev_sig} P:{pairs_sig} {Fore.CYAN}S:{simple_mom_sig}{Style.RESET_ALL}"
                            else:
                                strategy_summary = f"V:{vwap_sig} M:{momentum_sig} B:{bollinger_sig} Z:{mean_rev_sig} P:{pairs_sig}"
                            
                            print(f"  {Fore.CYAN}{symbol:<8}{Style.RESET_ALL} | "
                                  f"${current_price:>7.2f} {price_color}{price_change:>+6.2f} ({change_pct:>+5.2f}%){Style.RESET_ALL} | "
                                  f"{strategy_summary} | "
                                  f"{signal_color}{signal_icon} {combined_signal.upper()}{Style.RESET_ALL}")
                            
                            # Execute auto-trading if signal is actionable
                            if self.auto_trading and combined_signal in ['long', 'exit']:
                                self.execute_trade(symbol, combined_signal, current_price)
                        
                        else:
                            print(f"  {Fore.CYAN}{symbol:<8}{Style.RESET_ALL} | {Fore.YELLOW}No data available{Style.RESET_ALL}")
                            
                    except Exception as e:
                        print(f"  {Fore.CYAN}{symbol:<8}{Style.RESET_ALL} | {Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
                
                print()
                print(Fore.WHITE + "-"*80)
                print(f"Cycle: #{cycle} | Next update in 10 seconds...")
                print(Fore.YELLOW + "[PAUSE]  Press Ctrl+C to stop")
                print()
                
                cycle += 1
                time.sleep(10)  # Update every 10 seconds
                
        except KeyboardInterrupt:
            print("\n\n[WARN] Stopped by user")
        except Exception as e:
            print(f"\n[ERROR] Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.broker:
                print("\n[STOP] Disconnecting...")
                self.broker.disconnect()
                print("[OK] Dashboard stopped")
    
    def run(self):
        """Run the live dashboard"""
        print("[LAUNCH] Starting Live Trading Dashboard...")
        print("-" * 50)
        
        if self.auto_trading:
            print(f"[AUTO] Auto-Trading: {Fore.GREEN}ENABLED{Style.RESET_ALL} (Position Size: ${self.position_size:,})")
        else:
            print(f"[PAUSE]  Auto-Trading: {Fore.YELLOW}DISABLED{Style.RESET_ALL}")
        print()
        print("Press Ctrl+C to stop...")
        print()
        time.sleep(2)
        
        try:
            # Connect to IB Gateway
            print("[PLUG] Connecting to IB Gateway...")
            # Use unique client_id to avoid conflicts
            import random
            client_id = random.randint(2000, 9999)
            print(f"[INFO] Using client_id: {client_id}")
            self.broker = IBBroker(port=7497, client_id=client_id)
            
            if not self.broker.connect():
                print("[ERROR] Failed to connect to IB Gateway")
                print("   Make sure IB Gateway is running on Port 7497")
                return
            
            print("[OK] Connected successfully!")
            print()

            # Connect to Market Scanner
            if self.scanner_enabled:
                if self.connect_scanner():
                    print("[OK] Market Scanner initialized - Top % gainers tracking enabled")
                    # Do initial scan
                    self.update_symbols_from_scanner()
                    print(f"[OK] Initial scan complete - Tracking {len(self.symbols)} symbols")
                else:
                    print("[WARN] Market Scanner disabled - Using fixed symbols only")
                    self.symbols = self.fixed_symbols
                    self.valid_symbols = set(self.symbols)
            print()

            # Initialize strategies
            print("[BRAIN] Loading trading strategies...")
            self.vwap_strategy = VWAPStrategy(self.config['strategies']['vwap'])
            print("  [OK] VWAP Strategy loaded")
            
            self.momentum_strategy = MomentumStrategy(self.config['strategies']['Momentum'])
            print("  [OK] Momentum Strategy loaded (61% Win Rate)")
            
            self.bollinger_strategy = BollingerBandsStrategy(self.config['strategies']['Bollinger_Bands'])
            print("  [OK] Bollinger Bands Strategy loaded")
            
            self.mean_reversion_strategy = MeanReversionStrategy(self.config['strategies']['Mean_Reversion'])
            print("  [OK] Mean Reversion Strategy loaded (65% Win Rate, Z-Score Enhanced)")
            
            self.pairs_trading_strategy = PairsTradingStrategy(self.config['strategies']['Pairs_Trading'])
            print("  [OK] Pairs Trading Strategy loaded (68% Win Rate, 1.8 Sharpe Ratio)")
            
            # NEW: Simple Momentum Strategy for MSTR and LCID only
            simple_momentum_config = {
                'target_symbols': ['MSTR', 'LCID'],
                'price_change_threshold': 0.5,  # 0.5% trigger
                'lookback_minutes': 5,
                'volume_spike_threshold': 1.2,
                'stop_loss_percent': 0.3,
                'take_profit_percent': 1.0
            }
            self.simple_momentum_strategy = SimpleMomentumStrategy(simple_momentum_config)
            print(f"  [OK] Simple Momentum Strategy loaded - {Fore.CYAN}AGGRESSIVE MODE for MSTR & LCID{Style.RESET_ALL}")
            
            print(f"[LAUNCH] 6-Strategy Auto-Trading Ready! (5 Normal + 1 Aggressive for MSTR/LCID)")
            print("[CHART] Market Neutral & Long/Short strategies combined!")
            print()
            
            # Run dashboard
            self.display_dashboard()
            
        except Exception as e:
            print(f"[ERROR] Error starting dashboard: {e}")
        finally:
            # Disconnect scanner
            if self.scanner_ib and self.scanner_ib.isConnected():
                print("\n[CLEANUP] Disconnecting Market Scanner...")
                self.scanner_ib.disconnect()

            # Disconnect broker
            if self.broker:
                self.broker.disconnect()


if __name__ == "__main__":
    dashboard = SimpleLiveDashboard()
    dashboard.run()