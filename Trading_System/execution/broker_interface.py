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
            logger.error(f"Error getting historical data for {symbol}: {e}")
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
        logger.error(f"IB Error - ReqId: {reqId}, Code: {errorCode}, Msg: {errorString}")
    
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
