"""
Position Tracker Module

Real-time tracking of open positions, P&L calculation, and position state management.

Author: Trading System
Date: October 29, 2025
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
from ib_insync import IB, Position as IBPosition, Stock
import yaml


class PositionSide(Enum):
    """Position side (long/short)."""
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass
class Position:
    """
    Represents an open position.
    """
    symbol: str
    quantity: int
    side: PositionSide
    entry_price: float
    entry_time: datetime
    
    # Current market data
    current_price: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)
    
    # P&L tracking
    unrealized_pnl: float = 0.0
    unrealized_pnl_percent: float = 0.0
    realized_pnl: float = 0.0
    total_pnl: float = 0.0
    
    # Risk management
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    trailing_stop: Optional[float] = None
    
    # Commission and costs
    entry_commission: float = 0.0
    total_commission: float = 0.0
    
    # Strategy info
    strategy_name: str = ""
    notes: str = ""
    
    # Tracking
    max_unrealized_pnl: float = 0.0
    min_unrealized_pnl: float = 0.0
    max_price: float = 0.0
    min_price: float = 0.0
    
    def __post_init__(self):
        """Initialize calculated fields."""
        if self.current_price == 0.0:
            self.current_price = self.entry_price
        
        self.max_price = self.entry_price
        self.min_price = self.entry_price
    
    def update_price(self, price: float):
        """
        Update current price and recalculate P&L.
        
        Args:
            price: New market price
        """
        self.current_price = price
        self.last_update = datetime.now()
        
        # Track price extremes
        self.max_price = max(self.max_price, price)
        self.min_price = min(self.min_price, price)
        
        # Calculate P&L
        if self.side == PositionSide.LONG:
            self.unrealized_pnl = (price - self.entry_price) * self.quantity
        else:  # SHORT
            self.unrealized_pnl = (self.entry_price - price) * self.quantity
        
        # Account for commissions
        self.unrealized_pnl -= self.total_commission
        
        # Calculate percentage
        self.unrealized_pnl_percent = (self.unrealized_pnl / (self.entry_price * self.quantity)) * 100
        
        # Track extremes
        self.max_unrealized_pnl = max(self.max_unrealized_pnl, self.unrealized_pnl)
        self.min_unrealized_pnl = min(self.min_unrealized_pnl, self.unrealized_pnl)
        
        # Total P&L (realized + unrealized)
        self.total_pnl = self.realized_pnl + self.unrealized_pnl
    
    def check_exit_conditions(self) -> Tuple[bool, str]:
        """
        Check if position should be closed based on stop loss or take profit.
        
        Returns:
            Tuple of (should_close, reason)
        """
        if self.side == PositionSide.LONG:
            # Check stop loss
            if self.stop_loss and self.current_price <= self.stop_loss:
                return True, f"Stop Loss hit: ${self.current_price:.2f} <= ${self.stop_loss:.2f}"
            
            # Check take profit
            if self.take_profit and self.current_price >= self.take_profit:
                return True, f"Take Profit hit: ${self.current_price:.2f} >= ${self.take_profit:.2f}"
            
            # Check trailing stop
            if self.trailing_stop:
                trail_price = self.max_price - self.trailing_stop
                if self.current_price <= trail_price:
                    return True, f"Trailing Stop hit: ${self.current_price:.2f} <= ${trail_price:.2f}"
        
        else:  # SHORT
            # Check stop loss
            if self.stop_loss and self.current_price >= self.stop_loss:
                return True, f"Stop Loss hit: ${self.current_price:.2f} >= ${self.stop_loss:.2f}"
            
            # Check take profit
            if self.take_profit and self.current_price <= self.take_profit:
                return True, f"Take Profit hit: ${self.current_price:.2f} <= ${self.take_profit:.2f}"
            
            # Check trailing stop
            if self.trailing_stop:
                trail_price = self.min_price + self.trailing_stop
                if self.current_price >= trail_price:
                    return True, f"Trailing Stop hit: ${self.current_price:.2f} >= ${trail_price:.2f}"
        
        return False, ""
    
    def close(self, exit_price: float, exit_commission: float = 0.0) -> float:
        """
        Close the position and calculate final P&L.
        
        Args:
            exit_price: Exit price
            exit_commission: Commission on exit
            
        Returns:
            Total realized P&L
        """
        # Final P&L calculation
        if self.side == PositionSide.LONG:
            pnl = (exit_price - self.entry_price) * self.quantity
        else:
            pnl = (self.entry_price - exit_price) * self.quantity
        
        # Subtract all commissions
        total_commission = self.entry_commission + exit_commission
        pnl -= total_commission
        
        self.realized_pnl = pnl
        self.total_commission = total_commission
        
        return pnl
    
    def to_dict(self) -> Dict:
        """Convert position to dictionary."""
        return {
            'symbol': self.symbol,
            'quantity': self.quantity,
            'side': self.side.value,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'unrealized_pnl': self.unrealized_pnl,
            'unrealized_pnl_percent': self.unrealized_pnl_percent,
            'realized_pnl': self.realized_pnl,
            'total_pnl': self.total_pnl,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'strategy_name': self.strategy_name,
            'entry_time': self.entry_time.strftime('%Y-%m-%d %H:%M:%S'),
            'holding_period': str(datetime.now() - self.entry_time)
        }


class PositionTracker:
    """
    Tracks all open positions and manages position lifecycle.
    
    Features:
    - Real-time position tracking
    - P&L calculation and monitoring
    - Stop loss / Take profit monitoring
    - Position statistics
    """
    
    def __init__(self, config_path: str = "config/trading_config.yaml"):
        """
        Initialize Position Tracker.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Position tracking
        self.positions: Dict[str, Position] = {}  # symbol -> Position
        self.closed_positions: List[Position] = []
        
        # IB connection (optional, for syncing with broker)
        self.ib: Optional[IB] = None
        self.auto_sync = False
        
        # Statistics
        self.total_realized_pnl = 0.0
        self.total_unrealized_pnl = 0.0
        self.total_commission = 0.0
        
        self.logger.info("PositionTracker initialized")
    
    def connect_ib(self, ib: IB, auto_sync: bool = True):
        """
        Connect to IB instance for automatic position syncing.
        
        Args:
            ib: IB connection instance
            auto_sync: Automatically sync positions from broker
        """
        self.ib = ib
        self.auto_sync = auto_sync
        
        if auto_sync:
            self.sync_positions_from_broker()
    
    def sync_positions_from_broker(self) -> int:
        """
        Sync positions from broker.
        
        Returns:
            Number of positions synced
        """
        if not self.ib:
            self.logger.warning("IB connection not available for syncing")
            return 0
        
        try:
            ib_positions = self.ib.positions()
            synced = 0
            
            for ib_pos in ib_positions:
                symbol = ib_pos.contract.symbol
                quantity = int(ib_pos.position)
                avg_cost = ib_pos.avgCost
                
                if quantity == 0:
                    continue
                
                # Check if we already track this position
                if symbol not in self.positions:
                    # Create new position
                    side = PositionSide.LONG if quantity > 0 else PositionSide.SHORT
                    position = Position(
                        symbol=symbol,
                        quantity=abs(quantity),
                        side=side,
                        entry_price=avg_cost,
                        entry_time=datetime.now(),
                        strategy_name="Synced from Broker"
                    )
                    self.positions[symbol] = position
                    synced += 1
                    
                    self.logger.info(f"Synced position from broker: {symbol} {quantity}@${avg_cost:.2f}")
            
            return synced
            
        except Exception as e:
            self.logger.error(f"Failed to sync positions from broker: {e}")
            return 0
    
    def open_position(self, position: Position):
        """
        Open a new position.
        
        Args:
            position: Position object
        """
        if position.symbol in self.positions:
            self.logger.warning(f"Position for {position.symbol} already exists")
            return
        
        self.positions[position.symbol] = position
        self.logger.info(
            f"Opened position: {position.side.value} {position.quantity} {position.symbol} "
            f"@ ${position.entry_price:.2f}"
        )
    
    def close_position(self, symbol: str, exit_price: float, 
                      exit_commission: float = 0.0) -> Optional[float]:
        """
        Close a position.
        
        Args:
            symbol: Symbol to close
            exit_price: Exit price
            exit_commission: Commission on exit
            
        Returns:
            Realized P&L or None if position not found
        """
        if symbol not in self.positions:
            self.logger.warning(f"No position found for {symbol}")
            return None
        
        position = self.positions[symbol]
        pnl = position.close(exit_price, exit_commission)
        
        # Update statistics
        self.total_realized_pnl += pnl
        self.total_commission += position.total_commission
        
        # Move to closed positions
        self.closed_positions.append(position)
        del self.positions[symbol]
        
        self.logger.info(
            f"Closed position: {position.side.value} {position.quantity} {symbol} "
            f"@ ${exit_price:.2f} | P&L: ${pnl:.2f}"
        )
        
        return pnl
    
    def update_price(self, symbol: str, price: float):
        """
        Update position price and recalculate P&L.
        
        Args:
            symbol: Symbol to update
            price: New price
        """
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        position.update_price(price)
    
    def update_all_prices(self, prices: Dict[str, float]):
        """
        Update prices for all positions.
        
        Args:
            prices: Dictionary of symbol -> price
        """
        for symbol, price in prices.items():
            self.update_price(symbol, price)
        
        # Recalculate total unrealized P&L
        self.total_unrealized_pnl = sum(
            pos.unrealized_pnl for pos in self.positions.values()
        )
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """
        Get position for a symbol.
        
        Args:
            symbol: Symbol
            
        Returns:
            Position or None
        """
        return self.positions.get(symbol)
    
    def has_position(self, symbol: str) -> bool:
        """
        Check if position exists for symbol.
        
        Args:
            symbol: Symbol
            
        Returns:
            True if position exists
        """
        return symbol in self.positions
    
    def get_all_positions(self) -> List[Position]:
        """Get list of all open positions."""
        return list(self.positions.values())
    
    def get_positions_by_strategy(self, strategy_name: str) -> List[Position]:
        """
        Get positions for a specific strategy.
        
        Args:
            strategy_name: Strategy name
            
        Returns:
            List of positions
        """
        return [pos for pos in self.positions.values() 
                if pos.strategy_name == strategy_name]
    
    def check_exit_conditions(self) -> List[Tuple[str, str]]:
        """
        Check all positions for exit conditions.
        
        Returns:
            List of (symbol, reason) tuples for positions that should close
        """
        exits = []
        
        for symbol, position in self.positions.items():
            should_close, reason = position.check_exit_conditions()
            if should_close:
                exits.append((symbol, reason))
        
        return exits
    
    def get_total_exposure(self) -> float:
        """
        Calculate total market exposure (position value).
        
        Returns:
            Total exposure in dollars
        """
        total = 0.0
        for position in self.positions.values():
            total += position.current_price * position.quantity
        return total
    
    def get_net_exposure(self) -> float:
        """
        Calculate net exposure (long - short).
        
        Returns:
            Net exposure in dollars
        """
        net = 0.0
        for position in self.positions.values():
            value = position.current_price * position.quantity
            if position.side == PositionSide.LONG:
                net += value
            else:
                net -= value
        return net
    
    def get_statistics(self) -> Dict:
        """
        Get position tracker statistics.
        
        Returns:
            Dictionary of statistics
        """
        open_positions = len(self.positions)
        closed_positions = len(self.closed_positions)
        
        # Calculate total unrealized P&L
        total_unrealized = sum(pos.unrealized_pnl for pos in self.positions.values())
        
        # Count winning/losing positions
        winning = sum(1 for pos in self.positions.values() if pos.unrealized_pnl > 0)
        losing = sum(1 for pos in self.positions.values() if pos.unrealized_pnl < 0)
        
        # Exposure calculations
        total_exposure = self.get_total_exposure()
        net_exposure = self.get_net_exposure()
        
        # Calculate win rate
        total_closed = len(self.closed_positions)
        winning_closed = sum(1 for pos in self.closed_positions if pos.realized_pnl > 0)
        win_rate = (winning_closed / total_closed * 100) if total_closed > 0 else 0
        
        return {
            'open_positions': open_positions,
            'closed_positions': closed_positions,
            'winning_positions': winning,
            'losing_positions': losing,
            'total_unrealized_pnl': total_unrealized,
            'total_realized_pnl': self.total_realized_pnl,
            'total_pnl': self.total_realized_pnl + total_unrealized,
            'total_commission': self.total_commission,
            'total_exposure': total_exposure,
            'net_exposure': net_exposure,
            'win_rate': win_rate
        }
    
    def get_positions_df(self) -> pd.DataFrame:
        """
        Get all positions as a DataFrame.
        
        Returns:
            DataFrame with position information
        """
        if not self.positions:
            return pd.DataFrame()
        
        data = [pos.to_dict() for pos in self.positions.values()]
        df = pd.DataFrame(data)
        
        # Sort by unrealized P&L
        df = df.sort_values('unrealized_pnl', ascending=False)
        
        return df
    
    def print_positions(self):
        """Print all open positions."""
        if not self.positions:
            print("\nNo open positions")
            return
        
        print("\n=== OPEN POSITIONS ===")
        print(f"{'Symbol':<10} {'Side':<6} {'Qty':<8} {'Entry':<10} {'Current':<10} "
              f"{'P&L $':<12} {'P&L %':<10}")
        print("-" * 80)
        
        for position in sorted(self.positions.values(), 
                              key=lambda p: p.unrealized_pnl, reverse=True):
            pnl_color = '+' if position.unrealized_pnl >= 0 else ''
            print(
                f"{position.symbol:<10} {position.side.value:<6} "
                f"{position.quantity:<8} ${position.entry_price:<9.2f} "
                f"${position.current_price:<9.2f} "
                f"{pnl_color}${position.unrealized_pnl:<11.2f} "
                f"{pnl_color}{position.unrealized_pnl_percent:<9.2f}%"
            )
        
        print("-" * 80)
        
        # Print summary
        stats = self.get_statistics()
        print(f"\nTotal Positions: {stats['open_positions']}")
        print(f"Winning: {stats['winning_positions']} | Losing: {stats['losing_positions']}")
        print(f"Total Unrealized P&L: ${stats['total_unrealized_pnl']:,.2f}")
        print(f"Total Realized P&L: ${stats['total_realized_pnl']:,.2f}")
        print(f"Total P&L: ${stats['total_pnl']:,.2f}")
        print(f"Total Exposure: ${stats['total_exposure']:,.2f}")
        print(f"Net Exposure: ${stats['net_exposure']:,.2f}")
        print("=" * 80)
    
    def print_summary(self):
        """Print summary statistics."""
        stats = self.get_statistics()
        
        print("\n=== POSITION TRACKER SUMMARY ===")
        print(f"Open Positions: {stats['open_positions']}")
        print(f"Closed Positions: {stats['closed_positions']}")
        print(f"Total Unrealized P&L: ${stats['total_unrealized_pnl']:,.2f}")
        print(f"Total Realized P&L: ${stats['total_realized_pnl']:,.2f}")
        print(f"Total P&L: ${stats['total_pnl']:,.2f}")
        print(f"Total Commission: ${stats['total_commission']:,.2f}")
        print(f"Total Exposure: ${stats['total_exposure']:,.2f}")
        print("=" * 30)
