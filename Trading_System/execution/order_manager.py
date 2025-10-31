"""
Order Manager Module

Handles order creation, submission, tracking, and management for live trading.
Includes retry logic, error handling, and order state management.

Author: Trading System
Date: October 29, 2025
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import time
from ib_insync import IB, Order, Trade, OrderStatus as IBOrderStatus
from ib_insync import Stock, MarketOrder, LimitOrder, StopOrder
import yaml


class OrderType(Enum):
    """Order types supported by the system."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderSide(Enum):
    """Order side (buy/sell)."""
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(Enum):
    """Order status in the system."""
    PENDING = "PENDING"          # Created but not submitted
    SUBMITTED = "SUBMITTED"      # Submitted to broker
    FILLED = "FILLED"            # Fully filled
    PARTIALLY_FILLED = "PARTIALLY_FILLED"  # Partially filled
    CANCELLED = "CANCELLED"      # Cancelled by user
    REJECTED = "REJECTED"        # Rejected by broker
    FAILED = "FAILED"            # Failed to submit


@dataclass
class OrderRequest:
    """Order request from strategy."""
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType = OrderType.MARKET
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "DAY"
    strategy_name: str = ""
    notes: str = ""
    
    # Stop loss and take profit levels (optional)
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    submitted_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    
    # Status tracking
    status: OrderStatus = OrderStatus.PENDING
    ib_order_id: Optional[int] = None
    filled_quantity: int = 0
    avg_fill_price: Optional[float] = None
    
    # Error tracking
    error_message: str = ""
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class OrderFill:
    """Order fill information."""
    order_id: int
    symbol: str
    quantity: int
    price: float
    commission: float
    timestamp: datetime
    side: OrderSide


