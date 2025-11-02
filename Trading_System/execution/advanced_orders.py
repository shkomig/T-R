# -*- coding: utf-8 -*-
"""
Advanced Order Management System
מערכת ניהול פקודות מתקדמת

Features:
- Bracket Orders (Stop Loss + Take Profit)
- Trailing Stop Orders
- Conditional Orders
- Smart Order Routing
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

class OrderType(Enum):
    """סוגי פקודות מתקדמים"""
    BRACKET = "bracket"              # פקודה עם SL + TP
    TRAILING_STOP = "trailing_stop"  # Stop loss נודד
    CONDITIONAL = "conditional"      # פקודה מותנית
    TWAP = "twap"                   # Time Weighted Average Price
    VWAP = "vwap"                   # Volume Weighted Average Price
    ICEBERG = "iceberg"             # פקודה מוסתרת

@dataclass
class BracketOrderParams:
    """פרמטרים לפקודת Bracket"""
    entry_price: float
    stop_loss_price: float
    take_profit_price: float
    quantity: int
    trailing_stop_percent: Optional[float] = None

@dataclass
class TrailingStopParams:
    """פרמטרים ל-Trailing Stop"""
    trail_amount: float              # סכום המעקב
    trail_percent: Optional[float]   # אחוז המעקב
    aux_price: Optional[float] = None

class AdvancedOrderManager:
    """מנהל פקודות מתקדם"""
    
    def __init__(self, broker):
        self.broker = broker
        self.active_orders = {}
        self.order_history = []
        self.logger = logging.getLogger(__name__)
        
        # הגדרות ברירת מחדל
        self.default_stop_loss_pct = 0.02   # 2% stop loss
        self.default_take_profit_pct = 0.06  # 6% take profit
        self.default_trailing_pct = 0.015    # 1.5% trailing stop
    
    def place_bracket_order(self, symbol: str, action: str, quantity: int, 
                           params: Optional[BracketOrderParams] = None) -> Dict:
        """
        פקודת Bracket - קנייה/מכירה עם Stop Loss ו-Take Profit אוטומטיים
        
        Args:
            symbol: סמל המניה
            action: "BUY" או "SELL"
            quantity: כמות מניות
            params: פרמטרים מותאמים אישית
        """
        try:
            # קבלת מחיר נוכחי
            current_price = self._get_current_price(symbol)
            if not current_price:
                return {"success": False, "error": "Could not get current price"}
            
            # חישוב מחירי SL ו-TP אם לא ניתנו
            if not params:
                if action.upper() == "BUY":
                    stop_loss = current_price * (1 - self.default_stop_loss_pct)
                    take_profit = current_price * (1 + self.default_take_profit_pct)
                else:  # SELL
                    stop_loss = current_price * (1 + self.default_stop_loss_pct)
                    take_profit = current_price * (1 - self.default_take_profit_pct)
                
                params = BracketOrderParams(
                    entry_price=current_price,
                    stop_loss_price=stop_loss,
                    take_profit_price=take_profit,
                    quantity=quantity
                )
            
            # יצירת פקודות IB
            from ib_insync import LimitOrder, StopOrder
            
            # פקודת כניסה (Market או Limit)
            parent_order = LimitOrder(action, quantity, params.entry_price)
            
            # פקודת Stop Loss
            stop_action = "SELL" if action.upper() == "BUY" else "BUY"
            stop_order = StopOrder(stop_action, quantity, params.stop_loss_price)
            
            # פקודת Take Profit
            profit_order = LimitOrder(stop_action, quantity, params.take_profit_price)
            
            # שליחת הפקודות כ-Bracket
            bracket_orders = self.broker.create_bracket_order(
                parent=parent_order,
                stop_loss=stop_order,
                take_profit=profit_order
            )
            
            if bracket_orders:
                order_id = f"bracket_{symbol}_{datetime.now().strftime('%H%M%S')}"
                self.active_orders[order_id] = {
                    "type": "bracket",
                    "symbol": symbol,
                    "orders": bracket_orders,
                    "params": params,
                    "created_at": datetime.now()
                }
                
                self.logger.info(f"🎯 Bracket order placed for {symbol}: "
                               f"Entry=${params.entry_price:.2f}, "
                               f"SL=${params.stop_loss_price:.2f}, "
                               f"TP=${params.take_profit_price:.2f}")
                
                return {
                    "success": True,
                    "order_id": order_id,
                    "orders": bracket_orders,
                    "params": params
                }
            
            return {"success": False, "error": "Failed to place bracket order"}
            
        except Exception as e:
            self.logger.error(f"Error placing bracket order: {e}")
            return {"success": False, "error": str(e)}
    
    def place_trailing_stop(self, symbol: str, action: str, quantity: int,
                           trail_amount: Optional[float] = None, trail_percent: Optional[float] = None) -> Dict:
        """
        פקודת Trailing Stop - Stop Loss שעוקב אחרי המחיר
        
        Args:
            symbol: סמל המניה
            action: "BUY" או "SELL"
            quantity: כמות מניות
            trail_amount: סכום מעקב קבוע
            trail_percent: אחוז מעקב
        """
        try:
            from ib_insync import Order
            
            # שימוש בברירת מחדל אם לא ניתן
            if not trail_amount and not trail_percent:
                trail_percent = self.default_trailing_pct
            
            # יצירת פקודת Trailing Stop
            order = Order()
            order.action = action.upper()
            order.totalQuantity = quantity
            order.orderType = "TRAIL"
            
            if trail_amount:
                order.trailStopPrice = trail_amount
            elif trail_percent:
                order.trailingPercent = trail_percent * 100  # IB expects percentage
            
            # שליחת הפקודה
            result = self.broker.place_order(symbol, order)
            
            if result:
                order_id = f"trailing_{symbol}_{datetime.now().strftime('%H%M%S')}"
                self.active_orders[order_id] = {
                    "type": "trailing_stop",
                    "symbol": symbol,
                    "order": result,
                    "trail_amount": trail_amount,
                    "trail_percent": trail_percent,
                    "created_at": datetime.now()
                }
                
                trail_info = f"{trail_percent*100:.1f}%" if trail_percent else f"${trail_amount:.2f}"
                self.logger.info(f"🔄 Trailing stop placed for {symbol}: {trail_info}")
                
                return {
                    "success": True,
                    "order_id": order_id,
                    "order": result
                }
            
            return {"success": False, "error": "Failed to place trailing stop"}
            
        except Exception as e:
            self.logger.error(f"Error placing trailing stop: {e}")
            return {"success": False, "error": str(e)}
    
    def place_conditional_order(self, symbol: str, action: str, quantity: int,
                               condition_symbol: str, condition_price: float,
                               condition_operator: str = ">=") -> Dict:
        """
        פקודה מותנית - מתבצעת רק כשתנאי מסוים מתקיים
        
        Args:
            symbol: סמל המניה לקנייה/מכירה
            action: "BUY" או "SELL"
            quantity: כמות
            condition_symbol: סמל המניה לתנאי
            condition_price: מחיר התנאי
            condition_operator: ">=", "<=", "==", etc.
        """
        try:
            from ib_insync import Order, Contract
            
            # יצירת חוזה התנאי
            condition_contract = Contract()
            condition_contract.symbol = condition_symbol
            condition_contract.secType = "STK"
            condition_contract.exchange = "SMART"
            condition_contract.currency = "USD"
            
            # יצירת פקודה מותנית
            order = Order()
            order.action = action.upper()
            order.totalQuantity = quantity
            order.orderType = "MKT"  # Market order when condition is met
            
            # הוספת תנאי
            from ib_insync import PriceCondition
            condition = PriceCondition()
            condition.conId = condition_contract.conId
            condition.operator = condition_operator
            condition.price = condition_price
            
            order.conditions = [condition]
            
            # שליחת הפקודה
            result = self.broker.place_order(symbol, order)
            
            if result:
                order_id = f"conditional_{symbol}_{datetime.now().strftime('%H%M%S')}"
                self.active_orders[order_id] = {
                    "type": "conditional",
                    "symbol": symbol,
                    "order": result,
                    "condition": f"{condition_symbol} {condition_operator} {condition_price}",
                    "created_at": datetime.now()
                }
                
                self.logger.info(f"🎯 Conditional order placed: {symbol} {action} "
                               f"when {condition_symbol} {condition_operator} {condition_price}")
                
                return {
                    "success": True,
                    "order_id": order_id,
                    "order": result
                }
            
            return {"success": False, "error": "Failed to place conditional order"}
            
        except Exception as e:
            self.logger.error(f"Error placing conditional order: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_current_price(self, symbol: str) -> Optional[float]:
        """קבלת מחיר נוכחי"""
        try:
            bars = self.broker.get_historical_data(symbol, "1 D", "1 min")
            if bars and len(bars) > 0:
                return bars[-1].close
            return None
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """ביטול פקודה"""
        try:
            if order_id in self.active_orders:
                order_info = self.active_orders[order_id]
                
                # ביטול לפי סוג הפקודה
                if order_info["type"] == "bracket":
                    for order in order_info["orders"]:
                        self.broker.cancel_order(order)
                else:
                    self.broker.cancel_order(order_info["order"])
                
                # העברה להיסטוריה
                order_info["cancelled_at"] = datetime.now()
                self.order_history.append(order_info)
                del self.active_orders[order_id]
                
                self.logger.info(f"❌ Order cancelled: {order_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error cancelling order {order_id}: {e}")
            return False
    
    def get_active_orders(self) -> Dict:
        """קבלת כל הפקודות הפעילות"""
        return self.active_orders.copy()
    
    def get_order_status(self, order_id: str) -> Optional[Dict]:
        """קבלת סטטוס פקודה"""
        if order_id in self.active_orders:
            return self.active_orders[order_id]
        
        # חיפוש בהיסטוריה
        for order in self.order_history:
            if order.get("order_id") == order_id:
                return order
        
        return None


# פונקציות נוחות
def create_smart_bracket_order(broker, symbol: str, action: str, quantity: int,
                              risk_percent: float = 0.02, reward_ratio: float = 3.0):
    """
    יצירת פקודת Bracket חכמה עם יחס סיכון/תשואה
    
    Args:
        risk_percent: אחוז הסיכון (default: 2%)
        reward_ratio: יחס תשואה לסיכון (default: 3:1)
    """
    order_manager = AdvancedOrderManager(broker)
    
    # קבלת מחיר נוכחי
    current_price = order_manager._get_current_price(symbol)
    if not current_price:
        return None
    
    # חישוב מחירים
    if action.upper() == "BUY":
        stop_loss = current_price * (1 - risk_percent)
        take_profit = current_price * (1 + risk_percent * reward_ratio)
    else:
        stop_loss = current_price * (1 + risk_percent)
        take_profit = current_price * (1 - risk_percent * reward_ratio)
    
    params = BracketOrderParams(
        entry_price=current_price,
        stop_loss_price=stop_loss,
        take_profit_price=take_profit,
        quantity=quantity
    )
    
    return order_manager.place_bracket_order(symbol, action, quantity, params)


if __name__ == "__main__":
    print("🎯 Advanced Order Management System")
    print("💡 Features: Bracket Orders, Trailing Stops, Conditional Orders")
    print("💡 Import: from execution.advanced_orders import AdvancedOrderManager")