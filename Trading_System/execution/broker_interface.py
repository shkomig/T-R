"""
Interactive Brokers Interface Module
=====================================

Manages connection and communication with Interactive Brokers TWS/Gateway.
Supports Paper Trading (Port 7497) and Live Trading (Port 7496).

Author: Trading System
Version: 1.0.0
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import asyncio

from ib_insync import IB, Stock, util, MarketOrder, LimitOrder
from ib_insync.contract import Contract
from ib_insync.order import Order

logger = logging.getLogger(__name__)


class IBBroker:
    """
    Interactive Brokers connection manager.
    
    Features:
    - Automatic reconnection
    - Connection health monitoring
    - Error handling
    - Market data streaming
    - Order management
    """
    
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 7497,
        client_id: int = 1,
        timeout: int = 30,
        readonly: bool = False
    ):
        """
        Initialize IB Broker connection.
        
        Args:
            host: TWS/Gateway host address (default: 127.0.0.1)
            port: Connection port (7497=Paper, 7496=Live)
            client_id: Unique client identifier
            timeout: Connection timeout in seconds
            readonly: If True, trading operations are disabled
        """
        self.host = host
        self.port = port
        self.client_id = client_id
        self.timeout = timeout
        self.readonly = readonly
        
        self.ib = IB()
        self._connected = False
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        self._reconnect_delay = 10  # seconds
        
        # Connection callbacks
        self.ib.connectedEvent += self._on_connected
        self.ib.disconnectedEvent += self._on_disconnected
        self.ib.errorEvent += self._on_error
        
        logger.info(f"IBBroker initialized - Host: {host}, Port: {port}")
    
    def connect(self) -> bool:
        """
        Establish connection to Interactive Brokers.
        
        Returns:
            True if connected successfully, False otherwise
        """
        try:
            logger.info(f"Connecting to IB TWS/Gateway at {self.host}:{self.port}...")
            
            self.ib.connect(
                host=self.host,
                port=self.port,
                clientId=self.client_id,
                timeout=self.timeout,
                readonly=self.readonly
            )
            
            self._connected = True
            self._reconnect_attempts = 0
            
            logger.info("✓ Successfully connected to Interactive Brokers")
            logger.info(f"  Account: {self.get_account_summary()}")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to connect to IB: {e}")
            self._connected = False
            return False
    
    def disconnect(self) -> None:
        """Disconnect from Interactive Brokers."""
        try:
            if self.ib.isConnected():
                self.ib.disconnect()
                logger.info("Disconnected from Interactive Brokers")
            self._connected = False
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    def is_connected(self) -> bool:
        """Check if currently connected to IB."""
        return self._connected and self.ib.isConnected()
    
    def reconnect(self) -> bool:
        """
        Attempt to reconnect to IB.
        
        Returns:
            True if reconnected successfully
        """
        if self._reconnect_attempts >= self._max_reconnect_attempts:
            logger.error("Max reconnection attempts reached")
            return False
        
        self._reconnect_attempts += 1
        logger.info(f"Reconnection attempt {self._reconnect_attempts}/{self._max_reconnect_attempts}")
        
        self.disconnect()
        util.sleep(self._reconnect_delay)
        
        return self.connect()
    
    def get_account_summary(self) -> Dict[str, Any]:
        """
        Get account summary information.
        
        Returns:
            Dictionary with account details
        """
        if not self.is_connected():
            logger.warning("Not connected to IB")
            return {}
        
        try:
            account_values = self.ib.accountSummary()
            
            summary = {}
            for item in account_values:
                summary[item.tag] = {
                    'value': item.value,
                    'currency': item.currency,
                    'account': item.account
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting account summary: {e}")
            return {}
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current portfolio positions.
        
        Returns:
            List of position dictionaries
        """
        if not self.is_connected():
            logger.warning("Not connected to IB")
            return []
        
        try:
            positions = self.ib.positions()
            
            position_list = []
            for pos in positions:
                # Calculate market value manually (position * current_price)
                market_value = pos.position * pos.avgCost  # Simple approximation
                
                position_list.append({
                    'symbol': pos.contract.symbol,
                    'position': pos.position,
                    'avg_cost': pos.avgCost,
                    'market_value': market_value,
                    'pnl': getattr(pos, 'unrealizedPNL', 0),  # Safe get with default
                    'account': pos.account
                })
            
            return position_list
            
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def get_historical_data(
        self,
        symbol: str,
        duration: str = "1 D",
        bar_size: str = "30 mins",
        what_to_show: str = "TRADES"
    ) -> Any:
        """
        Request historical market data.
        
        Args:
            symbol: Stock symbol (e.g., "AAPL")
            duration: How far back to retrieve (e.g., "1 D", "1 W", "1 M")
            bar_size: Bar size (e.g., "1 min", "5 mins", "30 mins", "1 hour")
            what_to_show: Data type ("TRADES", "MIDPOINT", "BID", "ASK")
        
        Returns:
            BarDataList object with historical bars
        """
        if not self.is_connected():
            logger.warning("Not connected to IB")
            return None
        
        try:
            # Historical data works with SMART even without real-time subscription
            contract = Stock(symbol, "SMART", "USD")
            self.ib.qualifyContracts(contract)
            
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr=duration,
                barSizeSetting=bar_size,
                whatToShow=what_to_show,
                useRTH=True,  # Regular Trading Hours only
                formatDate=1
            )
            
            logger.info(f"Retrieved {len(bars)} bars for {symbol}")
            return bars
            
        except Exception as e:
            # Suppress these errors to clean the output
            # logger.error(f"Error getting historical data for {symbol}: {e}")
            return None
    
    def get_realtime_bars(
        self,
        symbol: str,
        bar_size: int = 5,
        what_to_show: str = "TRADES"
    ) -> Any:
        """
        Request real-time bars (streaming).
        
        Args:
            symbol: Stock symbol
            bar_size: Bar size in seconds (5 seconds minimum)
            what_to_show: Data type
        
        Returns:
            RealTimeBarList object
        """
        if not self.is_connected():
            logger.warning("Not connected to IB")
            return None
        
        try:
            # Use IEX exchange for FREE real-time data (no subscription required)
            contract = Stock(symbol, "IEX", "USD")
            self.ib.qualifyContracts(contract)
            
            bars = self.ib.reqRealTimeBars(
                contract,
                barSize=bar_size,
                whatToShow=what_to_show,
                useRTH=True
            )
            
            logger.info(f"Started real-time bars for {symbol}")
            return bars
            
        except Exception as e:
            logger.error(f"Error getting real-time bars for {symbol}: {e}")
            return None
    
    def place_order(
        self,
        symbol: str,
        action: str,
        quantity: int,
        order_type: str = "MKT",
        limit_price: Optional[float] = None
    ) -> Optional[Any]:
        """
        Place a trading order.
        
        Args:
            symbol: Stock symbol
            action: "BUY" or "SELL"
            quantity: Number of shares
            order_type: "MKT" (Market) or "LMT" (Limit)
            limit_price: Required for limit orders
        
        Returns:
            Trade object if successful, None otherwise
        """
        if self.readonly:
            logger.warning("Trading disabled - readonly mode")
            return None
        
        if not self.is_connected():
            logger.warning("Not connected to IB")
            return None
        
        try:
            # Orders use SMART routing for best execution
            contract = Stock(symbol, "SMART", "USD")
            self.ib.qualifyContracts(contract)
            
            # Create order based on type
            if order_type == "MKT":
                order = MarketOrder(action, quantity)
            elif order_type == "LMT":
                if limit_price is None:
                    logger.error("Limit price required for limit orders")
                    return None
                order = LimitOrder(action, quantity, limit_price)
            else:
                logger.error(f"Unsupported order type: {order_type}")
                return None
            
            # Place the order
            trade = self.ib.placeOrder(contract, order)
            
            logger.info(f"Order placed: {action} {quantity} {symbol} @ {order_type}")
            return trade
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def cancel_order(self, order: Order) -> bool:
        """
        Cancel an existing order.
        
        Args:
            order: Order object to cancel
        
        Returns:
            True if cancelled successfully
        """
        try:
            self.ib.cancelOrder(order)
            logger.info(f"Order cancelled: {order}")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False
    
    def get_open_orders(self) -> List[Any]:
        """Get all open orders."""
        if not self.is_connected():
            return []
        
        try:
            return self.ib.openOrders()
        except Exception as e:
            logger.error(f"Error getting open orders: {e}")
            return []
    
    def has_working_orders(self, symbol: str) -> bool:
        """
        Check if there are working orders for a specific symbol.
        
        Args:
            symbol: Stock symbol to check
            
        Returns:
            True if there are working orders for the symbol
        """
        open_orders = self.get_open_orders()
        for trade in open_orders:
            if hasattr(trade, 'contract') and hasattr(trade.contract, 'symbol'):
                if trade.contract.symbol == symbol:
                    # Check if order is still working (expanded status check)
                    if hasattr(trade, 'orderStatus'):
                        status = trade.orderStatus.status
                        # More comprehensive check for working orders
                        working_statuses = ['PendingSubmit', 'Submitted', 'PreSubmitted', 'ApiPending', 'PendingCancel']
                        if status in working_statuses:
                            logger.debug(f"🔍 Found working order for {symbol}: Status={status}, OrderID={trade.order.orderId}")
                            return True
        return False
    
    def cancel_open_orders_for_symbol(self, symbol: str) -> int:
        """
        Cancel all open orders for a specific symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Number of orders cancelled
        """
        if not self.is_connected():
            logger.warning("Not connected to IB - cannot cancel orders")
            return 0
        
        cancelled_count = 0
        open_orders = self.get_open_orders()
        
        try:
            for trade in open_orders:
                if hasattr(trade, 'contract') and hasattr(trade.contract, 'symbol'):
                    if trade.contract.symbol == symbol:
                        # Check if order is still working (expanded status check)
                        if hasattr(trade, 'orderStatus'):
                            status = trade.orderStatus.status
                            working_statuses = ['PendingSubmit', 'Submitted', 'PreSubmitted', 'ApiPending', 'PendingCancel']
                            if status in working_statuses:
                                logger.warning(f"🧹 Cancelling working order for {symbol}: OrderID {trade.order.orderId}, Status={status}")
                                self.ib.cancelOrder(trade.order)
                                cancelled_count += 1
            
            if cancelled_count > 0:
                logger.warning(f"🧹 CANCELLED {cancelled_count} open orders for {symbol} to prevent Error 201")
                # Give IB time to process cancellations
                import time
                time.sleep(1.0)  # Increased wait time
                
        except Exception as e:
            logger.error(f"Error cancelling orders for {symbol}: {e}")
        
        return cancelled_count
    
    def cancel_all_open_orders(self) -> int:
        """
        Cancel ALL open orders (emergency function).
        
        Returns:
            Number of orders cancelled
        """
        if not self.is_connected():
            logger.warning("Not connected to IB - cannot cancel orders")
            return 0
        
        cancelled_count = 0
        open_orders = self.get_open_orders()
        
        try:
            for trade in open_orders:
                if hasattr(trade, 'orderStatus'):
                    status = trade.orderStatus.status
                    working_statuses = ['PendingSubmit', 'Submitted', 'PreSubmitted', 'ApiPending', 'PendingCancel']
                    if status in working_statuses:
                        symbol = trade.contract.symbol if hasattr(trade, 'contract') else 'Unknown'
                        logger.warning(f"🧹 Emergency cancelling order: {symbol} OrderID {trade.order.orderId}, Status={status}")
                        self.ib.cancelOrder(trade.order)
                        cancelled_count += 1
            
            if cancelled_count > 0:
                logger.warning(f"🚨 EMERGENCY: CANCELLED ALL {cancelled_count} open orders")
                # Give IB time to process cancellations
                import time
                time.sleep(2.0)
                
        except Exception as e:
            logger.error(f"Error in emergency cancel all orders: {e}")
        
        return cancelled_count
    
    # Event handlers
    def _on_connected(self):
        """Called when connection is established."""
        logger.info("Connection established callback")
        self._connected = True
        self._reconnect_attempts = 0
    
    def _on_disconnected(self):
        """Called when connection is lost."""
        logger.warning("Connection lost callback")
        self._connected = False
    
    def _on_error(self, reqId, errorCode, errorString, contract):
        """Called when an error occurs."""
        # Handle specific market data errors that require reconnection
        if errorCode in [2104, 2106, 2107, 320, 200, 162]:  # Market data connection errors
            logger.warning(f"Market data error detected - Code: {errorCode}, Msg: {errorString}")
            # Schedule market data reconnection
            self._schedule_market_data_reconnect()
        else:
            logger.error(f"IB Error - ReqId: {reqId}, Code: {errorCode}, Msg: {errorString}")
    
    def _schedule_market_data_reconnect(self):
        """Schedule market data reconnection after a delay."""
        import threading
        import time
        
        def delayed_reconnect():
            time.sleep(5)  # Wait 5 seconds
            if self.is_connected():
                logger.info("Attempting to refresh market data connections...")
                try:
                    # Cancel all existing market data requests and re-subscribe
                    self._refresh_market_data_subscriptions()
                except Exception as e:
                    logger.error(f"Error refreshing market data: {e}")
        
        thread = threading.Thread(target=delayed_reconnect, daemon=True)
        thread.start()
    
    def _refresh_market_data_subscriptions(self):
        """Refresh market data subscriptions to restore data flow."""
        # This will be called by FreshDataBroker to refresh stale data
        logger.info("Refreshing market data subscriptions...")
        
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current market price for a symbol with enhanced error handling.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Current price or None if unavailable
        """
        if not self.is_connected():
            logger.warning("Not connected to IB")
            return None
        
        try:
            # Try IEX first for free real-time data
            contract = Stock(symbol, "IEX", "USD")
            self.ib.qualifyContracts(contract)
            
            # Request market data snapshot
            ticker = self.ib.reqMktData(contract, snapshot=True)
            self.ib.sleep(1)  # Wait for data
            
            # Get price from ticker
            if ticker.marketPrice() and ticker.marketPrice() > 0:
                price = ticker.marketPrice()
                self.ib.cancelMktData(contract)
                return price
            
            # Fallback to SMART exchange
            contract = Stock(symbol, "SMART", "USD")
            self.ib.qualifyContracts(contract)
            
            ticker = self.ib.reqMktData(contract, snapshot=True)
            self.ib.sleep(1)
            
            if ticker.marketPrice() and ticker.marketPrice() > 0:
                price = ticker.marketPrice()
                self.ib.cancelMktData(contract)
                return price
            
            # Final fallback to historical data
            bars = self.get_historical_data(symbol, "1 D", "1 min")
            if bars and len(bars) > 0:
                return bars[-1].close
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


# Convenience function
def create_broker(config: Dict[str, Any]) -> IBBroker:
    """
    Create IBBroker instance from configuration.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Configured IBBroker instance
    """
    broker_config = config.get('broker', {})
    
    return IBBroker(
        host=broker_config.get('host', '127.0.0.1'),
        port=broker_config.get('port', 7497),
        client_id=broker_config.get('client_id', 1),
        timeout=broker_config.get('timeout', 30),
        readonly=False
    )