class OrderManager:
    """
    Manages order lifecycle from creation to fill/cancel.
    
    Features:
    - Order queue management
    - Automatic retry on failures
    - Order status tracking
    - Fill notifications
    - Error handling
    """
    
    def __init__(self, config_path: str = "config/trading_config.yaml"):
        """
        Initialize Order Manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Interactive Brokers connection
        self.ib: Optional[IB] = None
        self.is_connected = False
        
        # Order tracking
        self.pending_orders: Dict[str, OrderRequest] = {}  # symbol -> order
        self.active_orders: Dict[int, OrderRequest] = {}   # ib_order_id -> order
        self.filled_orders: List[OrderFill] = []
        self.cancelled_orders: List[OrderRequest] = []
        
        # Configuration
        self.retry_delay = 2  # seconds
        self.max_retries = 3
        self.order_timeout = 60  # seconds
        
        self.logger.info("OrderManager initialized")
    
    def connect(self, host: str = '127.0.0.1', port: int = 7497, client_id: int = 1) -> bool:
        """
        Connect to Interactive Brokers.
        
        Args:
            host: IB Gateway host
            port: IB Gateway port (7497 for paper, 7496 for live)
            client_id: Client ID
            
        Returns:
            True if connected successfully
        """
        try:
            self.ib = IB()
            self.ib.connect(host, port, clientId=client_id)
            self.is_connected = True
            
            # Set up event handlers
            self.ib.orderStatusEvent += self._on_order_status
            self.ib.execDetailsEvent += self._on_execution
            self.ib.errorEvent += self._on_error
            
            self.logger.info(f"Connected to IB Gateway at {host}:{port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to IB: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from Interactive Brokers."""
        if self.ib and self.is_connected:
            self.ib.disconnect()
            self.is_connected = False
            self.logger.info("Disconnected from IB Gateway")
    
    def submit_order(self, order_request: OrderRequest) -> Tuple[bool, str]:
        """
        Submit an order to the broker.
        
        Args:
            order_request: Order request to submit
            
        Returns:
            Tuple of (success, message)
        """
        if not self.is_connected:
            return False, "Not connected to broker"
        
        try:
            # Create IB contract
            contract = Stock(order_request.symbol, 'SMART', 'USD')
            
            # Create IB order based on type
            ib_order = self._create_ib_order(order_request)
            
            # Submit order
            trade = self.ib.placeOrder(contract, ib_order)
            
            # Update order request
            order_request.status = OrderStatus.SUBMITTED
            order_request.submitted_at = datetime.now()
            order_request.ib_order_id = trade.order.orderId
            
            # Track order
            self.active_orders[trade.order.orderId] = order_request
            if order_request.symbol in self.pending_orders:
                del self.pending_orders[order_request.symbol]
            
            self.logger.info(
                f"Order submitted: {order_request.side.value} {order_request.quantity} "
                f"{order_request.symbol} @ {order_request.order_type.value} "
                f"(Order ID: {trade.order.orderId})"
            )
            
            return True, f"Order submitted with ID {trade.order.orderId}"
            
        except Exception as e:
            error_msg = f"Failed to submit order: {e}"
            self.logger.error(error_msg)
            order_request.status = OrderStatus.FAILED
            order_request.error_message = error_msg
            
            # Retry if not exceeded max retries
            if order_request.retry_count < order_request.max_retries:
                order_request.retry_count += 1
                self.pending_orders[order_request.symbol] = order_request
                self.logger.warning(
                    f"Will retry order submission (attempt {order_request.retry_count}/"
                    f"{order_request.max_retries})"
                )
            
            return False, error_msg
    
    def _create_ib_order(self, order_request: OrderRequest) -> Order:
        """
        Create Interactive Brokers order object.
        
        Args:
            order_request: Order request
            
        Returns:
            IB Order object
        """
        action = 'BUY' if order_request.side == OrderSide.BUY else 'SELL'
        
        if order_request.order_type == OrderType.MARKET:
            ib_order = MarketOrder(action, order_request.quantity)
            
        elif order_request.order_type == OrderType.LIMIT:
            if order_request.limit_price is None:
                raise ValueError("Limit price required for LIMIT order")
            ib_order = LimitOrder(action, order_request.quantity, order_request.limit_price)
            
        elif order_request.order_type == OrderType.STOP:
            if order_request.stop_price is None:
                raise ValueError("Stop price required for STOP order")
            ib_order = StopOrder(action, order_request.quantity, order_request.stop_price)
            
        else:
            raise ValueError(f"Unsupported order type: {order_request.order_type}")
        
        # Set time in force
        ib_order.tif = order_request.time_in_force
        
        # Set transmit (send to exchange immediately)
        ib_order.transmit = True
        
        return ib_order
    
    def cancel_order(self, order_id: int) -> Tuple[bool, str]:
        """
        Cancel an active order.
        
        Args:
            order_id: IB order ID
            
        Returns:
            Tuple of (success, message)
        """
        if not self.is_connected:
            return False, "Not connected to broker"
        
        if order_id not in self.active_orders:
            return False, f"Order {order_id} not found in active orders"
        
        try:
            # Find the trade
            trade = None
            for t in self.ib.trades():
                if t.order.orderId == order_id:
                    trade = t
                    break
            
            if trade is None:
                return False, f"Trade for order {order_id} not found"
            
            # Cancel the order
            self.ib.cancelOrder(trade.order)
            
            # Update status
            order_request = self.active_orders[order_id]
            order_request.status = OrderStatus.CANCELLED
            
            # Move to cancelled orders
            self.cancelled_orders.append(order_request)
            del self.active_orders[order_id]
            
            self.logger.info(f"Order {order_id} cancelled")
            return True, f"Order {order_id} cancelled"
            
        except Exception as e:
            error_msg = f"Failed to cancel order {order_id}: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def cancel_all_orders(self) -> int:
        """
        Cancel all active orders.
        
        Returns:
            Number of orders cancelled
        """
        order_ids = list(self.active_orders.keys())
        cancelled = 0
        
        for order_id in order_ids:
            success, _ = self.cancel_order(order_id)
            if success:
                cancelled += 1
        
        return cancelled
    
    def get_order_status(self, order_id: int) -> Optional[OrderStatus]:
        """
        Get status of an order.
        
        Args:
            order_id: IB order ID
            
        Returns:
            OrderStatus or None if not found
        """
        if order_id in self.active_orders:
            return self.active_orders[order_id].status
        
        # Check filled orders
        for fill in self.filled_orders:
            if fill.order_id == order_id:
                return OrderStatus.FILLED
        
        # Check cancelled orders
        for order in self.cancelled_orders:
            if order.ib_order_id == order_id:
                return order.status
        
        return None
    
    def get_active_orders(self, symbol: Optional[str] = None) -> List[OrderRequest]:
        """
        Get list of active orders.
        
        Args:
            symbol: Filter by symbol (optional)
            
        Returns:
            List of active order requests
        """
        orders = list(self.active_orders.values())
        
        if symbol:
            orders = [o for o in orders if o.symbol == symbol]
        
        return orders
    
    def get_filled_orders(self, symbol: Optional[str] = None) -> List[OrderFill]:
        """
        Get list of filled orders.
        
        Args:
            symbol: Filter by symbol (optional)
            
        Returns:
            List of order fills
        """
        fills = self.filled_orders
        
        if symbol:
            fills = [f for f in fills if f.symbol == symbol]
        
        return fills
    
    def process_pending_orders(self):
        """Process pending orders that need retry."""
        symbols_to_process = list(self.pending_orders.keys())
        
        for symbol in symbols_to_process:
            order_request = self.pending_orders[symbol]
            
            # Check if enough time has passed for retry
            if order_request.status == OrderStatus.FAILED:
                time_since_failure = (datetime.now() - order_request.created_at).total_seconds()
                
                if time_since_failure >= self.retry_delay:
                    self.logger.info(f"Retrying order for {symbol}")
                    self.submit_order(order_request)
    
    def _on_order_status(self, trade: Trade):
        """
        Event handler for order status updates.
        
        Args:
            trade: IB Trade object
        """
        order_id = trade.order.orderId
        
        if order_id not in self.active_orders:
            return
        
        order_request = self.active_orders[order_id]
        ib_status = trade.orderStatus.status
        
        self.logger.info(
            f"Order {order_id} status: {ib_status} "
            f"(Filled: {trade.orderStatus.filled}/{order_request.quantity})"
        )
        
        # Update order status
        if ib_status == 'Filled':
            order_request.status = OrderStatus.FILLED
            order_request.filled_quantity = trade.orderStatus.filled
            order_request.filled_at = datetime.now()
            
        elif ib_status == 'PartiallyFilled':
            order_request.status = OrderStatus.PARTIALLY_FILLED
            order_request.filled_quantity = trade.orderStatus.filled
            
        elif ib_status == 'Cancelled':
            order_request.status = OrderStatus.CANCELLED
            
        elif ib_status in ['Rejected', 'Error']:
            order_request.status = OrderStatus.REJECTED
            order_request.error_message = trade.orderStatus.whyHeld or "Unknown error"
    
    def _on_execution(self, trade: Trade, fill):
        """
        Event handler for order executions.
        
        Args:
            trade: IB Trade object
            fill: Fill details
        """
        order_id = trade.order.orderId
        
        if order_id not in self.active_orders:
            return
        
        order_request = self.active_orders[order_id]
        
        # Create fill record
        order_fill = OrderFill(
            order_id=order_id,
            symbol=order_request.symbol,
            quantity=fill.execution.shares,
            price=fill.execution.price,
            commission=fill.commissionReport.commission if fill.commissionReport else 0,
            timestamp=datetime.now(),
            side=order_request.side
        )
        
        self.filled_orders.append(order_fill)
        
        # Update average fill price
        if order_request.avg_fill_price is None:
            order_request.avg_fill_price = fill.execution.price
        else:
            # Weighted average
            total_filled = order_request.filled_quantity + fill.execution.shares
            order_request.avg_fill_price = (
                (order_request.avg_fill_price * order_request.filled_quantity +
                 fill.execution.price * fill.execution.shares) / total_filled
            )
        
        self.logger.info(
            f"Order {order_id} execution: {fill.execution.shares} shares @ "
            f"${fill.execution.price:.2f} (Commission: ${order_fill.commission:.2f})"
        )
        
        # If fully filled, remove from active orders
        if order_request.status == OrderStatus.FILLED:
            del self.active_orders[order_id]
            self.logger.info(f"Order {order_id} fully filled")
    
    def _on_error(self, reqId: int, errorCode: int, errorString: str, contract):
        """
        Event handler for errors.
        
        Args:
            reqId: Request ID
            errorCode: Error code
            errorString: Error message
            contract: Contract (if applicable)
        """
        # Filter out informational messages
        if errorCode in [2104, 2106, 2158]:  # Market data farm connection messages
            return
        
        self.logger.warning(f"IB Error {errorCode}: {errorString} (ReqId: {reqId})")
        
        # Update order status if this is an order error
        if reqId in self.active_orders:
            order_request = self.active_orders[reqId]
            order_request.error_message = f"{errorCode}: {errorString}"
            
            # Mark as failed if serious error
            if errorCode >= 200:  # Order errors start at 200
                order_request.status = OrderStatus.FAILED
    
    def get_statistics(self) -> Dict:
        """
        Get order manager statistics.
        
        Returns:
            Dictionary of statistics
        """
        total_filled = len(self.filled_orders)
        total_active = len(self.active_orders)
        total_cancelled = len(self.cancelled_orders)
        total_pending = len(self.pending_orders)
        
        # Calculate total volume and commission
        total_volume = sum(f.quantity * f.price for f in self.filled_orders)
        total_commission = sum(f.commission for f in self.filled_orders)
        
        return {
            'active_orders': total_active,
            'pending_orders': total_pending,
            'filled_orders': total_filled,
            'cancelled_orders': total_cancelled,
            'total_volume': total_volume,
            'total_commission': total_commission,
            'is_connected': self.is_connected
        }
    
    def print_status(self):
        """Print current order manager status."""
        stats = self.get_statistics()
        
        print("\n=== ORDER MANAGER STATUS ===")
        print(f"Connected: {stats['is_connected']}")
        print(f"Active Orders: {stats['active_orders']}")
        print(f"Pending Orders: {stats['pending_orders']}")
        print(f"Filled Orders: {stats['filled_orders']}")
        print(f"Cancelled Orders: {stats['cancelled_orders']}")
        print(f"Total Volume: ${stats['total_volume']:,.2f}")
        print(f"Total Commission: ${stats['total_commission']:,.2f}")
        print("="*30)
