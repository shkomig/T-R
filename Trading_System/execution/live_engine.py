"""
Live Trading Engine

Main live trading loop integrating strategies, risk management, order execution,
and monitoring for real-time trading.

Author: Trading System
Date: October 29, 2025
"""

import logging
from typing import Dict, List, Optional, Set
from datetime import datetime, time as dt_time
import time
import pandas as pd
from ib_insync import IB, Stock, util
import yaml

from strategies.ema_cross_strategy import EMACrossStrategy
from strategies.vwap_strategy import VWAPStrategy
from strategies.volume_breakout_strategy import VolumeBreakoutStrategy
from strategies.rsi_divergence_strategy import RSIDivergenceStrategy
from strategies.advanced_volume_breakout_strategy import VolumeBreakoutStrategy as AdvancedVolumeBreakoutStrategy
from strategies.base_strategy import SignalType, TradingSignal
from execution.order_manager import OrderManager, OrderRequest, OrderSide, OrderType
from execution.position_tracker import PositionTracker, Position, PositionSide
from risk_management.position_sizer import PositionSizer
from risk_management.risk_calculator import RiskCalculator
from monitoring.alert_system import AlertSystem, AlertType, AlertLevel
from utils.logger import setup_logging, get_trade_logger


class LiveTradingEngine:
    """
    Main live trading engine.
    
    Orchestrates all components for live trading:
    - Market data streaming
    - Strategy signal generation
    - Risk management
    - Order execution
    - Position tracking
    - Monitoring and alerts
    """
    
    def __init__(self, config_path: str = "config/trading_config.yaml"):
        """
        Initialize Live Trading Engine.
        
        Args:
            config_path: Path to configuration file
        """
        # Set up logging
        self.main_logger = setup_logging()
        self.logger = self.main_logger.get_logger()
        self.trade_logger = get_trade_logger()
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Load risk management config
        risk_config_path = "config/risk_management.yaml"
        with open(risk_config_path, 'r') as f:
            self.risk_config = yaml.safe_load(f)
        
        # Merge risk config into main config
        self.config['account'] = self.risk_config.get('account', {})
        self.config['position_sizing'] = self.risk_config.get('position_sizing', {})
        
        # Components
        self.ib: Optional[IB] = None
        self.order_manager: Optional[OrderManager] = None
        self.position_tracker: Optional[PositionTracker] = None
        self.position_sizer: Optional[PositionSizer] = None
        self.risk_calculator: Optional[RiskCalculator] = None
        self.alert_system: Optional[AlertSystem] = None
        
        # Strategies
        self.strategies: Dict[str, object] = {}
        
        # Trading state
        self.is_running = False
        self.is_market_hours = False
        self.symbols: List[str] = []
        self.market_data: Dict[str, pd.DataFrame] = {}  # symbol -> DataFrame
        self.latest_bars: Dict[str, pd.Series] = {}     # symbol -> latest bar
        
        # Settings
        self.broker_config = self.config.get('broker', {})
        self.paper_trading = self.config.get('development', {}).get('paper_trading', True)
        self.update_interval = 30  # seconds (30 min bars)
        self.initial_capital = 100000
        self.current_capital = self.initial_capital
        
        # Trading hours
        market_hours = self.config.get('market', {}).get('trading_hours', {})
        self.market_open = dt_time(9, 30)  # 9:30 AM
        self.market_close = dt_time(16, 0)  # 4:00 PM
        
        # Statistics
        self.signals_generated = 0
        self.orders_placed = 0
        self.positions_opened = 0
        self.positions_closed = 0
        
        self.logger.info("LiveTradingEngine initialized")
        self.logger.info(f"Paper Trading: {self.paper_trading}")
    
    def initialize(self) -> bool:
        """
        Initialize all components and connections.
        
        Returns:
            True if initialization successful
        """
        try:
            # Get symbols to trade
            self.symbols = self.config.get('universe', {}).get('tickers', [])
            if not self.symbols:
                self.logger.error("No symbols configured for trading")
                return False
            
            self.logger.info(f"Trading symbols: {', '.join(self.symbols)}")
            
            # Initialize Interactive Brokers connection
            host = self.broker_config.get('host', '127.0.0.1')
            port = self.broker_config.get('port', 7497)
            client_id = self.broker_config.get('client_id', 1)
            
            self.ib = IB()
            self.ib.connect(host, port, clientId=client_id)
            self.logger.info(f"Connected to IB Gateway at {host}:{port}")
            
            # Initialize Order Manager
            self.order_manager = OrderManager()
            self.order_manager.connect(host, port, client_id + 1)
            
            # Initialize Position Tracker
            self.position_tracker = PositionTracker()
            self.position_tracker.connect_ib(self.ib, auto_sync=True)
            
            # Initialize Position Sizer
            self.position_sizer = PositionSizer(self.config)
            
            # Initialize Risk Calculator
            self.risk_calculator = RiskCalculator(self.config)
            
            # Initialize Alert System
            self.alert_system = AlertSystem()
            
            # Initialize strategies
            self._initialize_strategies()
            
            # Subscribe to market data
            self._subscribe_market_data()
            
            self.logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}", exc_info=True)
            return False
    
    def _initialize_strategies(self):
        """Initialize trading strategies."""
        strategy_configs = self.config.get('strategies', {})
        enabled_strategies = strategy_configs.get('enabled', [])
        
        self.logger.info(f"Initializing strategies: {', '.join(enabled_strategies)}")
        
        if 'ema_cross' in enabled_strategies:
            self.strategies['ema_cross'] = EMACrossStrategy(self.config)
            self.logger.info("EMA Cross Strategy initialized")
        
        if 'vwap' in enabled_strategies:
            self.strategies['vwap'] = VWAPStrategy(self.config)
            self.logger.info("VWAP Strategy initialized")
        
        if 'volume_breakout' in enabled_strategies:
            self.strategies['volume_breakout'] = VolumeBreakoutStrategy(self.config)
            self.logger.info("Volume Breakout Strategy initialized")

        if 'rsi_divergence' in enabled_strategies:
            self.strategies['rsi_divergence'] = RSIDivergenceStrategy(name="RSI_Divergence", config=self.config.get('strategies', {}).get('RSI_Divergence', {}))
            self.logger.info("RSI Divergence Strategy initialized")

        if 'advanced_volume_breakout' in enabled_strategies:
            self.strategies['advanced_volume_breakout'] = AdvancedVolumeBreakoutStrategy(name="Advanced_Volume_Breakout", config=self.config.get('strategies', {}).get('Advanced_Volume_Breakout', {}))
            self.logger.info("Advanced Volume Breakout Strategy initialized")
    
    def _subscribe_market_data(self):
        """Subscribe to real-time market data for all symbols."""
        for symbol in self.symbols:
            try:
                contract = Stock(symbol, 'SMART', 'USD')
                
                # Request historical data for initial bars
                bars = self.ib.reqHistoricalData(
                    contract,
                    endDateTime='',
                    durationStr='2 D',  # 2 days
                    barSizeSetting='30 mins',
                    whatToShow='TRADES',
                    useRTH=True,
                    formatDate=1
                )
                
                # Convert to DataFrame
                df = util.df(bars)
                if not df.empty:
                    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 
                                'average', 'barCount']
                    df.set_index('date', inplace=True)
                    self.market_data[symbol] = df
                    self.latest_bars[symbol] = df.iloc[-1]
                    
                    self.logger.info(f"Loaded {len(df)} bars for {symbol}")
                
                # Subscribe to real-time bars
                self.ib.reqRealTimeBars(
                    contract,
                    5,  # 5 seconds
                    'TRADES',
                    False,
                    []
                )
                
            except Exception as e:
                self.logger.error(f"Failed to subscribe to {symbol}: {e}")
    
    def start(self):
        """Start the live trading engine."""
        # Check if already initialized
        if not self.ib or not self.ib.isConnected():
            if not self.initialize():
                self.logger.error("Failed to start: initialization error")
                return False
        
        self.is_running = True
        self.logger.info("Live trading engine started")
        
        # Send startup alert
        self.alert_system.send_alert(
            "🚀 Trading System Started",
            alert_type=AlertType.SYSTEM,
            alert_level=AlertLevel.INFO,
            data={'paper_trading': self.paper_trading, 'symbols': self.symbols}
        )
        
        # Run main loop
        try:
            self._main_loop()
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}", exc_info=True)
            self.alert_system.error_alert("MainLoop", str(e), "LiveTradingEngine")
        finally:
            self.stop()
        
        return True
        # finally:
        #     self.stop()
    
    def _main_loop(self):
        """Main trading loop."""
        last_update = datetime.now()
        
        while self.is_running:
            try:
                # Update IB connection
                self.ib.sleep(1)
                
                # Check if market is open
                self._check_market_hours()
                
                # Process pending orders
                if self.order_manager:
                    self.order_manager.process_pending_orders()
                
                # Check for exit conditions on open positions
                self._check_position_exits()
                
                # Only generate signals during market hours
                if self.is_market_hours:
                    # Check if it's time for next update (every 30 min)
                    now = datetime.now()
                    if (now - last_update).total_seconds() >= self.update_interval:
                        # Update market data
                        self._update_market_data()
                        
                        # Generate signals
                        self._generate_signals()
                        
                        last_update = now
                
                # Sleep briefly
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error in main loop iteration: {e}", exc_info=True)
                time.sleep(5)
    
    def _check_market_hours(self):
        """Check if market is currently open."""
        now = datetime.now().time()
        is_open = self.market_open <= now <= self.market_close
        
        # State change
        if is_open != self.is_market_hours:
            self.is_market_hours = is_open
            
            if is_open:
                self.logger.info("Market opened")
                self.alert_system.send_alert(
                    "📊 Market Opened - Trading Active",
                    alert_type=AlertType.SYSTEM,
                    alert_level=AlertLevel.INFO
                )
            else:
                self.logger.info("Market closed")
                self.alert_system.send_alert(
                    "🔴 Market Closed - Trading Paused",
                    alert_type=AlertType.SYSTEM,
                    alert_level=AlertLevel.INFO
                )
                
                # End of day summary
                self._send_daily_summary()
    
    def _update_market_data(self):
        """Update market data for all symbols."""
        for symbol in self.symbols:
            try:
                contract = Stock(symbol, 'SMART', 'USD')
                
                # Get latest bar
                bars = self.ib.reqHistoricalData(
                    contract,
                    endDateTime='',
                    durationStr='1 D',
                    barSizeSetting='30 mins',
                    whatToShow='TRADES',
                    useRTH=True,
                    formatDate=1
                )
                
                if bars:
                    df = util.df(bars)
                    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 
                                'average', 'barCount']
                    df.set_index('date', inplace=True)
                    
                    # Update market data
                    self.market_data[symbol] = df
                    self.latest_bars[symbol] = df.iloc[-1]
                    
                    # Update position prices
                    if self.position_tracker:
                        current_price = float(df.iloc[-1]['close'])
                        self.position_tracker.update_price(symbol, current_price)
                
            except Exception as e:
                self.logger.error(f"Failed to update data for {symbol}: {e}")
    
    def _generate_signals(self):
        """Generate trading signals from all strategies."""
        for symbol in self.symbols:
            if symbol not in self.market_data:
                continue
            
            df = self.market_data[symbol]
            
            # Check if we already have a position
            has_position = self.position_tracker.has_position(symbol)
            
            # Generate signals from each strategy
            for strategy_name, strategy in self.strategies.items():
                try:
                    # First, analyze the data to calculate indicators
                    analyzed_data = strategy.analyze(df)

                    # Then generate signals from the analyzed data
                    signals = strategy.generate_signals(analyzed_data)

                    # Process each signal returned (can be multiple)
                    for signal in signals:
                        # Set the symbol on the signal
                        signal.symbol = symbol

                        if signal and signal.strength != 'NEUTRAL':
                            self.signals_generated += 1

                            self.logger.info(
                                f"Signal: {signal.signal_type.value} {symbol} "
                                f"({signal.strength}) from {strategy_name}"
                            )

                            # Log signal
                            self.trade_logger.log_signal(
                                symbol,
                                signal.signal_type.value,
                                signal.strength,
                                signal.price,
                                strategy_name
                            )

                            # Send alert
                            self.alert_system.signal_alert(
                                symbol,
                                signal.signal_type.value,
                                signal.strength,
                                signal.price,
                                strategy_name
                            )

                            # Process signal
                            if signal.signal_type == SignalType.BUY and not has_position:
                                self._process_buy_signal(signal, strategy_name)
                            elif signal.signal_type == SignalType.SELL and has_position:
                                self._process_sell_signal(signal, strategy_name)

                except Exception as e:
                    self.logger.error(
                        f"Error generating signal for {symbol} with {strategy_name}: {e}"
                    )
    
    def _process_buy_signal(self, signal: TradingSignal, strategy_name: str):
        """
        Process buy signal.
        
        Args:
            signal: Trading signal
            strategy_name: Name of strategy
        """
        symbol = signal.symbol
        
        # Check risk limits
        if not self.risk_calculator.can_open_new_position(symbol):
            self.logger.warning(f"Risk limits prevent opening position in {symbol}")
            self.alert_system.risk_alert(
                "Position Limit",
                len(self.position_tracker.positions),
                self.risk_calculator.config['max_positions'],
                f"Cannot open new position in {symbol}"
            )
            return
        
        # Calculate position size
        position_size = self.position_sizer.calculate_position_size(
            symbol=symbol,
            entry_price=signal.price,
            stop_loss=signal.stop_loss,
            account_balance=self.current_capital
        )
        
        if position_size <= 0:
            self.logger.warning(f"Invalid position size for {symbol}")
            return
        
        # Create order request
        order_request = OrderRequest(
            symbol=symbol,
            side=OrderSide.BUY,
            quantity=position_size,
            order_type=OrderType.MARKET,
            strategy_name=strategy_name,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit
        )
        
        # Submit order
        success, message = self.order_manager.submit_order(order_request)
        
        if success:
            self.orders_placed += 1
            
            # Log order
            self.trade_logger.log_order(
                order_request.ib_order_id,
                symbol,
                'BUY',
                position_size,
                'MARKET'
            )
            
            # Send alert
            self.alert_system.order_alert(
                order_request.ib_order_id,
                symbol,
                'BUY',
                position_size,
                'MARKET',
                'SUBMITTED'
            )
            
            # Create position (will be updated when filled)
            position = Position(
                symbol=symbol,
                quantity=position_size,
                side=PositionSide.LONG,
                entry_price=signal.price,
                entry_time=datetime.now(),
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                strategy_name=strategy_name
            )
            
            # Wait a bit for fill
            time.sleep(2)
            
            # Check if filled
            order_status = self.order_manager.get_order_status(order_request.ib_order_id)
            if order_status and order_status.value == 'FILLED':
                self.position_tracker.open_position(position)
                self.positions_opened += 1
                
                self.logger.info(f"Position opened: {symbol} {position_size} shares")
                
                # Send alert
                self.alert_system.position_alert(
                    symbol,
                    'OPENED',
                    position_size,
                    signal.price
                )
    
    def _process_sell_signal(self, signal: TradingSignal, strategy_name: str):
        """
        Process sell signal.
        
        Args:
            signal: Trading signal
            strategy_name: Name of strategy
        """
        symbol = signal.symbol
        
        # Get position
        position = self.position_tracker.get_position(symbol)
        if not position:
            return
        
        # Create order request
        order_request = OrderRequest(
            symbol=symbol,
            side=OrderSide.SELL,
            quantity=position.quantity,
            order_type=OrderType.MARKET,
            strategy_name=strategy_name,
            notes=f"Exit signal from {strategy_name}"
        )
        
        # Submit order
        success, message = self.order_manager.submit_order(order_request)
        
        if success:
            self.orders_placed += 1
            
            # Log order
            self.trade_logger.log_order(
                order_request.ib_order_id,
                symbol,
                'SELL',
                position.quantity,
                'MARKET'
            )
            
            # Wait for fill
            time.sleep(2)
            
            # Close position
            pnl = self.position_tracker.close_position(symbol, signal.price)
            if pnl is not None:
                self.positions_closed += 1
                self.current_capital += pnl
                
                self.logger.info(
                    f"Position closed: {symbol} | P&L: ${pnl:.2f}"
                )
                
                # Log position close
                self.trade_logger.log_position_close(
                    symbol,
                    'LONG',
                    position.quantity,
                    position.entry_price,
                    signal.price,
                    pnl
                )
                
                # Send alert
                self.alert_system.position_alert(
                    symbol,
                    'CLOSED',
                    position.quantity,
                    signal.price,
                    pnl
                )
    
    def _check_position_exits(self):
        """Check if any positions should be closed due to stop loss/take profit."""
        if not self.position_tracker:
            return
        
        exits = self.position_tracker.check_exit_conditions()
        
        for symbol, reason in exits:
            self.logger.info(f"Exit condition met for {symbol}: {reason}")
            
            position = self.position_tracker.get_position(symbol)
            if not position:
                continue
            
            # Create sell order
            order_request = OrderRequest(
                symbol=symbol,
                side=OrderSide.SELL,
                quantity=position.quantity,
                order_type=OrderType.MARKET,
                notes=reason
            )
            
            success, message = self.order_manager.submit_order(order_request)
            
            if success:
                time.sleep(2)
                
                # Close position
                pnl = self.position_tracker.close_position(
                    symbol,
                    position.current_price
                )
                
                if pnl is not None:
                    self.positions_closed += 1
                    self.current_capital += pnl
                    
                    self.logger.info(f"{reason} - Position closed: {symbol} | P&L: ${pnl:.2f}")
                    
                    # Send alert
                    self.alert_system.position_alert(
                        symbol,
                        'CLOSED',
                        position.quantity,
                        position.current_price,
                        pnl
                    )
    
    def _send_daily_summary(self):
        """Send end-of-day summary."""
        stats = {
            'signals': self.signals_generated,
            'orders': self.orders_placed,
            'positions_opened': self.positions_opened,
            'positions_closed': self.positions_closed,
            'open_positions': len(self.position_tracker.positions),
            'pnl': self.current_capital - self.initial_capital,
            'capital': self.current_capital
        }
        
        self.logger.info(f"Daily Summary: {stats}")
        self.alert_system.daily_summary(stats)
    
    def stop(self):
        """Stop the trading engine."""
        self.logger.info("Stopping trading engine...")
        self.is_running = False
        
        # Cancel all open orders
        if self.order_manager:
            cancelled = self.order_manager.cancel_all_orders()
            self.logger.info(f"Cancelled {cancelled} open orders")
        
        # Print final status
        self._print_status()
        
        # Disconnect from IB
        if self.ib and self.ib.isConnected():
            self.ib.disconnect()
        
        if self.order_manager:
            self.order_manager.disconnect()
        
        # Send shutdown alert
        self.alert_system.send_alert(
            "🛑 Trading System Stopped",
            alert_type=AlertType.SYSTEM,
            alert_level=AlertLevel.WARNING
        )
        
        self.logger.info("Trading engine stopped")
    
    def _print_status(self):
        """Print current status."""
        print("\n" + "="*60)
        print("LIVE TRADING ENGINE STATUS")
        print("="*60)
        print(f"Running: {self.is_running}")
        print(f"Market Hours: {self.is_market_hours}")
        print(f"Paper Trading: {self.paper_trading}")
        print(f"\nStatistics:")
        print(f"  Signals Generated: {self.signals_generated}")
        print(f"  Orders Placed: {self.orders_placed}")
        print(f"  Positions Opened: {self.positions_opened}")
        print(f"  Positions Closed: {self.positions_closed}")
        print(f"\nCapital:")
        print(f"  Initial: ${self.initial_capital:,.2f}")
        print(f"  Current: ${self.current_capital:,.2f}")
        print(f"  P&L: ${self.current_capital - self.initial_capital:,.2f}")
        print("="*60)
        
        # Print positions
        if self.position_tracker:
            self.position_tracker.print_positions()


if __name__ == "__main__":
    # Create and start live trading engine
    engine = LiveTradingEngine()
    engine.start()
