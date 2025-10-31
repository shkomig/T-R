"""
Backtesting Engine
==================
מנוע סימולציה היסטורית למסחר

מריץ אסטרטגיות על נתונים היסטוריים ומחשב ביצועים.
כולל:
- Order execution simulation
- Position tracking
- PnL calculation
- Slippage & commission
- Realistic fills
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import pandas as pd
import numpy as np
from enum import Enum

from strategies.base_strategy import BaseStrategy, TradingSignal, SignalType
from risk_management import PositionSizer, RiskCalculator


class OrderStatus(Enum):
    """סטטוס פקודה"""
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIAL = "PARTIAL"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass
class Order:
    """פקודת מסחר"""
    order_id: int
    timestamp: datetime
    symbol: str
    signal_type: SignalType
    quantity: int
    order_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_price: Optional[float] = None
    filled_quantity: int = 0
    filled_timestamp: Optional[datetime] = None
    commission: float = 0.0
    slippage: float = 0.0
    strategy_name: str = ""


@dataclass
class Position:
    """פוזיציה פתוחה"""
    symbol: str
    entry_time: datetime
    entry_price: float
    quantity: int
    stop_loss: float
    take_profit: float
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    strategy_name: str = ""
    
    def update_price(self, price: float):
        """עדכון מחיר נוכחי וחישוב PnL"""
        self.current_price = price
        self.unrealized_pnl = (price - self.entry_price) * self.quantity


@dataclass
class Trade:
    """מסחר שהושלם"""
    trade_id: int
    symbol: str
    strategy_name: str
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    quantity: int
    pnl: float
    pnl_percent: float
    commission: float
    duration: timedelta
    exit_reason: str = ""  # "stop_loss", "take_profit", "signal", "manual"
    
    def __post_init__(self):
        if not self.duration:
            self.duration = self.exit_time - self.entry_time


@dataclass
class BacktestState:
    """מצב נוכחי של הבקטסט"""
    current_time: datetime
    cash: float
    equity: float
    positions: Dict[str, Position] = field(default_factory=dict)
    pending_orders: List[Order] = field(default_factory=list)
    trades: List[Trade] = field(default_factory=list)
    equity_curve: List[Tuple[datetime, float]] = field(default_factory=list)
    
    def get_position_value(self) -> float:
        """ערך כל הפוזיציות"""
        return sum(pos.quantity * pos.current_price for pos in self.positions.values())
    
    def update_equity(self):
        """עדכון ערך התיק"""
        self.equity = self.cash + self.get_position_value()
        self.equity_curve.append((self.current_time, self.equity))


class BacktestEngine:
    """
    מנוע בקטסט מלא
    
    מאפשר להריץ אסטרטגיות על נתונים היסטוריים ולחשב ביצועים
    """
    
    def __init__(self, config: Dict):
        """
        אתחול מנוע
        
        Args:
            config: קונפיגורציה (risk_management + trading_config)
        """
        self.config = config
        
        # Initial capital
        self.initial_capital = config.get('account', {}).get('initial_capital', 100000)
        
        # Slippage & commission
        self.slippage_percent = config.get('slippage_percent', 0.05)  # 0.05%
        self.commission_per_share = config.get('commission_per_share', 0.005)  # $0.005
        self.min_commission = config.get('min_commission', 1.0)  # $1 minimum
        
        # Risk management
        self.position_sizer = PositionSizer(config.get('position_sizing', {}))
        self.risk_calculator = RiskCalculator(config)
        
        # State
        self.state: Optional[BacktestState] = None
        self.order_id_counter = 0
        self.trade_id_counter = 0
        
        # Results
        self.results: Optional[Dict] = None
        
    def run(
        self,
        strategies: List[BaseStrategy],
        data: Dict[str, pd.DataFrame],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        הרצת בקטסט
        
        Args:
            strategies: רשימת אסטרטגיות
            data: מילון של {symbol: DataFrame} עם נתונים היסטוריים
            start_date: תאריך התחלה (אופציונלי)
            end_date: תאריך סיום (אופציונלי)
            
        Returns:
            תוצאות הבקטסט
        """
        print("=" * 80)
        print("  Starting Backtest")
        print("=" * 80)
        
        # Initialize state
        self.state = BacktestState(
            current_time=datetime.now(),
            cash=self.initial_capital,
            equity=self.initial_capital
        )
        
        # Get all timestamps (union of all symbols)
        all_timestamps = self._get_all_timestamps(data, start_date, end_date)
        
        if len(all_timestamps) == 0:
            raise ValueError("No data available for backtesting")
        
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Strategies: {len(strategies)}")
        print(f"Symbols: {list(data.keys())}")
        print(f"Timeframe: {all_timestamps[0]} to {all_timestamps[-1]}")
        print(f"Total bars: {len(all_timestamps)}")
        print()
        
        # Main backtest loop
        for i, timestamp in enumerate(all_timestamps):
            self.state.current_time = timestamp
            
            # Update positions with current prices
            self._update_positions(data, timestamp)
            
            # Check stop loss / take profit
            self._check_exits(data, timestamp)
            
            # Process pending orders
            self._process_orders(data, timestamp)
            
            # Generate new signals from strategies
            for strategy in strategies:
                if not strategy.enabled:
                    continue
                
                for symbol, df in data.items():
                    # Get data up to current timestamp
                    historical_data = df[df.index <= timestamp]
                    
                    if len(historical_data) < 50:  # Need minimum bars
                        continue
                    
                    try:
                        # Analyze and generate signals
                        analyzed_data = strategy.analyze(historical_data)
                        signals = strategy.generate_signals(analyzed_data)
                        
                        # Process signals
                        for signal in signals:
                            if signal.timestamp == timestamp:
                                self._process_signal(signal, symbol, strategy)
                                
                    except Exception as e:
                        # Skip errors in strategy
                        continue
            
            # Update equity
            self.state.update_equity()
            
            # Progress
            if (i + 1) % 100 == 0:
                progress = (i + 1) / len(all_timestamps) * 100
                print(f"Progress: {progress:.1f}% - Equity: ${self.state.equity:,.2f}", end='\r')
        
        print()
        print("\nBacktest completed!")
        
        # Calculate results
        self.results = self._calculate_results()
        
        return self.results
    
    def _get_all_timestamps(
        self,
        data: Dict[str, pd.DataFrame],
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> List[datetime]:
        """קבלת כל הtimestamps מכל הסמלים"""
        all_times = set()
        
        for df in data.values():
            all_times.update(df.index.tolist())
        
        timestamps = sorted(list(all_times))
        
        # Filter by date range
        if start_date:
            timestamps = [t for t in timestamps if t >= start_date]
        if end_date:
            timestamps = [t for t in timestamps if t <= end_date]
        
        return timestamps
    
    def _update_positions(self, data: Dict[str, pd.DataFrame], timestamp: datetime):
        """עדכון מחירים של פוזיציות פתוחות"""
        for symbol, position in self.state.positions.items():
            if symbol in data:
                df = data[symbol]
                current_bar = df[df.index <= timestamp]
                
                if len(current_bar) > 0:
                    current_price = current_bar.iloc[-1]['close']
                    position.update_price(current_price)
    
    def _check_exits(self, data: Dict[str, pd.DataFrame], timestamp: datetime):
        """בדיקת Stop Loss / Take Profit"""
        symbols_to_close = []
        
        for symbol, position in self.state.positions.items():
            if symbol not in data:
                continue
            
            df = data[symbol]
            current_bar = df[df.index <= timestamp]
            
            if len(current_bar) == 0:
                continue
            
            bar = current_bar.iloc[-1]
            
            # Check stop loss
            if position.stop_loss and bar['low'] <= position.stop_loss:
                self._close_position(
                    symbol, position.stop_loss, timestamp, "stop_loss"
                )
                symbols_to_close.append(symbol)
                continue
            
            # Check take profit
            if position.take_profit and bar['high'] >= position.take_profit:
                self._close_position(
                    symbol, position.take_profit, timestamp, "take_profit"
                )
                symbols_to_close.append(symbol)
        
        # Remove closed positions
        for symbol in symbols_to_close:
            del self.state.positions[symbol]
    
    def _process_orders(self, data: Dict[str, pd.DataFrame], timestamp: datetime):
        """עיבוד פקודות ממתינות"""
        filled_orders = []
        
        for order in self.state.pending_orders:
            if order.symbol not in data:
                continue
            
            df = data[order.symbol]
            current_bar = df[df.index <= timestamp]
            
            if len(current_bar) == 0:
                continue
            
            bar = current_bar.iloc[-1]
            
            # Simple fill logic: use open price of next bar
            fill_price = bar['open']
            
            # Apply slippage
            if order.signal_type == SignalType.BUY:
                fill_price *= (1 + self.slippage_percent / 100)
            else:
                fill_price *= (1 - self.slippage_percent / 100)
            
            # Calculate commission
            commission = max(
                order.quantity * self.commission_per_share,
                self.min_commission
            )
            
            # Execute fill
            order.status = OrderStatus.FILLED
            order.filled_price = fill_price
            order.filled_quantity = order.quantity
            order.filled_timestamp = timestamp
            order.commission = commission
            order.slippage = abs(fill_price - order.order_price)
            
            # Update cash
            if order.signal_type == SignalType.BUY:
                total_cost = (fill_price * order.quantity) + commission
                self.state.cash -= total_cost
                
                # Create position
                self.state.positions[order.symbol] = Position(
                    symbol=order.symbol,
                    entry_time=timestamp,
                    entry_price=fill_price,
                    quantity=order.quantity,
                    stop_loss=order.stop_loss or 0,
                    take_profit=order.take_profit or 0,
                    current_price=fill_price,
                    strategy_name=order.strategy_name
                )
            
            filled_orders.append(order)
        
        # Remove filled orders
        self.state.pending_orders = [
            o for o in self.state.pending_orders if o not in filled_orders
        ]
    
    def _process_signal(self, signal: TradingSignal, symbol: str, strategy: BaseStrategy):
        """עיבוד סיגנל חדש"""
        # Check if we already have a position
        if symbol in self.state.positions:
            return  # Already in position
        
        # Calculate position size
        shares = self.position_sizer.calculate_position_size(
            account_balance=self.state.equity,
            entry_price=signal.price,
            stop_loss=signal.stop_loss or signal.price * 0.98
        )
        
        if shares <= 0:
            return
        
        # Check risk limits
        position_risk = shares * abs(signal.price - (signal.stop_loss or signal.price * 0.98))
        
        can_trade, reason = self.risk_calculator.can_open_new_position(
            current_balance=self.state.equity,
            open_positions=[
                {'shares': p.quantity, 'entry_price': p.entry_price, 'stop_loss': p.stop_loss}
                for p in self.state.positions.values()
            ],
            new_position_risk=position_risk
        )
        
        if not can_trade:
            return  # Risk limits exceeded
        
        # Check if we have enough cash
        required_cash = shares * signal.price * 1.01  # +1% buffer
        if required_cash > self.state.cash:
            shares = int(self.state.cash / (signal.price * 1.01))
            if shares <= 0:
                return
        
        # Create order
        order = Order(
            order_id=self._get_next_order_id(),
            timestamp=signal.timestamp,
            symbol=symbol,
            signal_type=signal.signal_type,
            quantity=shares,
            order_price=signal.price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            strategy_name=strategy.name
        )
        
        self.state.pending_orders.append(order)
    
    def _close_position(self, symbol: str, exit_price: float, timestamp: datetime, reason: str):
        """סגירת פוזיציה"""
        if symbol not in self.state.positions:
            return
        
        position = self.state.positions[symbol]
        
        # Calculate PnL
        pnl = (exit_price - position.entry_price) * position.quantity
        commission = max(position.quantity * self.commission_per_share, self.min_commission)
        pnl -= commission
        
        pnl_percent = ((exit_price - position.entry_price) / position.entry_price) * 100
        
        # Update cash
        self.state.cash += (exit_price * position.quantity) - commission
        
        # Record trade
        trade = Trade(
            trade_id=self._get_next_trade_id(),
            symbol=symbol,
            strategy_name=position.strategy_name,
            entry_time=position.entry_time,
            exit_time=timestamp,
            entry_price=position.entry_price,
            exit_price=exit_price,
            quantity=position.quantity,
            pnl=pnl,
            pnl_percent=pnl_percent,
            commission=commission,
            duration=timestamp - position.entry_time,
            exit_reason=reason
        )
        
        self.state.trades.append(trade)
    
    def _get_next_order_id(self) -> int:
        """ID הבא לפקודה"""
        self.order_id_counter += 1
        return self.order_id_counter
    
    def _get_next_trade_id(self) -> int:
        """ID הבא למסחר"""
        self.trade_id_counter += 1
        return self.trade_id_counter
    
    def _calculate_results(self) -> Dict:
        """חישוב תוצאות סופיות"""
        if not self.state:
            return {}
        
        # Close any remaining positions at last price
        for symbol in list(self.state.positions.keys()):
            position = self.state.positions[symbol]
            self._close_position(
                symbol, position.current_price, self.state.current_time, "end_of_backtest"
            )
            del self.state.positions[symbol]
        
        # Update final equity
        self.state.update_equity()
        
        # Basic metrics
        total_trades = len(self.state.trades)
        winning_trades = [t for t in self.state.trades if t.pnl > 0]
        losing_trades = [t for t in self.state.trades if t.pnl <= 0]
        
        total_pnl = sum(t.pnl for t in self.state.trades)
        total_return = ((self.state.equity - self.initial_capital) / self.initial_capital) * 100
        
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0
        
        profit_factor = (
            abs(sum(t.pnl for t in winning_trades) / sum(t.pnl for t in losing_trades))
            if losing_trades and sum(t.pnl for t in losing_trades) != 0
            else 0
        )
        
        # Calculate max drawdown
        equity_curve = pd.Series([e for _, e in self.state.equity_curve])
        running_max = equity_curve.expanding().max()
        drawdown = (equity_curve - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        results = {
            'initial_capital': self.initial_capital,
            'final_equity': self.state.equity,
            'total_pnl': total_pnl,
            'total_return_pct': total_return,
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown_pct': max_drawdown,
            'trades': self.state.trades,
            'equity_curve': self.state.equity_curve
        }
        
        return results
    
    def print_results(self):
        """הדפסת תוצאות"""
        if not self.results:
            print("No results available")
            return
        
        print("\n" + "=" * 80)
        print("  BACKTEST RESULTS")
        print("=" * 80)
        
        print(f"\nCapital:")
        print(f"  Initial:  ${self.results['initial_capital']:,.2f}")
        print(f"  Final:    ${self.results['final_equity']:,.2f}")
        print(f"  PnL:      ${self.results['total_pnl']:,.2f}")
        print(f"  Return:   {self.results['total_return_pct']:.2f}%")
        
        print(f"\nTrades:")
        print(f"  Total:    {self.results['total_trades']}")
        print(f"  Winners:  {self.results['winning_trades']}")
        print(f"  Losers:   {self.results['losing_trades']}")
        print(f"  Win Rate: {self.results['win_rate']:.2f}%")
        
        print(f"\nPerformance:")
        print(f"  Avg Win:       ${self.results['avg_win']:.2f}")
        print(f"  Avg Loss:      ${self.results['avg_loss']:.2f}")
        print(f"  Profit Factor: {self.results['profit_factor']:.2f}")
        print(f"  Max Drawdown:  {self.results['max_drawdown_pct']:.2f}%")
        
        print("=" * 80)
